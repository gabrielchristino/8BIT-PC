"""Audit current NET-10 evidence and immutable historical snapshots."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net10'
BASE='5020e30394303971c4c0c1852a81d635365b4fee'
MANIFEST=OUT/'manifest.json'


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    failures=[]
    for mode in ('ideal','timed'):
        r=json.loads((OUT/f'results-{mode}.json').read_text())
        for item in r['sources']:
            if digest(ROOT/item['path'])!=item['sha256']:failures.append('Changed tested source '+item['path'])
        if r['quick'] or len(r['runs'])!=4:failures.append('Incomplete '+mode)
        for row in r['runs']:
            if row['compile']['exit'] or row.get('execution',{}).get('exit')!=0:failures.append('Failed '+mode+' '+row['bench'])
        if not r['runs'][-1].get('frame_matches_reference'):failures.append('Frame absent '+mode)
        if r['timed']!=(mode=='timed'):failures.append('Mode mismatch')
        if mode=='timed' and 'cpu_half=5000 video_half=7000' not in r['runs'][-1].get('execution',{}).get('stdout',''):failures.append('Unscaled timing fixture')
    negative=json.loads((OUT/'negative.json').read_text())
    for item in negative['sources']:
        if digest(ROOT/item['path'])!=item['sha256']:failures.append('Changed negative source '+item['path'])
    if len(negative['checks'])!=2 or not all(v['passed'] for v in negative['checks']):failures.append('Negative checks')
    schema=json.loads((OUT/'schematic-check.json').read_text())
    if schema['failures'] or schema['components']!=566 or schema['pins']!=4892 or schema['max_signal_input_loads']>4:failures.append('Pin graph')
    erc=json.loads((OUT/'erc-summary.json').read_text())
    if erc['board_release'] or erc['erc_passed']:failures.append('Unexpected CPU-only ERC claim')
    for item in erc['sources']:
        if digest(ROOT/item['path'])!=item['sha256']:failures.append('Changed ERC source '+item['path'])
    if '--check' in sys.argv:
        m=json.loads(MANIFEST.read_text())
        for item in m['files']:
            p=(ROOT/item['path']).resolve()
            if not p.is_relative_to(ROOT) or not p.is_file() or digest(p)!=item['sha256']:failures.append(item['path'])
        print(json.dumps({'checked':len(m['files']),'failures':failures,'production_released':False}));return int(bool(failures))
    previous=json.loads((ROOT/'verification/net09/baseline-integrity.json').read_text())
    snapshots=[(row['git_commit'],row['manifest']) for row in previous]+[(BASE,'verification/net09/manifest.json')]
    audit=[]
    for commit,name in snapshots:
        m=json.loads(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT));bad=[]
        for row in m['files']:
            data=subprocess.check_output(['git','show',commit+':'+row['path']],cwd=ROOT)
            if hashlib.sha256(data).hexdigest()!=row['sha256']:bad.append(row['path'])
        audit.append({'git_commit':commit,'manifest':name,'checked':len(m['files']),'failures':bad});failures+=bad
    (OUT/'baseline-integrity.json').write_text(json.dumps(audit,indent=2)+'\n')
    if failures:print(json.dumps({'failures':failures}));return 1
    files=set()
    for directory in ('hardware/cpu_global','verification/net10'):
        files.update(p for p in (ROOT/directory).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl' and '__pycache__' not in p.parts)
    files.update(ROOT/p for p in ['.gitattributes','.gitignore','tools/build_cpu_global.py','tools/convert_cpu_global.py','tools/check_cpu_global_negative.py','tools/check_cpu_global_erc.py','tools/run_cpu_global.py','tools/record_net10_manifest.py','docs/engineering/NET10.md','docs/engineering/KICAD_ENVIRONMENT.md','README.md','AGENTS.md','PROVENANCE.md','DECISIONS.md','ROADMAP.md','CHANGELOG.md','docs/engineering/PRODUCTION_GATES.md'])
    rows=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p),'origin':'NET-10 original development and verification, 2026-11-25; earlier failure logs are not acceptance'} for p in sorted(files)]
    MANIFEST.write_text(json.dumps({'iteration':'NET-10','date':'2026-11-25','base_git_commit':BASE,
        'transformation':'Eight preserved package graphs -> distribution buffers -> hierarchical KiCad -> exported XML -> joined CPU pin simulation',
        'scope':'CPU digital integration only; ERC retains 56 violations, production blocked','files':rows},indent=2)+'\n')
    print(json.dumps({'recorded':len(rows),'failures':[],'production_released':False}));return 0


if __name__=='__main__':raise SystemExit(main())
