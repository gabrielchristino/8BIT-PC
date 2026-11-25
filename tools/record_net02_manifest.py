"""Verify NET-02 tested sources and preserve provenance of the new artifacts."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"verification/net02"
MANIFEST=OUT/"manifest.json"
BASE="6bbac525a4435f87566ccb723e733134e21d3e43"


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report=json.loads((OUT/"results.json").read_text())
    failures=[]
    for item in report["sources"]:
        if digest(ROOT/item["path"])!=item["sha256"]:failures.append("Tested source changed: "+item["path"])
    if report["quick"] or len(report["runs"])!=9:failures.append("Full regression not recorded")
    for row in report["runs"]:
        if row["compile"]["exit"] or row.get("execution",{}).get("exit")!=0:failures.append("Bench failed: "+row["bench"])
        if row["bench"]=="tb_rtl_program" and not row.get("frame_matches_reference"):failures.append("Frame not compared")
    if len(report["negative_checks"])!=6 or not all(r["passed"] for r in report["negative_checks"]):failures.append("Negative checks not approved")
    schematic=json.loads((OUT/"schematic-check.json").read_text())
    if schematic["failures"] or schematic["pins"]!=220 or schematic["components"]!=24:failures.append("Schematic comparison not approved")
    if "--check" in sys.argv:
        manifest=json.loads(MANIFEST.read_text())
        for item in manifest["files"]:
            path=(ROOT/item["path"]).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or digest(path)!=item["sha256"]:failures.append(item["path"])
        print(json.dumps({"checked":len(manifest["files"]),"failures":failures}))
        return int(bool(failures))
    # Earlier manifests include mutable overview documents. Audit their exact
    # Git snapshots, not the newer overview wording in this working tree.
    baseline=[]
    for name in ("verification/rev9842/manifest.json","verification/rtl01/manifest.json"):
        data=subprocess.check_output(["git","show",BASE+":"+name],cwd=ROOT)
        old=json.loads(data)
        errors=[]
        for item in old["files"]:
            blob=subprocess.check_output(["git","show",BASE+":"+item["path"]],cwd=ROOT)
            if hashlib.sha256(blob).hexdigest()!=item["sha256"]:errors.append(item["path"])
        baseline.append({"git_commit":BASE,"manifest":name,"checked":len(old["files"]),"failures":errors})
        failures.extend(errors)
    (OUT/"baseline-integrity.json").write_text(json.dumps(baseline,indent=2)+"\n")
    if failures:
        print(json.dumps({"failures":failures}));return 1
    files=set()
    for name in ("hardware/stack_bank","sim/net02","verification/net02"):
        files.update(p for p in (ROOT/name).rglob("*") if p.is_file() and p!=MANIFEST and "__pycache__" not in p.parts)
    files.update(ROOT/name for name in ("tools/build_stack_bank.py","tools/make_stack_cpu.py","tools/run_stack_netlist.py",
         "tools/record_net02_manifest.py","docs/engineering/NET02.md","AGENTS.md","README.md","ROADMAP.md",
         "DECISIONS.md","CHANGELOG.md","PROVENANCE.md"))
    files.update(ROOT/"references/ti"/name for name in ("cd74hc283.pdf","sn74hc273.pdf","sn74hc04.pdf","sn74hc125.pdf"))
    rows=[]
    for path in sorted(files):
        relative=path.relative_to(ROOT).as_posix()
        origin="New NET-02 design/verification, 2026-11-25"
        row={"path":relative,"bytes":path.stat().st_size,"sha256":digest(path),"origin":origin}
        if relative.startswith("references/ti/"):
            if not path.read_bytes().startswith(b"%PDF-"):raise ValueError("Invalid PDF "+relative)
            row["origin"]="Texas Instruments official datasheet";row["url"]="https://www.ti.com/lit/ds/symlink/"+path.name
        rows.append(row)
    MANIFEST.write_text(json.dumps({"iteration":"NET-02","date":"2026-11-25","base_git_commit":BASE,
       "transformation":"Explicit package pin schema -> native KiCad -> KiCad XML -> pin-connected HDL -> ROM CPU adapter",
       "scope":"SP bank only; no complete electrical/production release","files":rows},indent=2)+"\n")
    print(json.dumps({"recorded":len(rows),"failures":[]}))
    return 0


if __name__=="__main__":raise SystemExit(main())
