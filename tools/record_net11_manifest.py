"""Audit NET-11 decoder, scoped integration and candidate reference provenance."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net11'
MANIFEST=OUT/'manifest.json'
# Set to the published NET-10 snapshot before creating this manifest.
BASE='52bb48901fda92848add95f01097b704472d397e'


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    failures=[]
    unit=json.loads((OUT/'results.json').read_text())
    ideal=json.loads((OUT/'cpu/results-ideal.json').read_text())
    timed=json.loads((OUT/'cpu/results-timed.json').read_text())
    for r in (unit,ideal,timed):
        for item in r['sources']:
            if digest(ROOT/item['path'])!=item['sha256']:failures.append('Changed tested source '+item['path'])
        for row in r['runs']:
            if row['compile']['exit'] or row.get('execution',{}).get('exit')!=0:failures.append('Failed execution')
    if len(unit['runs'])!=2 or any('address_bank_enable_cases=4194305 failures=0' not in r['execution']['stdout'] for r in unit['runs']):failures.append('Incomplete decoder coverage')
    if len(unit['negative'])!=2 or not all(r['passed'] for r in unit['negative']):failures.append('Negative checks')
    if ideal['quick'] or len(ideal['runs'])!=4 or not ideal['runs'][-1].get('frame_matches_reference'):failures.append('Incomplete ideal integration')
    if not timed['quick'] or len(timed['runs'])!=2 or not timed['timed']:failures.append('Unexpected partial timing configuration')
    schema=json.loads((OUT/'schematic-check.json').read_text())
    if schema['failures'] or schema['components']!=64 or schema['pins']!=512 or schema['max_signal_input_loads']>4:failures.append('Pin graph')
    for name in ('erc-summary.json','propagation-paths.json'):
        evidence=json.loads((OUT/name).read_text())
        for item in evidence['sources']:
            if digest(ROOT/item['path'])!=item['sha256']:failures.append('Changed evidence source '+item['path'])
    origin=json.loads((OUT/'adapter-origin.json').read_text())
    for item in origin['files']:
        if digest(ROOT/item['path'])!=item['sha256']:failures.append('Changed adapter origin '+item['path'])
    reference=json.loads((ROOT/'references/system-candidates-2026-11-25.json').read_text())
    for item in reference['files']:
        p=ROOT/item['path']
        if digest(p)!=item['sha256'] or not p.read_bytes().startswith(b'%PDF-'):failures.append('Candidate reference '+item['path'])
    if '--check' in sys.argv:
        m=json.loads(MANIFEST.read_text())
        for item in m['files']:
            p=(ROOT/item['path']).resolve()
            if not p.is_relative_to(ROOT) or not p.is_file() or digest(p)!=item['sha256']:failures.append(item['path'])
        print(json.dumps({'checked':len(m['files']),'failures':failures,'production_released':False}));return int(bool(failures))
    if BASE.startswith('PENDING'):failures.append('NET-10 commit not pinned')
    if failures:print(json.dumps({'failures':failures}));return 1
    previous=json.loads((ROOT/'verification/net10/baseline-integrity.json').read_text())
    audit=[]
    for commit,name in [(r['git_commit'],r['manifest']) for r in previous]+[(BASE,'verification/net10/manifest.json')]:
        m=json.loads(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT));bad=[]
        for item in m['files']:
            data=subprocess.check_output(['git','show',commit+':'+item['path']],cwd=ROOT)
            if hashlib.sha256(data).hexdigest()!=item['sha256']:bad.append(item['path'])
        audit.append({'git_commit':commit,'manifest':name,'checked':len(m['files']),'failures':bad});failures+=bad
    (OUT/'baseline-integrity.json').write_text(json.dumps(audit,indent=2)+'\n')
    if failures:print(json.dumps({'failures':failures}));return 1
    files=set()
    for directory in ('hardware/memory_decode','verification/net11','sim/net11'):
        files.update(p for p in (ROOT/directory).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl' and '__pycache__' not in p.parts)
    files.update(ROOT/p for p in ['tools/build_memory_decode.py','tools/check_memory_decode_erc.py','tools/analyze_memory_decode.py','tools/run_memory_decode.py','tools/make_memory_decode_cpu.py','tools/run_memory_decode_cpu.py','tools/record_net11_manifest.py','docs/engineering/NET11.md','references/system-candidates-2026-11-25.json','README.md','AGENTS.md','PROVENANCE.md','DECISIONS.md','ROADMAP.md','CHANGELOG.md','docs/engineering/PRODUCTION_GATES.md'])
    files.update(ROOT/item['path'] for item in reference['files'])
    rows=[]
    for p in sorted(files):
        name=p.relative_to(ROOT).as_posix()
        item={'path':name,'bytes':p.stat().st_size,'sha256':digest(p),'origin':'NET-11 original development/verification, 2026-11-25'}
        old=next((r for r in reference['files'] if r['path']==name),None)
        if old:item.update(origin='Official manufacturer PDF, original bytes; candidate only',url=old['url'])
        rows.append(item)
    MANIFEST.write_text(json.dumps({'iteration':'NET-11','date':'2026-11-25','base_git_commit':BASE,
      'transformation':'HC package pin design -> KiCad XML -> address-decode simulation; separate adapter derived from RTL-01 memory and NET-10 runner',
      'scope':'Exhaustive decoder ideal/timed; full ideal CPU integration; quick delayed integration only; ERC 85 violations; no complete memory/board release','files':rows},indent=2)+'\n')
    print(json.dumps({'recorded':len(rows),'failures':[],'production_released':False}));return 0


if __name__=='__main__':raise SystemExit(main())
