"""NET-09 tested-source/provenance audit; prior snapshots stay immutable."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"verification/net09"
MANIFEST=OUT/"manifest.json"
BASE="4f2584e7e3d07b0872ecb62eae694eae13a7fd4c"


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    failures=[]
    report=json.loads((OUT/"results.json").read_text())
    phase=json.loads((OUT/"negative.json").read_text())
    for collection in (report,phase):
        for item in collection["sources"]:
            if digest(ROOT/item["path"])!=item["sha256"]:failures.append("Tested source changed: "+item["path"])
        for row in collection.get("runs",[]):
            if row["compile"]["exit"] or row.get("execution",{}).get("exit")!=0:failures.append("Failed execution")
    if report['quick'] or len(report['runs'])!=9:failures.append('Full configuration set absent')
    units=[r for r in report['runs'] if r['bench']=='tb_x_register_bank']
    if len(units)!=2 or not all('x_cases=524288 failures=0' in row['execution']['stdout'] for row in units):failures.append('X coverage absent')
    if len(phase['checks'])!=2 or not all(x['passed'] for x in phase['checks']):failures.append('Negative checks absent/failed')
    glue=json.loads((OUT/'execution-glue-check.json').read_text())
    if glue['failures'] or glue['max_signal_input_loads']>4:failures.append('Glue schematic failed')
    programs=[r for r in report["runs"] if r["bench"]=="tb_rtl_program"]
    if len(programs)!=2 or not all(r.get("frame_matches_reference") for r in programs):failures.append("Frame comparison absent/failed")
    schematic=json.loads((OUT/"schematic-check.json").read_text())
    if schematic["failures"] or schematic["components"]!=36 or schematic["pins"]!=324 or schematic["no_connects"]!=9 or schematic["max_signal_input_loads"]>4:failures.append("Schematic/load check failed")
    if "--check" in sys.argv:
        manifest=json.loads(MANIFEST.read_text())
        for item in manifest["files"]:
            path=(ROOT/item["path"]).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or digest(path)!=item["sha256"]:failures.append(item["path"])
        print(json.dumps({"checked":len(manifest["files"]),"failures":failures}));return int(bool(failures))
    baseline=[]
    for commit,name in [("29c37359881a386644b8dcfbf4ccdd967edd159c","verification/rev9842/manifest.json"),
                        ("6bbac525a4435f87566ccb723e733134e21d3e43","verification/rtl01/manifest.json"),
                        ("60c097c8d5fb6a8f282fa6429347431c9f313ac8","verification/net02/manifest.json"),
                        ("b5e46593fab55b8679254f9004e5711cd1ffa2c5","verification/net03/manifest.json"),
                        ("179b06ed6aa80ab1658022657638ef571888d6a7","verification/net04/manifest.json"),
                        ("18a3cdc2ab83cb8af51177b8116b0320a4a4f5b8","verification/net05/manifest.json"),
                        ("d876dc6499c49b937c2dfd318abe605eea0497e3","verification/net06/manifest.json"),
                        ("50a923cd3d60bb4943030934140d8336be4ddf42","verification/net07/manifest.json"),
                        (BASE,"verification/net08/manifest.json")]:
        old=json.loads(subprocess.check_output(["git","show",commit+":"+name],cwd=ROOT));errors=[]
        for item in old["files"]:
            data=subprocess.check_output(["git","show",commit+":"+item["path"]],cwd=ROOT)
            if hashlib.sha256(data).hexdigest()!=item["sha256"]:errors.append(item["path"])
        baseline.append({"git_commit":commit,"manifest":name,"checked":len(old["files"]),"failures":errors});failures+=errors
    (OUT/"baseline-integrity.json").write_text(json.dumps(baseline,indent=2)+"\n")
    if failures:print(json.dumps({"failures":failures}));return 1
    files=set()
    for directory in ("hardware/x_register_bank","hardware/cpu_execution_glue","sim/net09","verification/net09"):
        files.update(p for p in (ROOT/directory).rglob("*") if p.is_file() and p!=MANIFEST and "__pycache__" not in p.parts)
    files.update(ROOT/n for n in ("tools/build_cpu_execution_glue.py","tools/build_x_register_bank.py","tools/make_x_register_cpu.py","tools/run_x_register_netlist.py",
      "tools/run_x_register_negative.py","tools/record_net09_manifest.py","docs/engineering/NET09.md","AGENTS.md","README.md","ROADMAP.md","DECISIONS.md","PROVENANCE.md","CHANGELOG.md","docs/engineering/KEYPAD_CONNECTOR.md","docs/engineering/PRODUCTION_GATES.md"))
    files.update(ROOT/"references/ti"/n for n in ("sn74hc273.pdf","cd74hc283.pdf","sn74hc157.pdf","sn74hc08.pdf","sn74hc32.pdf","sn74hc04.pdf","sn74hc125.pdf"))
    rows=[]
    for path in sorted(files):
        relative=path.relative_to(ROOT).as_posix()
        row={"path":relative,"bytes":path.stat().st_size,"sha256":digest(path),"origin":"NET-09 design/verification, 2026-11-25"}
        if relative.startswith("references/ti/"):
            if not path.read_bytes().startswith(b"%PDF-"):raise ValueError("Invalid PDF "+relative)
            row["origin"]="Texas Instruments official datasheet; existing or newly retrieved, original bytes retained"
            row["url"]="https://www.ti.com/lit/ds/symlink/"+path.name
        if relative.startswith('references/user/'):
            row['origin']='User-supplied keypad images; filenames changed only, original bytes and credit retained; see adjacent source manifest'
        if path.name=='baseline-before-pin-glue.json':
            row['origin']='NET-09 earlier accepted trial before explicit glue; hashes identify that trial, not final acceptance'
        rows.append(row)
    MANIFEST.write_text(json.dumps({"iteration":"NET-09","date":"2026-11-25","base_git_commit":BASE,
      "transformation":"Package pin schema -> KiCad schematic -> exported XML -> gate/FF/adder/mux netlist -> CPU X/glue adapter",
      "scope":"Main synchronous X and explicit execution glue; no complete-board timing/electrical/production release","files":rows},indent=2)+"\n")
    print(json.dumps({"recorded":len(rows),"failures":[]}));return 0


if __name__=="__main__":raise SystemExit(main())
