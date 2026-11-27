"""Audit completed Icarus evidence; optional CVC research is explicitly rejected."""
import hashlib
import inspect
import json
from pathlib import Path
import resource
import subprocess
import record_net14a_manifest as original

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net26'
BASE='64d01218193259dfc3740f71b6af5ecbe154149e'
MANIFEST=OUT/'manifest.json'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
exec(inspect.getsource(original.audit_history).replace('verification/net13/','verification/net25/'),globals())

def main():
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(120,)*2)
    failures=[]
    def hashed(rows):
        for r in rows:
            p=(ROOT/r['path']).resolve()
            if not p.is_relative_to(ROOT) or not p.is_file() or digest(p)!=r['sha256']:failures.append('Changed input '+r['path'])
    def read(name):
        data=json.loads((OUT/name).read_text());hashed(data.get('sources',[]))
        if data.get('failures'):failures.append('Failed engineering report '+name)
        return data
    def complete(row,negative=False):
        assert row['passed'] and row['compile']['exit']==0 and not row['compile']['stderr'],row
        r=row['execution']
        assert r['exit']!=0 if negative else r['exit']==0 and 'RESULT ' in r['stdout'] and 'failures=0' in r['stdout']
    for kind,ics,pins,erc_count in [('video',37,606,49),('reset',8,144,13),('keyboard',41,806,25)]:
        d=read(f'native/{kind}/schematic-check.json');assert d['ics']==ics and d['pins']==pins
        e=read(f'native/{kind}/erc-summary.json');assert not e['erc_passed'] and sum(e['violation_counts'].values())==erc_count
    topology=read('topology.json');assert topology['cross_sheet_loads']['backend_Q']['conditional_pf']==50
    b=topology['conditional_pulse_budget'];assert 22.71<b['controller_lower_ns']<22.73 and 7.71<b['keyboard_lower_ns']<7.73
    for name,count,key in [('local-phase-probe.json',156,'cases'),('local-phase-matrix.json',128,'cases'),('local-phase-negative.json',3,'runs')]:
        d=read(name);assert len(d[key])==count
        for row in d[key]:complete(row,name.endswith('negative.json'))
    memory=read('memory-pin-results.json');assert len(memory['runs'])==4 and len(memory['negative'])==2
    for row in memory['runs']:
        complete(row);assert 'active_write_cuts=12 stopped_clocks=2 max_we_inhibit_ns=94.000' in row['execution']['stdout']
    for row in memory['negative']:complete(row,True)
    for name in ['actual-cpu-write-reset.json','frequency-corners/actual-cpu-write-reset.json']:
        d=read(name);assert len(d['runs'])==2
        for row in d['runs']:
            complete(row);assert 'actual_cpu_write_cuts=2 restarted_scans=2 max_we_inhibit_ns=84.000' in row['execution']['stdout']
        for r in d.get('compiled_corner_benches',[]):assert digest(ROOT/r['path'])==r['sha256']
    for name,n in [('verified-cpu-ideal.json',6886),('verified-cpu-timed-quick.json',1062),('verified-cpu-early-timed-quick.json',1062)]:
        d=read('vectors/'+name);assert len(d['runs'])==1;row=d['runs'][0];complete(row)
        assert f'instruction_cases={n} ' in row['execution']['stdout']
        if n==1062:assert 'observed_setup_ns=54.888/16.944/26.944' in row['execution']['stdout']
        suffix=name.removeprefix('verified-cpu').removesuffix('-quick.json').removesuffix('.json')
        assert digest(OUT/'vectors'/('verified-tb_rtl_cpu'+suffix+'.sv'))==d['adapted_bench_sha256']
    program=read('program/system-program-ideal.json');assert len(program['runs'])==1
    complete(program['runs'][0]);assert program['runs'][0]['frame_matches_reference'] and program['program']['retirements']==132197
    assert 'frame_pixels=76800 wait_checks=5355850 pause_checks=46465' in program['runs'][0]['execution']['stdout']
    assert 'fixture_defaults=0' in program['runs'][0]['execution']['stdout']
    assert digest(OUT/'program/system-tb_rtl_program-ideal.sv')==program['adapted_bench_sha256']
    adapter=read('adapter-origin.json');hashed(adapter['files'])
    inventory=read('load-inventory.json');assert inventory['candidate_union_ic_count']==460 and inventory['oscillator_modules']==2
    env=read('environment.json');assert len(env['versions'])==5 and all(r['unchanged_from_baseline'] for r in env['shared_rom_inputs']);hashed(env['shared_rom_inputs'])
    # Optional engine results are deliberately NOT passed through read()/complete().
    # They remain failed, unadopted research and cannot make this circuit pass.
    compiled=json.loads((OUT/'tool-research/cvc-calibration.json').read_text());assert compiled['failures'] and not compiled['adopted_for_full_simulation']
    native=json.loads((OUT/'tool-research/cvc-native-probe.json').read_text());assert native['failures'] and not native['adopted_for_full_program']
    assert native['runs'][0]['cvc']['exit']==4 and native['runs'][0]['cvc']['limits']['memory_mb']==768
    assert 'No more memory' in native['runs'][0]['cvc']['stdout']
    if failures:print(json.dumps({'failures':failures}));return 1
    failures+=audit_history()
    if failures:print(json.dumps({'failures':failures}));return 1
    acceptance={'date':'2026-11-26','engine':'Icarus Verilog','selected_native_pulse_cases':156,'selected_matrix_cases':128,'reversion_negative_cases':3,
        'sram_active_write_cuts':48,'sram_source_pauses':8,'sram_negative_cases':2,'sram_max_we_inhibit_ns':94,
        'actual_cpu_write_cuts':8,'actual_cpu_restarted_scans':8,'cpu_max_we_inhibit_ns':84,
        'instruction_cases_ideal':6886,'timed_instruction_cases_each':1062,'timed_scenarios':2,
        'full_ideal_boot_instructions':132197,'full_ideal_boot_pixels':76800,'boot_sram_seeded':False,
        'full_timed_boot_executed':False,'candidate_union_ics':460,'oscillator_modules':2,
        'partial_erc_violations':{'video':49,'reset':13,'keyboard':25},
        'global_pvt_jitter_trace_por_mtbf_qualified':False,'power_budget_closed':False,'cvc_adopted':False,'production_released':False}
    (OUT/'acceptance.json').write_text(json.dumps(acceptance,indent=2)+'\n')
    names=['.gitattributes','README.md','ROADMAP.md','DECISIONS.md','PROVENANCE.md','CHANGELOG.md','AGENTS.md',
        'docs/engineering/NET26.md','docs/engineering/PRODUCTION_GATES.md','docs/engineering/VALIDATION_STATUS.md']
    names+=git('ls-files','--others','--exclude-standard','tools').decode().splitlines()
    names+=git('diff','--name-only',BASE,'--','tools').decode().splitlines()
    files={ROOT/n for n in names}
    for folder in ['hardware/local_phase_video','hardware/local_phase_reset','hardware/local_phase_keyboard','sim/net26','verification/net26']:
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl' and '__pycache__' not in p.parts)
    data={'iteration':'NET26','date':'2026-11-26','base_git_commit':BASE,
        'scope':'Native local reset, direct controller clock, fast keyboard MMIO family; selected Icarus regressions pass. Optional CVC research rejected, full timed boot/global electrical/production qualification open.',
        'files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'files':len(files),'historical_snapshots':29,'failures':failures,'cvc_adopted':False,'production_released':False}));return 0

if __name__=='__main__':raise SystemExit(main())
