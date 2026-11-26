"""Accept complete source-clock evidence and audit26 predecessor snapshots."""
import hashlib
import inspect
import json
from pathlib import Path
import re
import subprocess
import sys
import record_net14a_manifest as original

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net23'
BASE='cbb38703c34cf119612f39ecb0255940e670f974'
MANIFEST=OUT/'manifest.json'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
exec(inspect.getsource(original.audit_history).replace('verification/net13/','verification/net22/'),globals())


def main():
    failures=[]

    def hashed(item):
        path=(ROOT/item['path']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or digest(path)!=item['sha256']:
            failures.append('Changed source '+item['path'])

    def read(name):
        path=OUT/name
        if not path.is_file():
            failures.append('Missing completed report '+name)
            return {}
        data=json.loads(path.read_text())
        if data.get('failures'):failures.append('Failed report '+name)
        for item in data.get('sources',[]):hashed(item)
        return data

    def complete(row,label,negative=None):
        result=row.get('execution',{})
        output=result.get('stdout','')
        if row.get('compile',{}).get('exit')!=0 or row.get('compile',{}).get('stderr') or not row.get('passed',True):
            failures.append('Compile/acceptance '+label)
        if negative:
            if result.get('exit') in (None,0) or negative not in output:failures.append('Negative not detected '+label)
        elif result.get('exit')!=0 or 'RESULT ' not in output or 'failures=0' not in output:
            failures.append('Incomplete execution '+label)
        return output

    graph=read('native/schematic-check.json')
    if tuple(graph.get(k) for k in ['components','ics','logic_ics','supervisor_ics','oscillator_modules','pins','no_connects'])!=(26,8,7,1,2,144,7):
        failures.append('Native inventory/classification')
    erc=read('native/erc-summary.json')
    if erc.get('exit')!=5 or erc.get('erc_passed') is not False or sum(erc.get('violation_counts',{}).values())!=12:
        failures.append('Partial ERC scope')
    sources=read('clock-source-results.json')
    if len(sources.get('runs',[]))!=6:failures.append('Source startup coverage')
    for row in sources.get('runs',[]):
        output=complete(row,'source startup')
        wanted='access_inhibited=1' if row['parameters'].get('ABSENT') else 'starts=2 reset_cuts=3'
        if wanted not in output:failures.append('Source completion')
    model=read('clock-model-calibration.json')
    if len(model.get('runs',[]))!=2 or len(model.get('negative',[]))!=3:failures.append('Model calibration count')
    for row in model.get('runs',[]):complete(row,'model calibration')
    for row in model.get('negative',[]):complete(row,'model guard',row['expected_rejection'])
    for name in ['actual-cpu-write-reset.json','frequency-corners/actual-cpu-write-reset.json']:
        cpu=read(name)
        if [r['policy'] for r in cpu.get('runs',[])]!=[0,1]:failures.append('CPU fault policies '+name)
        for row in cpu.get('runs',[]):
            output=complete(row,'actual CPU fault')
            deadline=re.search(r'max_we_inhibit_ns=([\d.]+)',output)
            if 'actual_cpu_write_cuts=2 restarted_scans=2' not in output or 'fixture_defaults=0' not in output or not deadline or float(deadline[1])>100:
                failures.append('Actual CPU completion/deadline '+name)
    memory=read('source-memory-results.json')
    if [(r['absent'],r['force_safe_memory']) for r in memory.get('runs',[])]!=[(0,False),(1,False),(2,False)] or len(memory.get('negative',[]))!=1:
        failures.append('Physical source-memory coverage')
    for row in memory.get('runs',[]):
        output=complete(row,'source SRAM')
        wanted='physical_we_inhibited=1' if row['absent'] else 'normal_sram_write=1 active_write_cut=1'
        if wanted not in output:failures.append('Physical source-memory completion')
    for row in memory.get('negative',[]):complete(row,'source SRAM negative',row['expected_rejection'])
    loads=read('clock-loads.json')
    if [r['total_budget_pf'] for r in loads.get('nets',[])]!=[15,15,30] or loads.get('oscillator_output_load_qualified') is not False:
        failures.append('Source load budget/scope')
    if len(loads.get('negative',[]))!=2 or not all(r['passed'] for r in loads.get('negative',[])):failures.append('Load negatives')
    for name,bench,marker in [('verified-cpu-ideal.json','verified-tb_rtl_cpu-ideal.sv','instruction_cases=6886 transactions=13406'),
                              ('verified-cpu-timed-quick.json','verified-tb_rtl_cpu-timed.sv','instruction_cases=1062 transactions=1821'),
                              ('verified-cpu-early-timed-quick.json','verified-tb_rtl_cpu-early-timed.sv','instruction_cases=1062 transactions=1821')]:
        data=read('vectors/'+name)
        if len(data.get('runs',[]))!=1:failures.append('Instruction coverage '+name)
        for row in data.get('runs',[]):
            if marker not in complete(row,name):failures.append('Instruction completion '+name)
        if data and digest(OUT/'vectors'/bench)!=data.get('adapted_bench_sha256'):failures.append('Compiled bench '+name)
    for name in ['cpu-adapter-origin.json','vectors-adapter-origin.json','ideal-adapter-origin.json']:
        for item in read(name).get('files',[]):hashed(item)
    environment=read('environment.json')
    if environment.get('source'):hashed(environment['source'])
    if len(environment.get('versions',[]))!=5 or len(environment.get('shared_rom_inputs',[]))!=4:failures.append('Environment')
    for item in environment.get('shared_rom_inputs',[]):
        hashed(item)
        if not item['unchanged_from_baseline']:failures.append('ROM changed')
    research=read('research/source.json')
    read('research/input-limits.json')
    if research:
        hashed(research);hashed(research['source'])
        hashed({'path':research['extraction'],'sha256':research['extraction_sha256']})
        if research['selected_for_bom']:failures.append('Research promoted to BOM')
    snapshot=read('development/pre-cpu-schmitt/snapshot.json')
    if snapshot.get('source'):hashed(snapshot['source'])
    if len(snapshot.get('files',[]))!=30:failures.append('Intermediate snapshot coverage')
    for item in snapshot.get('files',[]):
        if item['sha256']!=item['copied_sha256']:failures.append('Intermediate copy '+item['snapshot'])
        hashed({'path':item['snapshot'],'sha256':item['sha256']})
    if failures:
        print(json.dumps({'failures':failures,'production_released':False}));return 1
    if '--check' in sys.argv:
        data=json.loads(MANIFEST.read_text())
        for item in data['files']:hashed(item)
        print(json.dumps({'checked':len(data['files']),'failures':failures}));return int(bool(failures))
    failures+=audit_history()
    if failures:
        print(json.dumps({'failures':failures}));return 1
    (OUT/'acceptance.json').write_text(json.dumps({'date':'2026-11-26','source_startup_scenarios':4,'source_absence_scenarios':2,
        'model_positive_modes':2,'model_invalid_parameter_negatives':3,'actual_cpu_write_cuts':8,'actual_cpu_restart_scans':8,
        'memory_master_active_cuts':1,'source_absence_physical_we_checks':2,'physical_we_negative_detected':True,
        'selected_max_we_inhibit_ns':84,'instruction_cases_ideal':6886,'instruction_cases_per_timed_scenario':1062,
        'timed_controller_cq_scenarios':2,'ics':8,'logic_ics':7,'supervisor_ics':1,'oscillator_modules':2,
        'partial_erc_violations':12,'new_full_boot_executed':False,'full_pvt_jitter_por_or_bom_qualified':False,'production_released':False},indent=2)+'\n')
    names=['.gitattributes','README.md','AGENTS.md','PROVENANCE.md','ROADMAP.md','DECISIONS.md','CHANGELOG.md',
           'docs/engineering/NET23.md','docs/engineering/VALIDATION_STATUS.md','docs/engineering/PRODUCTION_GATES.md']
    names+=git('ls-files','--others','--exclude-standard','tools').decode().splitlines()
    names+=git('diff','--name-only',BASE,'--','tools').decode().splitlines()
    files={ROOT/n for n in names}
    for folder in ['hardware/clocked_reset','sim/net23','verification/net23','references/net23']:
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl' and '__pycache__' not in p.parts)
    data={'iteration':'NET23','date':'2026-11-26','base_git_commit':BASE,
          'scope':'Configured oscillator/reset candidate, Schmitt CPU reception and selected source-driven digital CPU/memory proofs. No full PN, extracted loads, analog oscillator/jitter/POR/global PVT/MTBF or fabrication approval.',
          'files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'recorded':len(files),'prior_snapshots':26,'failures':failures,'production_released':False}));return 0


if __name__=='__main__':raise SystemExit(main())
