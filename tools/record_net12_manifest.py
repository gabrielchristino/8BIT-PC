"""Audit scoped NET-12 evidence and all twelve previous snapshots."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net12'
BASE='3cac9fca256377186960d106d08d7ccd0ca6c6dc'
MANIFEST=OUT/'manifest.json'


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    failures=[]
    unit=json.loads((OUT/'unit-results.json').read_text());ideal=json.loads((OUT/'cpu/results-ideal.json').read_text());timed=json.loads((OUT/'cpu/results-timed.json').read_text())
    for r in (unit,ideal,timed):
        for item in r['sources']:
            if digest(ROOT/item['path'])!=item['sha256']:failures.append('Changed tested source '+item['path'])
        for row in r['runs']:
            if row['compile']['exit'] or row.get('execution',{}).get('exit')!=0:failures.append('Failed execution')
    if len(unit['runs'])!=3 or any('transactions=890 reset_cuts=128' not in r['execution']['stdout'] for r in unit['runs']):failures.append('Controller coverage incomplete')
    if len(unit['negative'])!=3 or not all(r['passed'] for r in unit['negative']):failures.append('Negative checks')
    if ideal['quick'] or len(ideal['runs'])!=4 or not ideal['runs'][-1].get('frame_matches_reference'):failures.append('Full ideal integration absent/failed')
    if not timed['quick'] or len(timed['runs'])!=2 or not timed['timed']:failures.append('Partial timing configuration absent')
    schema=json.loads((OUT/'schematic-check.json').read_text())
    if schema['failures'] or schema['components']!=56 or schema['pins']!=478 or schema['max_signal_input_loads']>4:failures.append('Pin graph')
    erc=json.loads((OUT/'erc-summary.json').read_text())
    if erc['board_release'] or erc['erc_passed']:failures.append('Unexpected partial-board ERC claim')
    origin=json.loads((OUT/'adapter-origin.json').read_text())
    for collection in (erc['sources'],origin['files']):
        for item in collection:
            if digest(ROOT/item['path'])!=item['sha256']:failures.append('Changed evidence source '+item['path'])
    basis=json.loads((OUT/'timing-basis.json').read_text())
    for item in basis['sources']:
        if digest(ROOT/item['path'])!=item['sha256']:failures.append('Changed PDF '+item['path'])
    if '--check' in sys.argv:
        m=json.loads(MANIFEST.read_text())
        for item in m['files']:
            p=(ROOT/item['path']).resolve()
            if not p.is_relative_to(ROOT) or not p.is_file() or digest(p)!=item['sha256']:failures.append(item['path'])
        print(json.dumps({'checked':len(m['files']),'failures':failures,'production_released':False}));return int(bool(failures))
    if failures:print(json.dumps({'failures':failures}));return 1
    previous=json.loads((ROOT/'verification/net11/baseline-integrity.json').read_text());audit=[]
    for commit,name in [(r['git_commit'],r['manifest']) for r in previous]+[(BASE,'verification/net11/manifest.json')]:
        m=json.loads(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT));bad=[]
        for item in m['files']:
            data=subprocess.check_output(['git','show',commit+':'+item['path']],cwd=ROOT)
            if hashlib.sha256(data).hexdigest()!=item['sha256']:bad.append(item['path'])
        audit.append({'git_commit':commit,'manifest':name,'checked':len(m['files']),'failures':bad});failures+=bad
    (OUT/'baseline-integrity.json').write_text(json.dumps(audit,indent=2)+'\n')
    if failures:print(json.dumps({'failures':failures}));return 1
    files=set()
    for directory in ('hardware/memory_access','verification/net12','sim/net12'):
        files.update(p for p in (ROOT/directory).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl' and '__pycache__' not in p.parts)
    files.update(ROOT/p for p in ['tools/build_memory_access.py','tools/run_memory_access.py','tools/make_memory_access_cpu.py','tools/run_memory_access_cpu.py','tools/check_memory_access_erc.py','tools/record_net12_manifest.py','docs/engineering/NET12.md','README.md','AGENTS.md','PROVENANCE.md','DECISIONS.md','ROADMAP.md','CHANGELOG.md','docs/engineering/PRODUCTION_GATES.md'])
    files.update(ROOT/'references/ti'/name for name in ['sn74ahc08.pdf','sn74ahc32.pdf','sn74ahc04.pdf','sn74ahc125.pdf','sn74hc174.pdf','sn74hc74.pdf','sn74hc377.pdf','sn74hct377.pdf'])
    rows=[]
    for p in sorted(files):
        name=p.relative_to(ROOT).as_posix();row={'path':name,'bytes':p.stat().st_size,'sha256':digest(p),'origin':'NET-12 original engineering/verification, 2026-11-25; intermediate logs identified separately'}
        if name.startswith('references/ti/'):
            row.update(origin='Previously preserved official TI PDF, original bytes; selected model only, no qualified BOM',url='https://www.ti.com/lit/ds/symlink/'+p.name)
        rows.append(row)
    MANIFEST.write_text(json.dumps({'iteration':'NET-12','date':'2026-11-25','base_git_commit':BASE,
      'transformation':'HC/HCT/AHC package pins -> KiCad XML -> memory payload/state/strobe netlist -> separate simulation adapter and scoped CPU fixtures',
      'scope':'Three isolated controller scenarios; full ideal CPU integration; quick delayed integration; arrays/MMIO/raster/data-bus still models; ERC 129 violations, production blocked','files':rows},indent=2)+'\n')
    print(json.dumps({'recorded':len(rows),'failures':[],'production_released':False}));return 0


if __name__=='__main__':raise SystemExit(main())
