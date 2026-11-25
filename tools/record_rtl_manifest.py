"""Provenance manifest for RTL-01, independent of the 9.8.4.2 snapshot."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"verification/rtl01"
MANIFEST = OUT/"manifest.json"


def main():
    results = json.loads((OUT/"results.json").read_text())
    failures = []
    for item in results["sources"]:
        path = ROOT/item["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            failures.append("Source differs from tested version: "+item["path"])
    if results["quick"] or len(results["runs"]) != 14 or any(r["exit"] for r in results["runs"]):
        failures.append("Full seven-configuration regression not approved")
    if not results["program"].get("frame_matches_reference"):
        failures.append("Frame comparison missing/failed")
    guards = json.loads((OUT/"stack-guards.json").read_text())
    if guards["compile"]["exit"] or guards.get("execution",{}).get("exit") != 0:
        failures.append("Stack guard exhaustive bench not approved")
    for item in guards["sources"]:
        if hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest()!=item["sha256"]:
            failures.append("Stack guard tested source differs: "+item["path"])
    if "--check" in sys.argv:
        report = json.loads(MANIFEST.read_text())
        for item in report["files"]:
            path = (ROOT/item["path"]).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file():
                failures.append(item["path"])
            elif hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                failures.append(item["path"])
        print(json.dumps({"checked": len(report["files"]), "failures": failures}))
        return int(bool(failures))
    if failures:
        print(json.dumps({"failures": failures}))
        return 1
    paths = set()
    for name in ("sim/rtl", "sim/tests", "firmware", "verification/rtl01"):
        paths.update(p for p in (ROOT/name).rglob("*") if p.is_file() and p!=MANIFEST and "__pycache__" not in p.parts)
    paths.update(ROOT/name for name in ("tools/run_rtl.py", "tools/render_rtl_frame.py", "tools/run_stack_guards.py",
                 "tools/record_rtl_manifest.py", "docs/engineering/RTL01.md",
                 "AGENTS.md", "README.md", "ROADMAP.md", "DECISIONS.md", "PROVENANCE.md", "CHANGELOG.md"))
    rows = []
    for path in sorted(paths):
        data = path.read_bytes()
        rows.append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(data),
                     "sha256": hashlib.sha256(data).hexdigest(),
                     "origin": "New RTL-01 integration, 2026-11-24 to 2026-11-25; historical dependencies identified in results.json"})
    MANIFEST.write_text(json.dumps({"iteration": "RTL-01", "date": "2026-11-24",
        "continuation_date_client": "2026-11-25",
        "base_git_commit": "29c37359881a386644b8dcfbf4ccdd967edd159c",
        "transformation": "Original binary control lanes drive new RTL; architectural model supplies comparisons; frame rendered from verified HDL output",
        "files": rows}, indent=2)+"\n")
    print(json.dumps({"recorded": len(rows), "failures": []}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
