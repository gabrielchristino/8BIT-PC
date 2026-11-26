"""Audit the accepted NET19 scenarios, retain failures, audit 22 old snapshots."""
import hashlib
import inspect
import json
from pathlib import Path
import re
import subprocess
import sys
import record_net14a_manifest as original

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net19a'
BASE='9a21166ebdcd8d0dd118345e27b735ee75296984'
MANIFEST=OUT/'manifest.json'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)


exec(inspect.getsource(original.audit_history).replace('verification/net13/','verification/export-2026-11-26/'),globals())


def main():
    failures=[]
    def read(name):
        data=json.loads((OUT/name).read_text())
        if data.get('failures'):failures.append('Failed accepted report '+name)
        for item in data.get('sources',[]):
            if digest(ROOT/item['path'])!=item['sha256']:failures.append('Changed tested source '+item['path'])
        return data
    def complete(row,name,negative=False):
        execution=row.get('execution',{})
        if row['compile']['exit'] or not row.get('passed',True):failures.append('Compile/acceptance '+name)
        if negative:
            wanted=row.get('expected_rejection')
            if not isinstance(execution.get('exit'),int) or execution['exit']==0 or not wanted or wanted not in execution.get('stdout',''):failures.append('Negative completion '+name)
        elif execution.get('exit')!=0 or 'RESULT ' not in execution.get('stdout','') or 'failures=0' not in execution['stdout']:
            failures.append('Positive completion '+name)
        return execution.get('stdout','')
    positive=['verified-cpu-ideal.json','verified-cpu-timed-quick.json','verified-cpu-early-timed-quick.json','verified-safety-ideal.json','system-program-ideal.json']
    for name in positive:
        data=read(name)
        if len(data['runs'])!=1:failures.append('Run count '+name);continue
        row=data['runs'][0];output=complete(row,name)
        if name.startswith('verified-cpu'):
            count=1062 if data['quick'] else 6886
            if f'instruction_cases={count}' not in output:failures.append('Instruction coverage '+name)
            if data['timed']:
                match=re.search(r'STATE_TIMING observed_setup_ns=([\d.]+)/([\d.]+)/([\d.]+)',output)
                if not match or min(map(float,match.groups()))<4.5:failures.append('AHC174 timing '+name)
        elif name=='verified-safety-ideal.json':
            if 'reset_power_cases=4562 opcodes=26 failures=0' not in output:failures.append('Ideal cuts')
        else:
            if not row.get('frame_matches_reference') or 'retirements=132197 transactions=232576' not in output or 'frame_pixels=76800' not in output or 'fixture_defaults=0' not in output:failures.append('Boot/frame/unknown SRAM scope')
        if name.startswith('verified-'):
            filename='verified-'+data['bench']+('-early' if data['early_state_cq'] else '')+('-timed' if data['timed'] else '-ideal')+'.sv'
        else:filename='system-tb_rtl_program-ideal.sv'
        if digest(OUT/filename)!=data['adapted_bench_sha256']:failures.append('Actual compiled bench '+name)
        if data.get('early_state_cq') and '.CONTROL_EARLY(1)' not in (OUT/filename).read_text():failures.append('Early delay parameter unused')
    for name,wanted in [('verified-cpu-negative-bank-ideal-quick.json','MMIO register changed without sampled commit'),('verified-cpu-legacy-state-timed-quick.json','DFF data setup violation')]:
        data=read(name);row=data['runs'][0]
        if row.get('expected_rejection')!=wanted:failures.append('Negative meaning '+name)
        complete(row,name,True)
        stem='verified-'+data['bench']+('-negative-bank' if data['negative_bank'] else '-legacy-state')+('-timed' if data['timed'] else '-ideal')+'.sv'
        if digest(OUT/stem)!=data['adapted_bench_sha256']:failures.append('Actual negative bench '+name)
        if data.get('legacy_state'):
            item=data['negative_model_origin']
            if digest(ROOT/item['path'])!=item['sha256']:failures.append('Legacy hardware origin')
    batches=read('timed-safety-batches.json')
    intervals=[[i,min(i+4,26)] for i in range(0,26,4)]
    if [r['opcode_interval'] for r in batches['runs']]!=intervals or batches['covered_opcode_indices']!=list(range(26)) or batches['reset_power_cases']!=1692:failures.append('Incomplete/duplicate delayed cuts')
    import run_system_vectors as adapter
    refs=json.loads((ROOT/'hardware/cpu_global/design.json').read_text())['reference_map']
    text=adapter.fixture((ROOT/'sim/tests/tb_rtl_safety.sv').read_text(),True,refs)
    for row in batches['runs']:
        output=complete(row,'batch '+str(row['opcode_interval']))
        lo,hi=row['opcode_interval'];expected=text.replace('for(oi=0;oi<26;oi=oi+1)begin',f'for(oi={lo};oi<{hi};oi=oi+1)begin')
        if hashlib.sha256(expected.encode()).hexdigest()!=row['adapted_bench_sha256']:failures.append('Batch transformation '+str(lo))
    for name in ['system-scan-timed.json','policy0/system-scan-timed.json']:
        data=read(name);output=complete(data,name)
        for marker in ['scan_frames=5 completed_column_reads=40','completed_row_writes=20 total_row_writes=21','stopped_cpu_checks=1 reset_pending_checks=1']:
            if marker not in output:failures.append('Scan coverage '+name)
        image=OUT/('policy0/' if name.startswith('policy0/') else '')/'system-keyboard-scan-eeprom.bin'
        if image.stat().st_size!=32768 or digest(image)!=data['image_sha256']:failures.append('Scan EEPROM '+name)
        if name.startswith('policy0/'):
            if data.get('binary_reset_resolution_late')!=0 or digest(ROOT/data['compiled_bench']['path'])!=data['compiled_bench']['sha256']:failures.append('Policy0 forcepoint provenance')
            policy_text=(ROOT/data['compiled_bench']['path']).read_text()
            if not all(s in policy_text for s in ['memory.raster.RESOLVE_LATE=0','memory.peripheral.RESOLVE_LATE=0']):failures.append('Unused reset policy parameters')
    data=read('system-scan-ideal-negative.json')
    negative=dict(data);negative['expected_rejection']='CPU column read before hardware settling'
    complete(negative,'scan bypass',True)
    model=read('native/ahc174-model-results.json')
    if len(model['runs'])!=2 or len(model['negative'])!=5:failures.append('AHC174 model boundary coverage')
    for row in model['runs']:complete(row,'AHC174 positive')
    for row in model['negative']:complete(row,'AHC174 negative',True)
    graph=read('native/schematic-check.json')
    if (graph['components'],graph['pins'],graph['no_connects'],graph['max_signal_input_loads'])!=(62,526,9,4):failures.append('Native graph')
    equivalence=read('native/equivalence-check.json')
    if not equivalence['same_pin_logic_except_package_models'] or len(equivalence['changes'])!=3:failures.append('Physical package substitution proof')
    erc=read('native/erc-summary.json')
    if erc['exit']!=5 or sum(erc['violation_counts'].values())!=135 or erc['erc_passed'] or erc['board_release']:failures.append('Partial ERC falsely approved/changed')
    inventory=read('load-inventory.json')
    if inventory['candidate_union_ic_count']!=456 or len(inventory['power_budget'])!=30 or inventory['global_board_integrated'] or any(x['board_icc_upper_bound_a'] is not None for x in inventory['power_budget']):failures.append('Current/BOM scope')
    for name in ['adapter-origin.json','system-adapter-origin.json','vector-origin.json']:
        for item in read(name)['files']:
            if digest(ROOT/item['path'])!=item['sha256']:failures.append('Changed transformation '+item['path'])
    for item in read('research/sources.json')['files']:
        if digest(ROOT/item['path'])!=item['sha256'] or digest(ROOT/item['extraction'])!=item['extraction_sha256']:failures.append('Datasheet/extraction')
    environment=read('environment.json')
    if not environment['collected_after_runs'] or len(environment['shared_rom_inputs'])!=4:failures.append('Supplementary environment scope')
    for item in environment['shared_rom_inputs']:
        if digest(ROOT/item['path'])!=item['sha256'] or not item['unchanged_from_baseline']:failures.append('Shared ROM '+item['path'])
    if (ROOT/'revisions/rev983/diagnostic.asm').exists():failures.append('Historical missing diagnostic status changed: review before updating claim')
    if '--check' in sys.argv:
        manifest=json.loads(MANIFEST.read_text())
        for item in manifest['files']:
            path=(ROOT/item['path']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or digest(path)!=item['sha256']:failures.append(item['path'])
        print(json.dumps({'checked':len(manifest['files']),'failures':failures,'production_released':False}));return int(bool(failures))
    if not failures:failures+=audit_history()
    if failures:print(json.dumps({'failures':failures}));return 1
    (OUT/'acceptance.json').write_text(json.dumps({'date':'2026-11-26','ideal_instruction_cases':6886,'selected_delayed_instruction_cases_per_scenario':1062,
        'delayed_state_cq_scenarios_ns':[10.5,1],'ideal_reset_cuts':4562,'delayed_reset_cuts':1692,'delayed_batches':7,
        'ideal_boot_retirements':132197,'full_program_timed_executed':False,'cpu_raw_scan_firmware_executed':True,
        'scan_binary_reset_policies_tested':[0,1],'cpu_key_event_firmware_implemented':False,'net18_power_domains_integrated':False,
        'partial_controller_erc_violations':135,'historical_diagnostic_asm_still_missing':True,'production_released':False},indent=2)+'\n')
    names=['.gitattributes','README.md','AGENTS.md','PROVENANCE.md','ROADMAP.md','DECISIONS.md','CHANGELOG.md','docs/engineering/NET19A.md','docs/engineering/VALIDATION_STATUS.md','docs/engineering/PRODUCTION_GATES.md','references/ti/sn74ahc174.pdf']
    names+=['tools/'+n+'.py' for n in ['make_keyboard_cpu','run_keyboard_cpu','run_keyboard_scan','build_system_access','make_system_cpu','run_system_cpu','run_system_scan','run_system_scan_policy0','prepare_system_vectors','run_system_vectors','run_system_safety_batches','check_system_access','check_system_access_erc','check_ahc174_limits','inventory_system_loads','record_system_environment','record_net19_manifest']]
    names+=[f'revisions/rev983/control_lane{i}.bin' for i in range(4)]
    files={ROOT/n for n in names}
    for folder in ['hardware/system_access','sim/net19a','firmware/net19a','verification/net19a']:
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl' and '__pycache__' not in p.parts)
    manifest={'iteration':'NET-19A','date':'2026-11-26','base_git_commit':BASE,'scope':'Native MMIO/keyboard/CPU digital integration, matched AHC174 state candidate and selected timing scenarios. Explicit failed intermediate fixtures, no global power/clock/load/PCB/physical signoff.',
              'files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'recorded':len(files),'bytes':sum(p.stat().st_size for p in files),'prior_snapshots':22,'failures':failures,'production_released':False}));return 0


if __name__=='__main__':raise SystemExit(main())
