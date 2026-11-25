"""Audit isolated NET-15 acceptance and original snapshots at their commits."""
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
import record_net14a_manifest as original_auditor

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net15'
BASE='c1eac2581f8c08b92aff576c700a6465e16056d2';MANIFEST=OUT/'manifest.json'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
exec(inspect.getsource(original_auditor.audit_history).replace('verification/net13/','verification/net14c/'),globals())


def main():
    failures=[]
    def read(n):return json.loads((OUT/n).read_text())
    for name in ('results.json','settling-results.json','access/unit-results.json','electrical-envelope.json','erc-summary.json','access/erc-summary.json'):
        d=read(name)
        for x in d.get('sources',[]):
            if digest(ROOT/x['path'])!=x['sha256']:failures.append('Changed tested source '+x['path'])
        if d.get('failures'):failures.append('Failed report '+name)
        if name.endswith('erc-summary.json'):
            if d['exit']!=5 or d['erc_passed'] or d['board_release']:failures.append('Partial ERC classification '+name)
            continue
        if name=='electrical-envelope.json':
            if d['qualified_model_corners']!=48 or d['out_of_budget_corners']!=48 or d['physical_approval']:failures.append('Electrical scope')
            for x in d['rows']:
                if x['exit'] or (x['within_qualification_budget'] and not x['envelope_passed']):failures.append('Electrical corner '+str(x['corner']))
            if not d['out_of_budget_model_failures']:failures.append('Missing outside-budget calibration')
            continue
        expected=3 if name.startswith('access/') else 2
        if len(d['runs'])!=expected:failures.append('Run count '+name)
        for x in d['runs']:
            if x['compile']['exit'] or x['execution']['exit'] or 'RESULT ' not in x['execution']['stdout'] or 'failures=0' not in x['execution']['stdout']:failures.append('Completion '+name)
        if not d['negative'] or not all(x['passed'] for x in d['negative']):failures.append('Negative calibration '+name)
    for name,ics,pins in [('schematic-check.json',40,782),('access/schematic-check.json',31,526)]:
        d=read(name)
        count=d['ics'] if 'ics' in d else sum(x['part']!='C' for x in json.loads((ROOT/'hardware/keyboard_access/design.json').read_text())['parts'])
        if d['failures'] or count!=ics or d['pins']!=pins or d['max_signal_input_loads']>4:failures.append('Pin graph '+name)
    if '--check' in sys.argv:
        m=json.loads(MANIFEST.read_text())
        for x in m['files']:
            p=(ROOT/x['path']).resolve()
            if not p.is_relative_to(ROOT) or not p.is_file() or digest(p)!=x['sha256']:failures.append(x['path'])
        print(json.dumps({'checked':len(m['files']),'failures':failures,'production_released':False}));return int(bool(failures))
    if failures:print(json.dumps({'failures':failures}));return 1
    failures+=audit_history()
    if failures:print(json.dumps({'failures':failures}));return 1
    (OUT/'acceptance.json').write_text(json.dumps({'date':'2026-11-25','isolated_digital_passed':True,'conditional_electrical_corners':48,'cpu_raster_mmio_integrated':False,'membranes_measured':False,'production_released':False,'erc_partial_violations':[25,135]},indent=2)+'\n')
    names=['.gitattributes','README.md','AGENTS.md','ROADMAP.md','DECISIONS.md','PROVENANCE.md','CHANGELOG.md','docs/engineering/NET15.md','docs/engineering/VALIDATION_STATUS.md','docs/engineering/PRODUCTION_GATES.md','references/keyboard-candidates-2026-11-25.json']
    names += ['references/ti/'+n+'.pdf' for n in ('sn74ahc14','sn74hc14','sn74hcs125')]
    names += ['tools/'+n+'.py' for n in ('build_mmio_keyboard','build_keyboard_access','prepare_keyboard_access_checks','run_mmio_keyboard','run_keyboard_access_control','run_key_settle','run_keypad_envelope','check_keyboard_erc','record_net15_manifest')]
    files={ROOT/n for n in names}
    for folder in ('hardware/mmio_keyboard','hardware/keyboard_access','sim/net15','verification/net15'):
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl' and '__pycache__' not in p.parts)
    data={'iteration':'NET-15','date':'2026-11-25','base_git_commit':BASE,'scope':'Isolated pin-derived keyboard/MMIO, quiet timer and conditional RC envelope, no measured units or full CPU integration',
      'files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p),'origin':'New NET-15 development, official referenced PDF or explicitly classified intermediate evidence; not recovered historical revisions'} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'recorded':len(files),'historical_snapshots':17,'failures':failures,'production_released':False}));return 0


if __name__=='__main__':raise SystemExit(main())
