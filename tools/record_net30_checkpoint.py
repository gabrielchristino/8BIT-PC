"""Record finished partial regressions while other outputs remain pending."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from audit_pending_timed_run import audit
from stage_net30_checkpoint import PENDING

ROOT=Path(__file__).resolve().parents[1]
BASE='b5a19c7ee72a9b8543060e77f9c26824daf271ca'
OUT=ROOT/'verification/net30'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)

def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE
    sources_checked=0
    def hashed(rows):
        nonlocal sources_checked
        for row in rows:
            assert digest(ROOT/row['path'])==row['sha256'],row['path'];sources_checked+=1
    def read(name):
        data=json.loads((OUT/name).read_text());hashed(data.get('sources',[]))
        assert not data.get('failures'),name
        return data
    def complete(row,negative=False):
        assert row['passed'] and row['compile']['exit']==0 and not row['compile']['stderr']
        result=row['execution']
        if negative:assert result['exit']!=0 and 'FATAL:' in result['stdout']
        else:assert result['exit']==0 and 'RESULT ' in result['stdout'] and 'failures=0' in result['stdout']
    graph=read('system-pin-loads.json');assert graph['connected_pins']==7814 and graph['maximum_input_count']==4
    assert sum(map(len,graph['native_pin_deltas'].values()))==15
    for kind,components,pins in [('video',74,606),('keyboard',110,806),('bus',80,576)]:
        data=read('native/'+kind+'/schematic-check.json');assert data['components']==components and data['pins']==pins
        erc=json.loads((OUT/'native'/kind/'erc-summary.json').read_text());hashed(erc['sources']);assert not erc['erc_passed']
    adapter=json.loads((OUT/'adapter-origin.json').read_text());hashed(adapter['files'])
    memory=read('memory-pin-results.json');assert len(memory['runs'])==4 and len(memory['negative'])==2
    for row in memory['runs']:complete(row);assert 'active_write_cuts=12 stopped_clocks=2 max_we_inhibit_ns=94.000' in row['execution']['stdout']
    for row in memory['negative']:complete(row,True)
    for filename,count in [('verified-cpu-ideal.json',6886),('verified-cpu-timed-quick.json',1062),('verified-cpu-early-timed-quick.json',1062)]:
        data=read('vectors/'+filename);assert len(data['runs'])==1;row=data['runs'][0];complete(row)
        assert 'instruction_cases='+str(count)+' ' in row['execution']['stdout']
    for name in ['actual-cpu-write-reset.json','frequency-corners/actual-cpu-write-reset.json']:
        data=read(name);assert len(data['runs'])==2
        for row in data['runs']:complete(row);assert 'actual_cpu_write_cuts=2 restarted_scans=2 max_we_inhibit_ns=84.000 fixture_defaults=0' in row['execution']['stdout']
        for row in data.get('compiled_corner_benches',[]):assert digest(ROOT/row['path'])==row['sha256']
    # Check every listed input of every still-pending NET30 job; additions of
    # independent future files are allowed, mutations of listed sources are not.
    states=[]
    for state_path in sorted((OUT/'jobs').glob('*/run-state.json')):
        state=json.loads(state_path.read_text())
        if state['status']=='running':hashed(json.loads((state_path.parent/'origin.json').read_text())['sources'])
        states.append({'job':state_path.parent.name,'state_at_read':state})
    assert any(r['job']=='program' and r['state_at_read']['status']=='running' for r in states)
    folder=OUT/'checkpoint';folder.mkdir(exist_ok=True)
    frozen=audit();(folder/'pending-integrity.json').write_text(json.dumps({'net27':frozen,'net30_states_at_read':states,
        'active_listed_sources_unchanged':True,'completed_hardware_reports_checked':True,'source_records_checked':sources_checked,
        'not_a_full_program_pass':True},indent=2)+'\n',newline='\n')
    docs={'.gitattributes','AGENTS.md','README.md','PROVENANCE.md','DECISIONS.md','ROADMAP.md','CHANGELOG.md','docs/engineering/NET30.md','docs/engineering/VALIDATION_STATUS.md'}
    names=[];pending=[]
    for row in git('status','--porcelain=v1','-z','--untracked-files=all').split(b'\0'):
        if not row:continue
        assert row[:2] not in (b'R ',b' R',b'C ',b' C')
        name=row[3:].decode()
        if name.startswith(PENDING):pending.append(name);continue
        allowed=name in docs or name.startswith(('hardware/load_distributed_','sim/net30/','verification/net30/')) or (name.startswith('tools/') and ('distributed' in name or name in ['tools/diagnose_load_frame_startup.py','tools/stage_net30_checkpoint.py','tools/record_net30_checkpoint.py']))
        assert allowed,name
        if name!='verification/net30/checkpoint/manifest.json':names.append(name)
    assert pending
    report={'date':'2026-11-26','base_git_commit':BASE,
        'scope':'NET30 candidate checkpoint only; native/structural and finished partial regressions. Full program and qualified-start frame results deliberately pending.',
        'python':platform.python_version(),'git':git('--version').decode().strip(),
        'commands':['WSL: python3 tools/build_distributed_loads.py','WSL: python3 tools/prepare_distributed_load_checks.py',
            'python tools/audit_distributed_loads.py','WSL: python3 tools/check_distributed_native.py',
            'WSL: python3 tools/run_distributed_load_job.py JOB','WSL: python3 tools/run_distributed_load_corners.py',
            'WSL: python3 tools/diagnose_load_frame_startup.py','WSL: python3 tools/run_distributed_load_frames.py',
            'python tools/record_net30_checkpoint.py','python tools/stage_net30_checkpoint.py verification/net30/checkpoint/manifest.json'],
        'completed_evidence':{'native_pin_changes':15,'new_ics':0,'maximum_counted_inputs':4,'sram_cuts':48,'memory_negative_cases':2,
            'ideal_instruction_cases':6886,'timed_cases_each':1062,'timed_scenarios':2,'cpu_write_cuts_nominal_and_corners':8,
            'cold_frame_fixture_initial_watchdog_preserved':True},
        'excluded_pending_run_prefix':list(PENDING),'excluded_files_at_snapshot':pending,
        'files':[{'path':name,'bytes':(ROOT/name).stat().st_size,'sha256':digest(ROOT/name)} for name in sorted(names)],
        'candidate_promoted':False,'production_released':False}
    (folder/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    print(json.dumps({'checkpoint_files':len(names),'pending_files_excluded':len(pending),'source_records_checked':sources_checked,'candidate_promoted':False}))

if __name__=='__main__':main()
