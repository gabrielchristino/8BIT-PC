"""Audit functional results AND preserve four known reset pulse rejections."""
import hashlib
import inspect
import json
from pathlib import Path
import re
import subprocess
import sys
import record_net14a_manifest as original

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net24'
BASE='c54226afed52e04c787b91c65dc29cfacf8f661e'
MANIFEST=OUT/'manifest.json'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
exec(inspect.getsource(original.audit_history).replace('verification/net13/','verification/net23/'),globals())


def main():
    failures=[]

    def hashed(item):
        path=(ROOT/item['path']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or digest(path)!=item['sha256']:
            failures.append('Changed source '+item['path'])

    def read(name):
        path=OUT/name
        if not path.is_file():
            failures.append('Missing completed report '+name);return {}
        data=json.loads(path.read_text())
        if data.get('failures'):failures.append('Failed collection/report '+name)
        for item in data.get('sources',[]):hashed(item)
        return data

    def complete(row,label,negative=None):
        result=row.get('execution',{});output=result.get('stdout','')
        if row.get('compile',{}).get('exit')!=0 or row.get('compile',{}).get('stderr') or not row.get('passed',True):
            failures.append('Compile/acceptance '+label)
        if negative:
            if result.get('exit') in (None,0) or negative not in output:failures.append('Expected rejection not detected '+label)
        elif result.get('exit')!=0 or 'RESULT ' not in output or 'failures=0' not in output:
            failures.append('Incomplete execution '+label)
        return output

    graph=read('native/schematic-check.json')
    if tuple(graph.get(k) for k in ['components','pins','no_connects','max_signal_input_loads'])!=(62,526,9,4):failures.append('Native graph counts')
    topology=read('topology.json')
    if topology.get('ics')!=31 or len(topology.get('changed_pins',[]))!=2 or [r['input_count'] for r in topology.get('clock_groups',[])]!=[3,3,3]:
        failures.append('Pin delta/clock groups')
    if topology.get('backend_source',{}).get('steady_duty')!=.5 or topology.get('first_stage_metastability_modeled') is not False:
        failures.append('Topology/model scope')
    baseline=read('request-skew-probe.json')
    if len(baseline.get('runs',[]))!=5 or len(baseline.get('investigations',[]))!=1:failures.append('Baseline request probe coverage')
    for row in baseline.get('runs',[]):complete(row,'baseline request')
    for row in baseline.get('investigations',[]):complete(row,'split clock counterexample','DFF data setup violation')
    common=read('common-request-probe.json')
    if len(common.get('runs',[]))!=32 or len(common.get('negative',[]))!=1:failures.append('Common request coverage')
    for row in common.get('runs',[]):complete(row,'common request')
    for row in common.get('negative',[]):complete(row,'reverted clock','DFF data setup violation')

    # These are OPEN model-constraint failures. Collection success must never
    # silently classify their exit1 results as a passing circuit scenario.
    pulse=read('reset-pulse-probe.json')
    if len(pulse.get('baseline',[]))!=8 or len(pulse.get('investigations',[]))!=8:failures.append('Reset pulse coverage')
    for row in pulse.get('baseline',[]):complete(row,'symmetric pulse')
    rejected=[]
    for row in pulse.get('investigations',[]):
        if row.get('pulse_constraint_rejected'):
            output=complete(row,'KNOWN OPEN pulse rejection','DFF clock pulse violation measured_ns=7.722 required_ns=20 clr_n=1')
            if row.get('completed') is not False or not row.get('investigation_recorded') or 'bank_memory_n=1' not in output:
                failures.append('Open pulse failure hidden or unrecorded')
            rejected.append(row['raw_after_backend_fall_ns'])
        else:complete(row,'asymmetric pulse completion')
    if rejected!=[30,39,40,60] or pulse.get('reset_transition_pulse_envelope_qualified') is not False:
        failures.append('Known pulse failures missing/promoted')

    for name in ['actual-cpu-write-reset.json','frequency-corners/actual-cpu-write-reset.json']:
        data=read(name)
        if [r['policy'] for r in data.get('runs',[])]!=[0,1]:failures.append('Actual CPU policies '+name)
        for row in data.get('runs',[]):
            output=complete(row,'actual CPU '+name);deadline=re.search(r'max_we_inhibit_ns=([\d.]+)',output)
            if 'actual_cpu_write_cuts=2 restarted_scans=2' not in output or 'fixture_defaults=0' not in output or not deadline or float(deadline[1])>100:
                failures.append('Actual CPU completion/deadline '+name)
    for name,bench,marker in [('verified-cpu-ideal.json','verified-tb_rtl_cpu-ideal.sv','instruction_cases=6886 transactions=13406'),
                              ('verified-cpu-timed-quick.json','verified-tb_rtl_cpu-timed.sv','instruction_cases=1062 transactions=1821'),
                              ('verified-cpu-early-timed-quick.json','verified-tb_rtl_cpu-early-timed.sv','instruction_cases=1062 transactions=1821')]:
        data=read('vectors/'+name)
        if len(data.get('runs',[]))!=1:failures.append('Instruction coverage '+name)
        for row in data.get('runs',[]):
            if marker not in complete(row,name):failures.append('Instruction completion '+name)
        if data and digest(OUT/'vectors'/bench)!=data.get('adapted_bench_sha256'):failures.append('Compiled instruction bench '+name)
    program=read('program/system-program-ideal.json')
    if len(program.get('runs',[]))!=1:failures.append('Full program coverage')
    for row in program.get('runs',[]):
        output=complete(row,'full boot/frame')
        if 'retirements=132197 transactions=232576' not in output or 'frame_pixels=76800' not in output or 'fixture_defaults=0' not in output or not row.get('frame_matches_reference'):
            failures.append('Boot/SRAM/frame completion')
    if program and digest(OUT/'program/system-tb_rtl_program-ideal.sv')!=program.get('adapted_bench_sha256'):
        failures.append('Compiled program bench')
    for item in read('cpu-adapter-origin.json').get('files',[]):hashed(item)
    erc=read('native/erc-summary.json')
    if erc.get('exit')!=5 or erc.get('erc_passed') is not False or sum(erc.get('violation_counts',{}).values())!=135:
        failures.append('Partial ERC scope')
    reference=read('research/reference.json')
    if reference.get('clock_q_min_ns','missing') is not None or reference.get('clock_pulse_min_ns')!=20:failures.append('HC74 limits misread')
    environment=read('environment.json')
    if environment.get('source'):hashed(environment['source'])
    if len(environment.get('versions',[]))!=5 or len(environment.get('shared_rom_inputs',[]))!=4:failures.append('Environment')
    for item in environment.get('shared_rom_inputs',[]):
        hashed(item)
        if not item['unchanged_from_baseline']:failures.append('ROM changed')
    if failures:
        print(json.dumps({'failures':failures,'known_open_reset_pulse_cases':rejected,'production_released':False}));return 1
    if '--check' in sys.argv:
        data=json.loads(MANIFEST.read_text())
        for item in data['files']:hashed(item)
        print(json.dumps({'checked':len(data['files']),'failures':failures,'known_open_reset_pulse_cases':rejected}));return int(bool(failures))
    failures+=audit_history()
    if failures:
        print(json.dumps({'failures':failures}));return 1
    (OUT/'acceptance.json').write_text(json.dumps({'date':'2026-11-26','functional_regressions_passed':True,
        'ics':31,'changed_clock_pins':2,'common_request_selected_cases':32,'reverted_clock_rejection_detected':True,
        'instruction_cases_ideal':6886,'instruction_cases_per_timed_scenario':1062,'timed_controller_cq_scenarios':2,
        'actual_cpu_write_cuts':8,'actual_cpu_restarted_scans':8,'selected_max_we_inhibit_ns':84,
        'full_ideal_boot_retirements':132197,'full_ideal_boot_pixels':76800,'full_ideal_boot_sram_seeded':False,
        'symmetric_reset_pulse_cases_completed':8,'asymmetric_reset_pulse_cases_completed':4,
        'known_open_reset_pulse_constraint_rejections':4,'known_rejected_offsets_ns':rejected,
        'known_rejected_clock_pulse_ns':7.722,'required_clock_pulse_ns':20,
        'global_reset_pulse_qualified':False,'first_stage_mtbf_qualified':False,'full_timed_program_executed':False,
        'partial_erc_violations':135,'clock_drain_study_implemented':False,'production_released':False},indent=2)+'\n')
    names=['.gitattributes','README.md','AGENTS.md','PROVENANCE.md','ROADMAP.md','DECISIONS.md','CHANGELOG.md',
           'docs/engineering/NET24.md','docs/engineering/CLOCK_DRAIN_STUDY.md','docs/engineering/VALIDATION_STATUS.md','docs/engineering/PRODUCTION_GATES.md']
    names+=git('ls-files','--others','--exclude-standard','tools').decode().splitlines()
    names+=git('diff','--name-only',BASE,'--','tools').decode().splitlines()
    files={ROOT/n for n in names}
    for folder in ['hardware/common_request','sim/net24','verification/net24']:
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl' and '__pycache__' not in p.parts)
    data={'iteration':'NET24','date':'2026-11-26','base_git_commit':BASE,
          'scope':'Two native request clock pin changes, selected functional probes/CPU/boot pass. Four asymmetric reset pulse scenarios remain rejected7.722ns/20ns; no global timing/MTBF/analog/fabrication qualification. Clock drain proposal unimplemented.',
          'known_open_reset_pulse_constraint_rejections':4,
          'files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'recorded':len(files),'prior_snapshots':27,'failures':failures,
                      'known_open_reset_pulse_constraint_rejections':4,'production_released':False}));return 0


if __name__=='__main__':raise SystemExit(main())
