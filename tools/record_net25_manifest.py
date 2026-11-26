"""Archive an unpromoted experiment with functional successes AND open failures."""
import hashlib
import inspect
import json
from pathlib import Path
import re
import subprocess
import record_net14a_manifest as original

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net25'
BASE='5a871ff3ddc58986ae1fb7998690bb9ec3711d5b'
MANIFEST=OUT/'manifest.json'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
exec(inspect.getsource(original.audit_history).replace('verification/net13/','verification/net24/'),globals())

def main():
    failures=[]
    def check_sources(data,key='sources'):
        for row in data.get(key,[]):
            p=ROOT/row['path']
            if not p.is_file() or digest(p)!=row['sha256']:failures.append('changed source '+row['path'])
    def read(name,allow_failure=False):
        p=OUT/name
        if not p.is_file():raise RuntimeError('Missing completed report '+name)
        data=json.loads(p.read_text());check_sources(data)
        if data.get('failures') and not allow_failure:failures.append('failed report '+name)
        return data
    def complete(row,negative=False):
        assert row['passed'],row
        assert row['compile']['exit']==0 and not row['compile']['stderr'],row
        r=row['execution']
        assert r['exit']!=0 if negative else r['exit']==0 and 'RESULT ' in r['stdout'] and 'failures=0' in r['stdout']
    for kind in ['video','reset']:
        r=read(f'native/{kind}/schematic-check.json');assert r['ics']==(36 if kind=='video' else 8)
        erc=read(f'native/{kind}/erc-summary.json');assert not erc['erc_passed'] and erc['exit']!=0
        assert sum(erc['violation_counts'].values())==(49 if kind=='video' else 14)
    topology=read('topology.json');assert topology['pin_contracts_checked']==16
    warm=read('warm-calibration.json');assert len(warm['runs'])==18
    for row in warm['runs']:complete(row,row['expected_rejection'])
    probe=read('drain-pulse.json');assert len(probe['cases'])==32
    for row in probe['cases']:complete(row)
    startup=read('drain-startup.json',True)
    assert len(startup['cases'])==55 and len(startup['failures'])==1
    assert startup['failures'][0]=={'PROFILE':1,'POLICY':0,'RAW_LOW_NS':50,'OFFSET_NS':39}
    assert 'AHC74 reset recovery violation' in startup['cases'][-1]['execution']['stdout']
    assert 'video.U36_1' in startup['cases'][-1]['execution']['stdout'] and not startup['strict_cold_clock_envelope_qualified']
    for row in startup['cases'][:-1]:complete(row)
    cold=json.loads((OUT/'development/strict-cold-clock/result.json').read_text())
    assert not cold['cases'][-1]['passed'] and 'measured_ns=7.722 required_ns=20 clr_n=0' in cold['cases'][-1]['execution']['stdout']
    hyp=read('local-sync-hypothesis.json');assert len(hyp['cases'])==156 and not hyp['native_schematic_exists_for_hypothesis'] and not hyp['strict_cold_clock_pulses_qualified']
    for row in hyp['cases']:complete(row)
    direct=read('direct-backend-hypothesis.json');assert len(direct['cases'])==156 and direct['strict_selected_cases'] and not direct['native_schematic_exists_for_hypothesis']
    for row in direct['cases']:
        complete(row);assert 'OPEN_RESET_CLOCK' not in row['execution']['stdout']
    negatives=read('direct-backend-negative.json');assert len(negatives['runs'])==2
    for row in negatives['runs']:complete(row,True)
    cpu=read('actual-cpu-write-reset.json');assert len(cpu['runs'])==2
    for row in cpu['runs']:
        complete(row);assert 'actual_cpu_write_cuts=2 restarted_scans=2 max_we_inhibit_ns=84.000' in row['execution']['stdout']
    for name,n in [('verified-cpu-ideal.json',6886),('verified-cpu-timed-quick.json',1062),('verified-cpu-early-timed-quick.json',1062)]:
        data=read('vectors/'+name);assert len(data['runs'])==1
        complete(data['runs'][0]);assert f'instruction_cases={n} ' in data['runs'][0]['execution']['stdout']
        suffix=name.removeprefix('verified-cpu').removesuffix('-quick.json').removesuffix('.json')
        assert digest(OUT/'vectors'/('verified-tb_rtl_cpu'+suffix+'.sv'))==data['adapted_bench_sha256']
    program=read('program/system-program-ideal.json');assert len(program['runs'])==1
    complete(program['runs'][0]);assert program['runs'][0]['frame_matches_reference'] and program['program']['retirements']==132197
    assert 'fixture_defaults=0' in program['runs'][0]['execution']['stdout']
    assert digest(OUT/'program/system-tb_rtl_program-ideal.sv')==program['adapted_bench_sha256']
    for name in ['probe-origin.json','system-adapter-origin.json']:
        data=read(name);check_sources(data,'files')
    env=read('environment.json');assert len(env['versions'])==5 and all(r['unchanged_from_baseline'] for r in env['shared_rom_inputs'])
    check_sources(env,'shared_rom_inputs');read('ahc04-reference.json')
    if failures:print(json.dumps({'failures':failures}));return 1
    failures+=audit_history()
    if failures:print(json.dumps({'failures':failures}));return 1
    acceptance={'date':'2026-11-26','experiment_promoted':False,'functional_ideal_instruction_cases':6886,'functional_timed_cases_each':1062,'timed_scenarios':2,
        'actual_cpu_write_cuts':4,'actual_cpu_restarted_scans':4,'selected_we_inhibit_ns':84,'strict_selected_pulse_cases':32,
        'full_ideal_boot_retirements':132197,'full_ideal_boot_pixels':76800,'full_timed_boot_executed':False,
        'known_strict_cold_clock_rejection_ns':7.722,'cold_clock_required_ns':20,'strict_cold_clock_qualified':False,
        'known_short_raw_recovery_rejection':startup['failures'][0],'extended_native_cases_completed':54,'extended_native_first_failure_case':55,
        'hypothesis_only_hdl_functional_cases':156,'hypothesis_native_schematic_exists':False,
        'hypothesis_cold_clock_qualified':False,'analog_mtbf_por_qualified':False,'partial_erc_violations_video':49,'partial_erc_violations_reset':14,'production_released':False}
    acceptance.update(second_hdl_hypothesis_strict_controller_cases=156,second_hdl_hypothesis_negative_calibrations=2,second_hdl_hypothesis_keyboard_instantiated=False)
    (OUT/'acceptance.json').write_text(json.dumps(acceptance,indent=2)+'\n')
    names=['.gitattributes','README.md','ROADMAP.md','DECISIONS.md','PROVENANCE.md','CHANGELOG.md','AGENTS.md',
        'docs/engineering/NET25.md','docs/engineering/CLOCK_TREE_STUDY.md','docs/engineering/PRODUCTION_GATES.md','docs/engineering/VALIDATION_STATUS.md']
    names+=git('ls-files','--others','--exclude-standard','tools').decode().splitlines()
    names+=git('diff','--name-only',BASE,'--','tools').decode().splitlines()
    files={ROOT/n for n in names}
    for folder in ['hardware/phase_drain_video','hardware/phase_drain_reset','sim/net25','verification/net25']:
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl' and '__pycache__' not in p.parts)
    manifest={'iteration':'NET25 experimental NOT promoted','date':'2026-11-26','base_git_commit':BASE,
        'scope':'Functional successes plus preserved cold clock and short RAW recovery rejections; simulation-only next hypothesis not a native circuit. No fabrication qualification.',
        'files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'files':len(files),'historical_snapshots':28,'failures':failures,'experiment_promoted':False}));return 0

if __name__=='__main__':raise SystemExit(main())
