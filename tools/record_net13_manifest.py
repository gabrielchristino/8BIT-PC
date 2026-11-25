"""Audit NET-13 scoped results, artifacts and thirteen historical snapshots."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net13'
BASE='ce19e78eeb865e7787b5f913dd5a6aa6e3914547'
MANIFEST=OUT/'manifest.json'


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    failures=[]
    control=json.loads((OUT/'access/unit-results.json').read_text());bus=json.loads((OUT/'bus-results.json').read_text())
    ideal=json.loads((OUT/'cpu/results-ideal.json').read_text());timed=json.loads((OUT/'cpu/results-timed.json').read_text());rc=json.loads((OUT/'rc-results.json').read_text())
    for report in (control,bus,ideal,timed,rc):
        for item in report['sources']:
            if digest(ROOT/item['path'])!=item['sha256']:failures.append('Changed tested source '+item['path'])
        for row in report.get('runs',[]):
            if row['compile']['exit'] or row.get('execution',{}).get('exit')!=0:failures.append('Failed execution')
    if len(control['runs'])!=3 or any('transactions=890 reset_cuts=128' not in r['execution']['stdout'] for r in control['runs']):failures.append('Controller coverage')
    if len(bus['runs'])!=4:failures.append('Bus configuration coverage')
    for collection in (control['negative'],bus['negative']):
        if len(collection)!=3 or not all(r['passed'] for r in collection):failures.append('Negative checks')
    bulk=[r for r in bus['runs'] if r['bench']=='tb_memory_bus'];fabric=[r for r in bus['runs'] if r['bench']=='tb_memory_fabric']
    if len(bulk)!=2 or not all('normal_writes=131072 reads=164096 video_reads=65536' in r['execution']['stdout'] for r in bulk):failures.append('Memory address coverage')
    if len(fabric)!=2 or not all('transactions=714' in r['execution']['stdout'] and 'all_slot_starts=32' in r['execution']['stdout'] for r in fabric):failures.append('Fabric coverage')
    if ideal['quick'] or len(ideal['runs'])!=4 or not ideal['runs'][-1].get('frame_matches_reference'):failures.append('Full ideal integration')
    if 'ram_aborts=0 vram_aborts=0 fixture_defaults=0' not in ideal['runs'][-1].get('execution',{}).get('stdout',''):failures.append('Unseeded SRAM boot missing')
    if not timed['quick'] or len(timed['runs'])!=2 or not timed['timed']:failures.append('Reduced timing integration')
    if rc['failures'] or len(rc['rows'])!=24 or not all(r['meets_conservative_500ns_rise']==r['within_rc_budget'] for r in rc['rows']):failures.append('RC sweep/calibration')
    for name,components,pins in [('schematic-check.json',80,576),('access/schematic-check.json',60,510)]:
        r=json.loads((OUT/name).read_text())
        if r['failures'] or r['components']!=components or r['pins']!=pins or r['max_signal_input_loads']>4:failures.append('Pin graph '+name)
    erc=json.loads((OUT/'erc-summary.json').read_text())
    if erc['board_release'] or any(r['erc_passed'] for r in erc['schematics']):failures.append('Unexpected partial-board ERC claim')
    collections=[r['sources'] for r in erc['schematics']]
    for name in ('control-origin.json','adapter-origin.json'):collections.append(json.loads((OUT/name).read_text())['files'])
    image=json.loads((ROOT/'firmware/net13/origin.json').read_text());collections.extend([image['sources'],image['files']])
    collections.append(json.loads((ROOT/'references/memory-bus-2026-11-25.json').read_text())['files'])
    for collection in collections:
        for item in collection:
            if digest(ROOT/item['path'])!=item['sha256']:failures.append('Changed evidence/reference '+item['path'])
    if '--check' in sys.argv:
        manifest=json.loads(MANIFEST.read_text())
        for item in manifest['files']:
            p=(ROOT/item['path']).resolve()
            if not p.is_relative_to(ROOT) or not p.is_file() or digest(p)!=item['sha256']:failures.append(item['path'])
        print(json.dumps({'checked':len(manifest['files']),'failures':failures,'production_released':False}));return int(bool(failures))
    if failures:print(json.dumps({'failures':failures}));return 1
    audit=[];previous=json.loads((ROOT/'verification/net12/baseline-integrity.json').read_text())
    for commit,name in [(r['git_commit'],r['manifest']) for r in previous]+[(BASE,'verification/net12/manifest.json')]:
        manifest=json.loads(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT));bad=[]
        for item in manifest['files']:
            data=subprocess.check_output(['git','show',commit+':'+item['path']],cwd=ROOT)
            if hashlib.sha256(data).hexdigest()!=item['sha256']:bad.append(item['path'])
        audit.append({'git_commit':commit,'manifest':name,'checked':len(manifest['files']),'failures':bad});failures+=bad
    (OUT/'baseline-integrity.json').write_text(json.dumps(audit,indent=2)+'\n')
    if failures:print(json.dumps({'failures':failures}));return 1
    files=set()
    for directory in ('hardware/memory_bus','hardware/memory_bus_access','sim/net13','verification/net13','firmware/net13'):
        files.update(p for p in (ROOT/directory).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl' and '__pycache__' not in p.parts)
    files.update(ROOT/p for p in ['.gitattributes','tools/prepare_memory_bus_access.py','tools/build_memory_bus_access.py','tools/run_memory_bus_control.py','tools/build_memory_bus.py','tools/run_memory_bus.py','tools/run_memory_pullups.py','tools/make_memory_bus_cpu.py','tools/run_memory_bus_cpu.py','tools/export_memory_diagnostic.py','tools/check_memory_bus_erc.py','tools/record_net13_manifest.py','docs/engineering/NET13.md','README.md','AGENTS.md','PROVENANCE.md','DECISIONS.md','ROADMAP.md','CHANGELOG.md','docs/engineering/PRODUCTION_GATES.md','references/memory-bus-2026-11-25.json','references/ti/sn74hct244.pdf','hardware/memory_access/memory_access_netlist.sv'])
    rows=[]
    for p in sorted(files):
        name=p.relative_to(ROOT).as_posix();row={'path':name,'bytes':p.stat().st_size,'sha256':digest(p),'origin':'NET-13 original design/model/verification work, 2026-11-25; not recovered historical originals'}
        if name=='references/ti/sn74hct244.pdf':row.update(origin='TI original PDF, unchanged, retrieved 2026-11-25; notices retained; candidate reference',url='https://www.ti.com/lit/ds/symlink/sn74hct244.pdf')
        if name=='hardware/memory_access/memory_access_netlist.sv':row['origin']='Preserved NET-12 source at base commit, used as contention negative calibration'
        rows.append(row)
    MANIFEST.write_text(json.dumps({'iteration':'NET-13','date':'2026-11-25','base_git_commit':BASE,
      'transformation':'Physical package pin maps -> KiCad XML -> tri-state chip/buffer/mux models; separate controller driver-window variant; explicit chip-array fixtures and raw EEPROM artifact matched to accepted boot',
      'scope':'Digital component scenarios + first-order pull-up RC; full ideal CPU boot with unseeded SRAM, reduced delayed CPU; partial ERC and electrical/PCB/PVT/reset-ordering criteria remain open','files':rows},indent=2)+'\n')
    print(json.dumps({'recorded':len(rows),'failures':[],'production_released':False}));return 0


if __name__=='__main__':raise SystemExit(main())
