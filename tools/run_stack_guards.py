"""Exhaust ideal SP interval checks without modifying recovered sources."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import ROOT, BASE, OUT, run


def main():
    names = ["sim/hdl/hc_models.sv", "sim/hdl/counter_load_candidate.sv",
             "sim/rtl/isa1_cpu.sv", "sim/tests/tb_stack_guards.sv"]
    sources = [ROOT/name for name in names]
    report = {"date": "2026-11-24", "scope": "Ideal first-stack-microinstruction bounds, all 16-bit SP values, boot on/off, CALL/RET/PUSH/POP",
              "sources": [{"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in [*sources, Path(__file__), ROOT/"tools/run_rtl.py"]]}
    with tempfile.TemporaryDirectory(prefix="isa1-stack-bounds-") as temporary:
        work = Path(temporary)
        lanes = [(BASE/f"control_lane{i}.bin").read_bytes() for i in range(4)]
        (work/"control.hex").write_text("".join(f"{sum(lanes[l][a]<<(8*l) for l in range(4)):08x}\n" for a in range(8192)))
        report["compile"] = run(["iverilog", "-g2012", "-Wall", "-s", "tb_stack_guards", "-o", str(work/"stack.vvp"), *map(str,sources)], work)
        if report["compile"]["exit"] == 0:
            report["execution"] = run(["vvp",str(work/"stack.vvp")],work)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"stack-guards.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report),flush=True)
    return int(report["compile"]["exit"]!=0 or report.get("execution",{}).get("exit")!=0)


if __name__ == "__main__":
    raise SystemExit(main())
