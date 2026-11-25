"""Run RTL-01 under Ubuntu WSL; all build/vector files live in Linux /tmp."""
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import shutil
import subprocess
import sys
import tempfile
import time
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verification/rtl01"
BASE = ROOT / "revisions/rev983"
sys.dont_write_bytecode = True
sys.path.insert(0, str(BASE))
from cpu import CPU
from system import Machine
from control import FIELDS, FETCH, TABLE, unpack
from assembler import assemble


class Reference(Machine):
    def __init__(self):
        super().__init__()
        self.trace = []

    def micro(self, delay=0):
        self.current_opcode = self.read(self.pc)
        self.stack_operations = 0
        yield from CPU.micro(self, delay)

    def push(self, value, delay):
        if self.current_opcode == 0x50 and not self.stack_operations:
            lower = 0x4000 if self.boot else 0
            if not lower+2 <= self.sp <= 0x8000:
                raise ValueError("stack overflow")
        self.stack_operations += 1
        yield from CPU.push(self, value, delay)

    def pop(self, delay):
        if self.current_opcode == 0x51 and not self.stack_operations:
            lower = 0x4000 if self.boot else 0
            if not lower <= self.sp <= 0x7ffe:
                raise ValueError("stack underflow")
        self.stack_operations += 1
        return (yield from CPU.pop(self, delay))

    def bus(self, address, data=None, delay=0):
        generator = CPU.bus(self, address, data, delay)
        while True:
            try:
                event = next(generator)
            except StopIteration as completed:
                return completed.value
            if event[0] == "COMMIT":
                self.trace.append((address, 0 if data is None else 256 | data,
                                   self.read(address) if data is None else 0))
            yield event


