"""Run with Ubuntu/WSL: python3 tools/run_rev9842.py."""
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "verification/rev9842"


def run(command, cwd):
    return subprocess.run(command, cwd=cwd, capture_output=True,
                          text=True, timeout=180)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for tool in ("iverilog", "vvp"):
        if not shutil.which(tool):
            raise SystemExit(f"Missing tool: {tool}")
    sources = [ROOT / "sim/hdl" / name for name in
               ("hc_models.sv", "counter_load_candidate.sv", "tb_counter_load.sv")]
    report = {"date": "2026-11-24", "platform": platform.platform(),
              "python": platform.python_version(),
              "iverilog": run(["iverilog", "-V"], ROOT).stdout.splitlines()[0],
              "sources": [{"path": p.relative_to(ROOT).as_posix(),
                           "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in sources], "runs": []}
    if "--checks-only" in sys.argv:
        report = json.loads((OUTPUT / "results.json").read_text())
        for source in report["sources"]:
            if hashlib.sha256((ROOT/source["path"]).read_bytes()).hexdigest() != source["sha256"]:
                raise SystemExit("Source changed: rerun the complete bench")
    for timed in (() if "--checks-only" in sys.argv else (0, 1)):
        with tempfile.TemporaryDirectory(prefix="isa1-rev9842-") as temporary:
            binary = Path(temporary) / "counter.vvp"
            compile_command = ["iverilog", "-g2012", "-Wall", "-s", "tb_counter_load",
                               f"-Ptb_counter_load.TIMED={timed}", "-o", str(binary),
                               *map(str, sources)]
            compiled = run(compile_command, temporary)
            executed = run(["vvp", str(binary)], temporary) if compiled.returncode == 0 else None
            row = {"timed": timed, "compile_exit": compiled.returncode,
                   "compile_stdout": compiled.stdout, "compile_stderr": compiled.stderr,
                   "run_exit": executed.returncode if executed else None,
                   "stdout": executed.stdout if executed else "",
                   "stderr": executed.stderr if executed else ""}
            if executed and executed.returncode == 0:
                row["counts"] = {k: int(v) for k, v in
                                 re.findall(r"(\w+)=(\d+)", executed.stdout)}
            report["runs"].append(row)
            (OUTPUT / "results.json").write_text(json.dumps(report, indent=2) + "\n")
            print(json.dumps(row), flush=True)
    report["additional_checks"] = []
    expected = ["LOAD pulse violation", "data setup before LOAD release violation",
                "LOAD recovery violation", "count setup violation",
                "data hold after LOAD violation", "CTEN hold violation",
                "direction hold violation"]
    for case in [-1, *range(len(expected))]:
        bench = "tb_hc191_unit" if case == -1 else "tb_hc191_negative"
        with tempfile.TemporaryDirectory(prefix="isa1-chip-check-") as temporary:
            binary = Path(temporary) / "chip.vvp"
            command = ["iverilog", "-g2012", "-Wall", "-s", bench]
            if case >= 0:
                command += [f"-P{bench}.CASE={case}"]
            command += ["-o", str(binary), str(sources[0]),
                        str(ROOT / "sim/hdl" / (bench + ".sv"))]
            compiled = run(command, temporary)
            executed = run(["vvp", str(binary)], temporary) if compiled.returncode == 0 else None
            output = executed.stdout + executed.stderr if executed else compiled.stderr
            passed = compiled.returncode == 0 and executed is not None and (
                (executed.returncode == 0 and "failures=0" in output) if case == -1 else
                (executed.returncode != 0 and expected[case] in output))
            report["additional_checks"].append({"bench": bench, "case": case,
                "expected_failure": case >= 0, "passed": passed,
                "compile_exit": compiled.returncode,
                "run_exit": executed.returncode if executed else None, "output": output})
    for filename in ("tb_hc191_unit.sv", "tb_hc191_negative.sv"):
        source = ROOT / "sim/hdl" / filename
        item = {"path": source.relative_to(ROOT).as_posix(),
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
        report["sources"] = [s for s in report["sources"] if s["path"] != item["path"]] + [item]
    (OUTPUT / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"additional_checks": report["additional_checks"]}), flush=True)
    ok = all(r["compile_exit"] == 0 and r["run_exit"] == 0
             and r.get("counts", {}).get("failures") == 0 for r in report["runs"])
    ok = ok and all(r["passed"] for r in report["additional_checks"])
    return int(not ok)


if __name__ == "__main__":
    raise SystemExit(main())
