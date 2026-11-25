"""Run recovered benches in disposable copies, without changing the archive."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verification"


def main():
    OUT.mkdir(exist_ok=True)
    results = []
    for revision in sorted((ROOT / "revisions").iterdir()):
        if not revision.is_dir():
            continue
        benches = sorted({p.name for p in revision.glob("test*.py")})
        benches += [n for n in ("validation.py", "keyboard.py", "alu_gates.py",
                                "datapath_blocks.py", "counter.py")
                    if (revision / n).is_file()]
        for bench in benches:
            with tempfile.TemporaryDirectory(prefix="isa1-check-") as tmp:
                work = Path(tmp) / "source"
                shutil.copytree(revision, work)
                env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
                try:
                    run = subprocess.run([sys.executable, bench], cwd=work, env=env,
                                         capture_output=True, text=True, timeout=120)
                    row = dict(revision=revision.name, bench=bench,
                               exit_code=run.returncode,
                               status="passed" if run.returncode == 0 else "failed",
                               stdout=run.stdout, stderr=run.stderr)
                except subprocess.TimeoutExpired as exc:
                    row = dict(revision=revision.name, bench=bench, status="timeout",
                               stdout=str(exc.stdout or ""), stderr=str(exc.stderr or ""))
                results.append(row)
                print(f"{revision.name}/{bench}: {row['status']}", flush=True)
    roms = []
    latest = ROOT / "revisions" / "rev983"
    with tempfile.TemporaryDirectory(prefix="isa1-rom-") as tmp:
        work = Path(tmp) / "source"
        shutil.copytree(latest, work)
        for existing in work.glob("control_lane*.bin"):
            existing.unlink()
        run = subprocess.run([sys.executable, "sequencer.py"], cwd=work,
                             capture_output=True, text=True)
        for original in sorted(latest.glob("control_lane*.bin")):
            generated = work / original.name
            roms.append(dict(path=original.relative_to(ROOT).as_posix(),
                             generator_exit_code=run.returncode,
                             identical=generated.exists() and original.read_bytes() == generated.read_bytes(),
                             sha256=hashlib.sha256(original.read_bytes()).hexdigest()))
    report = dict(python=platform.python_version(), date="2026-11-24",
                  note="Logical simulation only; recovered source snapshots unchanged.",
                  benches=results, rom_regeneration=roms)
    (OUT / "results.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    passed = sum(r["status"] == "passed" for r in results)
    print(f"{passed}/{len(results)} benches passed; ROM matches: {sum(r['identical'] for r in roms)}/{len(roms)}")
    return 0 if passed == len(results) and all(r["identical"] for r in roms) else 1


if __name__ == "__main__":
    raise SystemExit(main())