def fixtures(quick=False):
    rng = random.Random(98501)
    rows, coverage = [], {}
    valid = set(TABLE)
    sp_edges = [0, 1, 2, 0x3fff, 0x4000, 0x4001, 0x4002,
                0x7ffe, 0x7fff, 0x8000, 0x8001, 0xffff]
    targets = [0, 0x3fff, 0x4000, 0x5000, 0x7fff, 0x8000,
               0x9fff, 0xa000, 0xa001, 0xa002, 0xa010, 0xa011, 0xa012, 0xbfff, 0xc000, 0xffff]
    patterns = [bytes((p*17+(p>>8)+salt)&255 for p in range(32768)) for salt in (49, 93, 167)]
    for op in range(256):
        coverage[f"{op:02x}"] = 0
        for sample in range((32 if quick else 256) if op in valid else 1):
            m = Reference()
            m.ram[:], m.vram[:], m.rom[:] = patterns
            m.pc = 0x4000
            m.sp = sp_edges[sample % len(sp_edges)] if sample < 48 else 0x7ffc
            m.a, m.b = rng.randrange(256), rng.randrange(256)
            m.x = targets[sample % len(targets)] if sample < 64 else rng.randrange(65536)
            m.z, m.c = (sample >> 1) & 1, sample & 1
            m.boot, m.vb, m.eb, m.row = bool((sample // 12) % 2), sample % 4, sample % 2, sample % 4
            target = targets[sample % len(targets)] if sample < 64 else rng.randrange(65536)
            lo, hi = target & 255, target >> 8
            stack_lo, stack_hi = rng.randrange(256), rng.randrange(256)
            if m.sp < 0x8000:
                m.ram[m.sp] = stack_lo
                if m.sp + 1 < 0x8000:
                    m.ram[m.sp + 1] = stack_hi
            m.ram[0x4000:0x4003] = bytes((op, lo, hi))
            initial = [m.pc, m.sp, m.a, m.b, m.x, m.z, m.c,
                       int(m.boot), m.vb, m.eb, m.row, op, lo, hi,
                       sample % 11, stack_lo, stack_hi]
            fault = 0
            try:
                m.step()
            except ValueError as error:
                if str(error) == "stack overflow": fault = 1
                elif str(error) == "stack underflow": fault = 2
                elif str(error).startswith("unknown opcode"): fault = 3
                else: raise
                m.halt = True
            if fault and op in (0x50, 0x51):
                # Atomic bounds rejection: fetches are allowed, stack effects are not.
                assert m.sp == initial[1]
                assert len(m.trace) == (3 if op == 0x50 else 1)
            expected = [m.pc, m.sp, m.a, m.b, m.x, m.z, m.c, int(m.halt),
                        fault, int(m.boot), m.vb, m.eb, m.row, len(m.trace), 0]
            row = initial + expected
            assert len(row) == 32 and len(m.trace) <= 8
            for transaction in m.trace:
                row.extend(transaction)
            rows.append(row + [0] * (64 - len(row)))
            coverage[f"{op:02x}"] += 1
    return rows, coverage


def run(command, cwd, timeout=240):
    started = time.monotonic()
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return {"command": [str(p) for p in command], "exit": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr,
            "seconds": round(time.monotonic()-started, 3)}


def program_fixture(work):
    source = (ROOT/"firmware/rtl01_diagnostic.asm").read_text()
    code = assemble(source, 0x4000)
    loader = []
    for address, byte in enumerate(code, 0x4000):
        loader += [f"LDA #{byte}", f"STA {address}"]
    loader += ["LDA #1", "STA A002H", "JMP 4000H"]
    m = Reference()
    m.rom[:3] = bytes.fromhex("40 40 c0")
    boot_code = assemble("\n".join(loader), 0xc040)
    assert len(boot_code) + 0x40 < 0x4000
    m.rom[0x40:0x40+len(boot_code)] = boot_code
    m.rom[0x4020] = 123
    image = bytes(m.rom)
    m.keys = {(0, 0), (0, 1), (1, 0)}
    retirements = []
    opcodes = set()
    for _ in range(200000):
        op = m.read(m.pc)
        opcodes.add(op)
        m.step()
        state = [(op, 8), (m.pc, 16), (m.sp, 16), (m.x, 16),
                 (m.a, 8), (m.b, 8), (m.z, 1), (m.c, 1), (int(m.halt), 1),
                 (0, 2), (int(m.boot), 1), (m.vb, 2), (m.eb, 1), (m.row, 2)]
        packed = 0
        for value, width in state: packed = (packed << width) | value
        retirements.append(packed)
        if m.halt: break
    else: raise AssertionError("Reference program timeout")
    assert m.ram[0x5ff0] == 165, "New diagnostic failed in reference"
    assert bytes(m.vram) == bytes(range(256))*128
    assert opcodes == set(TABLE), (opcodes, set(TABLE))
    (work/"rom_image.hex").write_text("".join(f"{b:02x}\n" for b in image))
    (work/"program_state.hex").write_text("".join(f"{s:021x}\n" for s in retirements))
    (work/"program_bus.hex").write_text("".join(
        f"{(addr<<17) | (int(bool(wr&256))<<16) | ((wr&255)<<8) | rd:09x}\n"
        for addr, wr, rd in m.trace))
    pixels = bytearray()
    for y in range(480):
        for x in range(160):
            p = m.vram[(y//4)*256+x]
            pixels += bytes((((p>>5)&7)*255//7, ((p>>2)&7)*255//7, (p&3)*255//3))
    expected_frame = b"P6\n160 480\n255\n" + pixels
    # Minimal PNG encoder: direct rendering of emulated framebuffer data.
    def chunk(kind, data):
        return struct.pack(">I", len(data))+kind+data+struct.pack(">I", zlib.crc32(kind+data)&0xffffffff)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB",160,480,8,2,0,0,0))
    png += chunk(b"IDAT",zlib.compress(b"".join(b"\x00"+pixels[y*480:(y+1)*480] for y in range(480))))+chunk(b"IEND",b"")
    return {"retirements": len(retirements), "transactions": len(m.trace),
            "opcodes": sorted(opcodes), "assembled_bytes": len(code),
            "firmware_sha256": hashlib.sha256(code).hexdigest(),
            "boot_image_sha256": hashlib.sha256(image).hexdigest()}, expected_frame, png


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    quick = "--quick" in sys.argv
    lanes = [(BASE / f"control_lane{i}.bin").read_bytes() for i in range(4)]
    assert all(len(lane) == 8192 for lane in lanes)
    words = [sum(lanes[l][a] << (8*l) for l in range(4)) for a in range(8192)]
    # Verify that the committed binary lanes, rather than a newly generated
    # replacement, contain the control contract interpreted by this RTL.
    for seq in [FETCH, *TABLE.values()]:
        for w in seq:
            q = unpack(w)
            if q["mem"] != "-":
                assert all(q[f] == "-" for f in ("dst", "pc", "sp", "x", "alu", "flags", "end", "halt"))
    from sequencer import ROM
    assert words == ROM
    rows, coverage = fixtures(quick)
    models = [ROOT/"sim/hdl/hc_models.sv", ROOT/"sim/hdl/counter_load_candidate.sv",
              ROOT / "sim/rtl/isa1_cpu.sv", ROOT / "sim/rtl/isa1_memory.sv"]
    benches = ["tb_rtl_cpu", "tb_rtl_safety", "tb_rtl_alu", "tb_rtl_program"]
    sources = models + [ROOT / "sim/tests" / (name+".sv") for name in benches]
    provenance = sources + [Path(__file__), ROOT/"firmware/rtl01_diagnostic.asm", *[BASE/f"control_lane{i}.bin" for i in range(4)],
                           *[BASE/f for f in ("cpu.py", "system.py", "control.py", "microcode.py", "sequencer.py", "assembler.py")]]
    report = {"iteration": "RTL-01", "date": "2026-11-24", "quick": quick,
              "platform": platform.platform(), "python": platform.python_version(),
              "iverilog": subprocess.run(["iverilog", "-V"], capture_output=True, text=True).stdout.splitlines()[0],
              "scope": "ROM-driven RTL versus architectural Python; not IC netlist/electrical validation",
              "sources": [{"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in provenance], "opcode_cases": coverage, "runs": []}
    with tempfile.TemporaryDirectory(prefix="isa1-rtl01-") as temporary:
        work = Path(temporary)
        (work/"control.hex").write_text("".join(f"{w:08x}\n" for w in words))
        vectors = "".join("".join(f"{w:08x}\n" for w in row) for row in rows)
        (work/"vectors.hex").write_text(vectors)
        report["vector_sha256"] = hashlib.sha256(vectors.encode()).hexdigest()
        report["program"], expected_frame, png = program_fixture(work)
        configurations = [(bench, chip) for bench in benches for chip in
                          ((0,) if bench == "tb_rtl_alu" else (0, 1))]
        for bench, chip in configurations:
            command = ["iverilog", "-g2012", "-Wall", "-s", bench]
            if bench != "tb_rtl_alu": command += [f"-P{bench}.USE_HC191={chip}"]
            if bench == "tb_rtl_cpu": command += [f"-Ptb_rtl_cpu.CASES={len(rows)}"]
            if bench == "tb_rtl_program":
                command += [f"-Ptb_rtl_program.RETIREMENTS={report['program']['retirements']}",
                            f"-Ptb_rtl_program.BUS_COUNT={report['program']['transactions']}"]
                if chip: command += ["-Ptb_rtl_program.CPU_HALF=7", "-Ptb_rtl_program.VIDEO_HALF=5"]
            command += ["-o", str(work/(bench+".vvp")), *map(str, models), str(ROOT/"sim/tests"/(bench+".sv"))]
            compiled = run(command, work)
            report["runs"].append(compiled)
            if compiled["exit"] == 0:
                report["runs"].append(run(["vvp", str(work/(bench+".vvp"))], work))
                if bench == "tb_rtl_program" and report["runs"][-1]["exit"] == 0:
                    matched = (work/"frame.ppm").read_bytes() == expected_frame
                    report["runs"][-1]["frame_matches_reference"] = matched
                    if not matched: report["runs"][-1]["exit"] = 1
            print(json.dumps({"bench": bench, "hc191": chip, "result": report["runs"][-1]}), flush=True)
            (OUT/"results.json").write_text(json.dumps(report, indent=2)+"\n")
            if report["runs"][-1]["exit"]: break
        frame = work/"frame.ppm"
        report["program"]["frame_matches_reference"] = frame.exists() and frame.read_bytes() == expected_frame
        if report["program"]["frame_matches_reference"]:
            shutil.copyfile(frame, OUT/"frame.ppm")
            (OUT/"frame.png").write_bytes(png)
            report["program"]["frame_sha256"] = hashlib.sha256(frame.read_bytes()).hexdigest()
    (OUT/"results.json").write_text(json.dumps(report, indent=2)+"\n")
    return int(len(report["runs"]) != 2*len(configurations) or any(r["exit"] for r in report["runs"])
               or not report["program"]["frame_matches_reference"])


if __name__ == "__main__":
    raise SystemExit(main())
