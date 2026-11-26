"""Audit the conditional keypad candidate and nineteen original snapshots."""
import hashlib
import inspect
import json
from pathlib import Path
import re
import subprocess
import sys
import record_net14a_manifest as original_auditor
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net17'
BASE='30648b94d7529fe577d1984f3a8f8ccf108c1acf';MANIFEST=OUT/'manifest.json'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
exec(inspect.getsource(original_auditor.audit_history).replace('verification/net13/','verification/net16/'),globals())


def main():
    failures=[]
    def read(n):return json.loads((OUT/n).read_text())
    for name in ('electrical-results.json','policy-results.json','native/results.json','native/settling-results.json','native/resume-results.json','native/erc-summary.json'):
        d=read(name)
        for x in d.get('sources',[]):
            if digest(ROOT/x['path'])!=x['sha256']:failures.append('Changed tested source '+x['path'])
        if d.get('failures'):failures.append('Failed report '+name)
        if name=='electrical-results.json':
            if d['normal_scenarios']!=768 or d['negative_scenarios']!=3 or d['production_released']:failures.append('Electrical scope')
            a=d['analytic_bounds']
            if min(a['low_margin_after_settling_budget_v'],a['high_margin_after_settling_budget_v'])<=0 or a['sink_current_transient_upper_a']>=.008:failures.append('Analytic envelope')
            if d['assumptions']['native_guard_cycles']!=16384 or d['assumptions']['settling_budget_s']!=.002 or d['assumptions']['isolation_measured']:failures.append('Electrical assumptions')
            for x in d['runs']:
                if not x['passed'] or x['violations'] or x['exit'] or len(x['measures'])!=33 or x['dc_residual_a']>1e-9:failures.append('Normal electrical corner '+str(x['index']))
            expected={'contact resistance outside budget':'Actual key not guaranteed low','isolation outside budget':'Unconnected column not guaranteed high','capacitance outside budget':'Unconnected column not guaranteed high'}
            for x in d['negative']:
                if not x['passed'] or x['exit'] or len(x['measures'])!=33 or not any(v.startswith(expected[x['negative']]) for v in x['violations']):failures.append('Negative electrical completion '+str(x['index']))
        elif name=='policy-results.json':
            expected={'exhaustive_static_sets_0_to_3':43745,'extreme_observations':87490,'random_large_partial_ghost_frames':10000,'stateful_random_steps':100000}
            if any(d['counts'].get(k)!=v for k,v in expected.items()) or len(d['stateful_sequences'])!=8 or not d['mixed_frame_limitation']:failures.append('Policy scope/coverage')
            if not all(x['passed'] for x in d['negative']):failures.append('Policy negative')
            execution=read('policy-execution.json')
            if execution['exit'] or 'cpu_firmware_implemented' not in execution['stdout']:failures.append('Policy completion')
        elif name.endswith('erc-summary.json'):
            if d['exit']!=5 or sum(d['violation_counts'].values())!=25 or d['erc_passed'] or d['board_release']:failures.append('Partial ERC scope')
        else:
            count=3 if name.endswith('resume-results.json') else 2
            if len(d['runs'])!=count or not all(x['passed'] and x['compile']['exit']==0 and x['execution']['exit']==0 and 'RESULT ' in x['execution']['stdout'] and 'failures=0' in x['execution']['stdout'] for x in d['runs']):failures.append('Digital completion '+name)
            if not d['negative'] or not all(x['passed'] for x in d['negative']):failures.append('Digital negatives '+name)
            if name=='native/results.json' and (len(d['negative'])!=3 or any('matrix_patterns=5681 row_scans=22724' not in x['execution']['stdout'] for x in d['runs'])):failures.append('Matrix coverage')
            if name.endswith('resume-results.json'):
                for x in d['runs']:
                    if 'late_enables=2' not in x['execution']['stdout']:failures.append('Late enable coverage')
                    if x['timed']:
                        match=re.search(r'recovery=(\d+)/(\d+)',x['execution']['stdout'])
                        if not match or min(map(int,match.groups()))<2:failures.append('Safe-release apertures')
                if len(d['negative'])!=2 or not any('AHC74 reset recovery violation' in x['execution']['stdout'] and x['execution']['exit']!=0 for x in d['negative']):failures.append('Strict recovery gap missing')
    graph=read('native/schematic-check.json')
    if graph['failures'] or (graph['components'],graph['ics'],graph['pins'],graph['no_connects'])!=(110,41,806,40) or graph['max_signal_input_loads']>4:failures.append('Native pin graph')
    if read('native/preparation-check.json')['failures']:failures.append('Fixture regeneration')
    for x in read('native/check-origin.json')['files']:
        if digest(ROOT/x['base'])!=x['base_sha256'] or digest(ROOT/x['generated'])!=x['generated_sha256']:failures.append('Fixture origin '+x['generated'])
    references=json.loads((ROOT/'references/keyboard-500-2026-11-26.json').read_text())
    for x in references['files']:
        if digest(ROOT/x['path'])!=x['sha256']:failures.append('Reused PDF '+x['path'])
    if '--check' in sys.argv:
        manifest=json.loads(MANIFEST.read_text())
        for x in manifest['files']:
            p=(ROOT/x['path']).resolve()
            if not p.is_relative_to(ROOT) or not p.is_file() or digest(p)!=x['sha256']:failures.append(x['path'])
        print(json.dumps({'checked':len(manifest['files']),'failures':failures,'production_released':False}));return int(bool(failures))
    if failures:print(json.dumps({'failures':failures}));return 1
    failures+=audit_history()
    if failures:print(json.dumps({'failures':failures}));return 1
    (OUT/'acceptance.json').write_text(json.dumps({'date':'2026-11-26','conditional_contact_target_ohm':500,'conditional_model_scenarios':768,'digital_matrix_patterns_per_mode':5681,'static_policy_sets':43745,'policy_host_only':True,'full_cpu_integration_executed':False,'membranes_measured':False,'strict_recovery':'Expected rejection, not physical MTBF approval','partial_erc_violations':25,'production_released':False},indent=2)+'\n')
    names=['.gitattributes','README.md','AGENTS.md','PROVENANCE.md','ROADMAP.md','DECISIONS.md','CHANGELOG.md','docs/engineering/NET17.md','docs/engineering/VALIDATION_STATUS.md','docs/engineering/PRODUCTION_GATES.md','docs/engineering/KEYPAD_CONNECTOR.md','references/keyboard-500-2026-11-26.json']
    names+=['tools/'+n+'.py' for n in ('build_keyboard_500','prepare_keyboard_500_checks','run_keyboard_500','run_key_settle_500','run_keyboard_resume','run_keypad_500','run_keypad_policy','check_keyboard_500_erc','record_net17_manifest')]
    files={ROOT/n for n in names}
    for folder in ('hardware/keyboard_500','sim/net17','verification/net17'):
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl' and '__pycache__' not in p.parts)
    data={'iteration':'NET-17','date':'2026-11-26','base_git_commit':BASE,'scope':'Conditional 500-ohm <=2-key target, resistor variant, delayed enable and host policy; no full CPU/firmware/MTBF/PCB/physical approval','files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p),'origin':'New NET-17 work or explicitly identified intermediate/source metadata; not recovered historical originals'} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'recorded':len(files),'historical_snapshots':19,'bytes':sum(p.stat().st_size for p in files),'failures':failures,'production_released':False}));return 0


if __name__=='__main__':raise SystemExit(main())
