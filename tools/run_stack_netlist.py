"""NET-02 regressions: KiCad pin graph inside the ROM-driven CPU."""
import copy
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from run_rtl import ROOT, BASE, fixtures, program_fixture, run
from make_stack_cpu import transform_bench
from build_stack_bank import convert, definitions

OUT=ROOT/"verification/net02"


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    quick="--quick" in sys.argv
    models=[ROOT/name for name in ("sim/hdl/hc_models.sv", "sim/hdl/counter_load_candidate.sv",
       "sim/net02/package_models.sv", "hardware/stack_bank/stack_bank_netlist.sv",
       "sim/net02/isa1_cpu_stack.sv", "sim/rtl/isa1_memory.sv")]
    bench_names=["tb_rtl_cpu","tb_rtl_safety","tb_stack_guards","tb_rtl_program"]
    provenance=[*models,Path(__file__),ROOT/"tools/run_rtl.py",ROOT/"tools/make_stack_cpu.py",
        ROOT/"tools/build_stack_bank.py",ROOT/"sim/net02/tb_stack_bank.sv",ROOT/"sim/net02/tb_hc273_negative.sv",
        ROOT/"hardware/stack_bank/stack_bank.kicad_sch",OUT/"stack_bank.xml",
        ROOT/"firmware/rtl01_diagnostic.asm"]
    provenance += [ROOT/"sim/tests"/(n+".sv") for n in bench_names]
    provenance += [BASE/f"control_lane{i}.bin" for i in range(4)]
    provenance += [BASE/n for n in ("cpu.py","system.py","control.py","microcode.py","sequencer.py","assembler.py")]
    report={"iteration":"NET-02","date":"2026-11-25","quick":quick,"platform":platform.platform(),
      "python":platform.python_version(),"iverilog":subprocess.run(["iverilog","-V"],capture_output=True,text=True).stdout.splitlines()[0],
      "scope":"Functional SP netlist exported from native schematic, integrated in reference ROM CPU. No timing/ERC/DRC release.",
      "sources":[{"path":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in provenance],
      "runs":[],"negative_checks":[]}
    def save():
        (OUT/"results.json").write_text(json.dumps(report,indent=2)+"\n")
    with tempfile.TemporaryDirectory(prefix="isa1-net02-") as temporary:
        work=Path(temporary)
        lanes=[(BASE/f"control_lane{i}.bin").read_bytes() for i in range(4)]
        (work/"control.hex").write_text("".join(f"{sum(lanes[l][a]<<(8*l) for l in range(4)):08x}\n" for a in range(8192)))
        rows,coverage=fixtures(quick)
        vectors="".join("".join(f"{v:08x}\n" for v in row) for row in rows)
        (work/"vectors.hex").write_text(vectors)
        report["opcode_cases"]=coverage;report["vector_sha256"]=hashlib.sha256(vectors.encode()).hexdigest()
        report["program"],frame,png=program_fixture(work)
        for name in bench_names:
            original=(ROOT/"sim/tests"/(name+".sv")).read_text()
            transformed=transform_bench(original)
            (work/(name+".sv")).write_text(transformed)
        shutil.copyfile(ROOT/"sim/net02/tb_stack_bank.sv",work/"tb_stack_bank.sv")
        configurations=[("tb_stack_bank",0),("tb_stack_bank",1),("tb_rtl_cpu",0),("tb_rtl_cpu",1),
                        ("tb_rtl_safety",0),("tb_rtl_safety",1),("tb_stack_guards",0)]
        if not quick:configurations += [("tb_rtl_program",0),("tb_rtl_program",1)]
        for bench,chip in configurations:
            command=["iverilog","-g2012","-Wall","-s",bench]
            if bench in ("tb_rtl_cpu","tb_rtl_safety","tb_rtl_program"):
                command += [f"-P{bench}.USE_HC191={chip}"]
            if bench=="tb_rtl_cpu":command += [f"-P{bench}.CASES={len(rows)}"]
            if bench=="tb_stack_bank":command += [f"-P{bench}.TIMED={chip}"]
            if bench=="tb_rtl_program":
                command += [f"-P{bench}.RETIREMENTS={report['program']['retirements']}",f"-P{bench}.BUS_COUNT={report['program']['transactions']}"]
                if chip:command += [f"-P{bench}.CPU_HALF=7",f"-P{bench}.VIDEO_HALF=5"]
            command += ["-o",str(work/"bench.vvp"),*map(str,models),str(work/(bench+".sv"))]
            row={"bench":bench,"hc191":chip,"compile":run(command,work)}
            if row["compile"]["exit"]==0:
                row["execution"]=run(["vvp",str(work/"bench.vvp")],work,timeout=360)
                if bench=="tb_rtl_program" and row["execution"]["exit"]==0:
                    matched=(work/"frame.ppm").read_bytes()==frame
                    row["frame_matches_reference"]=matched
                    if not matched:row["execution"]["exit"]=1
                    else:
                        shutil.copyfile(work/"frame.ppm",OUT/"frame.ppm")
                        (OUT/"frame.png").write_bytes(png)
            report["runs"].append(row);save();print(json.dumps(row),flush=True)
            if row["compile"]["exit"] or row.get("execution",{}).get("exit")!=0:return 1
        # Fault injection uses copies of the XML, never the production candidate.
        tree=ET.parse(OUT/"stack_bank.xml")
        for net in tree.getroot().findall("./nets/net"):
            for node in list(net.findall("node")):
                if node.get("ref")=="U7" and node.get("pin")=="6":
                    moved=copy.deepcopy(node);net.remove(node)
        ground=next(n for n in tree.getroot().findall("./nets/net") if n.get("name").removeprefix("/")=="GND")
        ground.append(moved);tree.write(work/"bad-b0.xml")
        convert(work/"bad-b0.xml",definitions(),work/"bad-stack.sv")
        bad_models=[p for p in models if p.name!="stack_bank_netlist.sv"]+[work/"bad-stack.sv"]
        compiled=run(["iverilog","-g2012","-Wall","-s","tb_stack_bank","-o",str(work/"bad.vvp"),*map(str,bad_models),str(work/"tb_stack_bank.sv")],work)
        executed=run(["vvp",str(work/"bad.vvp")],work) if compiled["exit"]==0 else None
        passed=executed is not None and executed["exit"]!=0 and "stack arithmetic mismatch" in executed["stdout"]
        report["negative_checks"].append({"case":"B0 first adder tied to GND instead of VCC","expected_rejection":True,
            "passed":passed,"compile":compiled,"execution":executed})
        tree=ET.parse(OUT/"stack_bank.xml")
        for net in tree.getroot().findall("./nets/net"):
            for node in list(net.findall("node")):
                if node.get("ref")=="U1" and node.get("pin")=="3":net.remove(node)
        tree.write(work/"floating.xml")
        try:convert(work/"floating.xml",definitions(),work/"floating.sv")
        except ValueError as error:
            message=str(error);passed_floating="Floating input U1/3" in message
        else:message="No rejection";passed_floating=False
        report["negative_checks"].append({"case":"Floating register D0","expected_rejection":True,"passed":passed_floating,"message":message})
        expected=["data setup", "clear recovery", "clear pulse", "clock pulse"]
        for case,message in enumerate(expected):
            compiled=run(["iverilog","-g2012","-Wall","-s","tb_hc273_negative",f"-Ptb_hc273_negative.CASE={case}",
                "-o",str(work/"negative.vvp"),str(ROOT/"sim/net02/package_models.sv"),str(ROOT/"sim/net02/tb_hc273_negative.sv")],work)
            executed=run(["vvp",str(work/"negative.vvp")],work) if compiled["exit"]==0 else None
            passed_timing=executed is not None and executed["exit"]!=0 and f"HC273 {message} violation" in executed["stdout"]
            report["negative_checks"].append({"case":"HC273 "+message,"expected_rejection":True,"passed":passed_timing,
                                             "compile":compiled,"execution":executed})
        save();print(json.dumps({"negative_checks":report["negative_checks"]}),flush=True)
        return int(not all(r["passed"] for r in report["negative_checks"]))


if __name__=="__main__":raise SystemExit(main())
