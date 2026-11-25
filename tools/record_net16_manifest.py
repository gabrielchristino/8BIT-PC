"""Audit reset pre-design/native candidates without promoting model assumptions."""
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
import record_net14a_manifest as original_auditor
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net16'
BASE='f297efb645a7cbaf75f7deee03ce805acce2dd32';MANIFEST=OUT/'manifest.json'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
exec(inspect.getsource(original_auditor.audit_history).replace('verification/net13/','verification/net15/'),globals())


def main():
    failures=[]
    def read(n):return json.loads((OUT/n).read_text())
    for name in ('reset-order-envelope.json','native/reset-order-envelope.json','native/results.json','native/apertures.json','native/erc-summary.json'):
        d=read(name)
        for x in d.get('sources',[]):
            if digest(ROOT/x['path'])!=x['sha256']:failures.append('Changed tested source '+x['path'])
        if d.get('failures'):failures.append('Failed report '+name)
        if name.endswith('erc-summary.json'):
            if d['exit']!=5 or sum(d['violation_counts'].values())!=6 or d['erc_passed'] or d['board_release']:failures.append('ERC partial scope')
        elif name.endswith('envelope.json'):
            if d['summary']['qualified_scenarios']!=128 or len(d['rows'])!=129 or not all(x['passed'] for x in d['negative']):failures.append('RC acceptance '+name)
            for x in d['rows']:
                if x['exit'] or ('crossing_s' not in x):failures.append('RC completion '+name)
            if any(x['qualified'] for x in d['supervisor_hold_up_screen']):failures.append('Screen promoted to qualification')
        else:
            expected=16 if name.endswith('results.json') else 2
            if len(d['runs'])!=expected or not all(x['passed'] and 'RESULT ' in x['execution']['stdout'] and 'failures=0' in x['execution']['stdout'] for x in d['runs']):failures.append('Digital completion '+name)
            if not d['negative'] or not all(x['passed'] and x['execution']['exit']!=0 for x in d['negative']):failures.append('Negatives '+name)
            if name.endswith('apertures.json') and 'AHC74 reset recovery violation' not in d['negative'][0]['execution']['stdout']:failures.append('Strict recovery rejection')
    graph=read('native/schematic-check.json')
    if graph['failures'] or graph['ics']!=5 or graph['pins']!=84 or graph['max_signal_input_loads']>4:failures.append('Native pin graph')
    for name in ('native/rc-origin.json','native/erc-origin.json'):
        d=read(name)
        if digest(ROOT/d['base'])!=d['base_sha256'] or digest(ROOT/d['generated'])!=d['generated_sha256']:failures.append('Transformation '+name)
    for x in read('research/transformations.json')['files']:
        if digest(ROOT/x['path'])!=x['sha256']:failures.append('Research transformation '+x['path'])
    if '--check' in sys.argv:
        m=json.loads(MANIFEST.read_text())
        for x in m['files']:
            p=(ROOT/x['path']).resolve()
            if not p.is_relative_to(ROOT) or not p.is_file() or digest(p)!=x['sha256']:failures.append(x['path'])
        print(json.dumps({'checked':len(m['files']),'failures':failures,'production_released':False}));return int(bool(failures))
    if failures:print(json.dumps({'failures':failures}));return 1
    failures+=audit_history()
    if failures:print(json.dumps({'failures':failures}));return 1
    (OUT/'acceptance.json').write_text(json.dumps({'date':'2026-11-25','isolated_model_passed':True,'rc_scenarios_per_envelope':128,'digital_configs':16,'cuts_per_config':32,'strict_external_recovery':'Expected rejection; physical MTBF remains open','supervisor_qualified':False,'full_cpu_integration_executed':False,'production_released':False},indent=2)+'\n')
    names=['.gitattributes','README.md','ROADMAP.md','PROVENANCE.md','AGENTS.md','CHANGELOG.md','DECISIONS.md','docs/engineering/VALIDATION_STATUS.md','docs/engineering/NET16A.md','docs/engineering/NET16B.md','references/power-candidates/tlv803e.pdf']
    names+=['tools/'+n+'.py' for n in ('run_reset_order_envelope','run_reset_buffered_envelope','build_reset_domains','run_reset_domains','run_reset_apertures','check_reset_domains_erc','record_net16_manifest')]
    files={ROOT/n for n in names}
    for folder in ('hardware/reset_domains','sim/net16','verification/net16'):
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl' and '__pycache__' not in p.parts)
    data={'iteration':'NET-16A/B','date':'2026-11-25','base_git_commit':BASE,'scope':'Pre-design RC/supply screen and native delayed reset candidate; no supervisor qualification, full CPU integration, MTBF or PCB approval','files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p),'origin':'New reset candidate work, official PDF/extraction or explicitly classified intermediate evidence; not recovered historical originals'} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'recorded':len(files),'historical_snapshots':18,'failures':failures,'production_released':False}));return 0


if __name__=='__main__':raise SystemExit(main())
