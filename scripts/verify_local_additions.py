"""Re-run existing standalone benches in temporary copies."""
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    results = []
    for revision in ("74", "75"):
        source = ROOT / f"isa1_rev{revision}.py"
        original_result = ROOT / f"isa1_rev{revision}_results.json"
        with tempfile.TemporaryDirectory(prefix="isa1-additional-") as folder:
            work = Path(folder)
            shutil.copyfile(source, work / source.name)
            run = subprocess.run([sys.executable, source.name], cwd=work,
                                 capture_output=True, text=True, timeout=120)
            generated = work / original_result.name
            identical = (generated.exists() and
                         json.loads(generated.read_text()) ==
                         json.loads(original_result.read_text()))
            results.append(dict(source=source.name, exit_code=run.returncode,
                                stdout=run.stdout, stderr=run.stderr,
                                matches_original_result=identical))
    report = dict(date="2026-11-24", python=platform.python_version(),
                  scope="Existing abstract Python models, not electrical validation",
                  results=results)
    (ROOT / "verification/local-additions.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return int(any(r["exit_code"] != 0 or not r["matches_original_result"] for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
