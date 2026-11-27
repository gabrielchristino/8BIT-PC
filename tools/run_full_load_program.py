# GENERATED separate NET30 complete timed candidate; ancestors unchanged.
"""Run the complete NET30 candidate program with nominal clock periods and selected delays.

Long bounded Icarus run, not a global analog/PVT or production qualification.
An existing live attempt is reported rather than duplicated; interrupted
simulation processes cannot be resumed internally and require a new attempt.
"""
import hashlib
import inspect
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import run_system_cpu as base
import run_distributed_load_program as template
from run_request_skew_probe import once
from tracked_simulation import active,run_tracked,save_state

ROOT=Path(__file__).resolve().parents[1]
CIRCUIT_BASE='16a82e4866ac9c791dfae0e162c2f887842b1f52'
OUT=ROOT/'verification/net30/full-timed'
ATTEMPT=None
SNAPSHOTS=[]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def execute(command,work,timeout=1200):
    command=list(command)
    if command[0]=='iverilog':
        for i,arg in enumerate(command):
            p=Path(arg)
            if p.suffix=='.sv' and p.is_file():
                relative=p.relative_to(ROOT) if p.is_relative_to(ROOT) else Path('generated-bench.sv')
                dest=ATTEMPT/'compiler-inputs'/relative;dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(p,dest)
                SNAPSHOTS.append({'original':str(p),'snapshot':dest.relative_to(ROOT).as_posix(),'sha256':digest(dest)})
                if p.name=='tb_rtl_program.sv':
                    text=dest.read_text()
                    assert 'CPU_HALF=5000' in text and 'VIDEO_HALF=19.860973' in text
                    assert 'CPU_STARTUP_NS=10000000' in text and 'MASTER_STARTUP_NS=10000000' in text
                    assert '.FIXTURE_DEFAULTS(0)' in text and '.TIMED(1)' in text
                command[i]=str(dest)
        for p in Path(work).glob('*.hex'):
            dest=ATTEMPT/'input-images'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
            SNAPSHOTS.append({'original':str(p),'snapshot':dest.relative_to(ROOT).as_posix(),'sha256':digest(dest)})
        (ATTEMPT/'compiler-inputs.json').write_text(json.dumps(SNAPSHOTS,indent=2)+'\n')
        return run_tracked(command,work,ATTEMPT,'compile',180,1024,120)
    if command[0]=='vvp':
        result=run_tracked(command,work,ATTEMPT,'simulation',86400,1024,72000)
        frame=Path(work)/'frame.ppm'
        if frame.is_file():shutil.copyfile(frame,ATTEMPT/'observed-frame.ppm')
        return result
    raise RuntimeError('Unexpected simulator command '+str(command))

def choose_attempt():
    OUT.mkdir(parents=True,exist_ok=True)
    attempts=sorted(OUT.glob('attempt-*'))
    for p in reversed(attempts):
        state=p/'run-state.json'
        if state.is_file():
            d=json.loads(state.read_text())
            if active(d):
                print(json.dumps({'status':'already_running','path':str(p),'pid':d['pid'],'simulation_passed':False}));return None
            if d.get('status')=='complete' and d.get('simulation_passed'):
                print(json.dumps({'status':'already_completed','path':str(p),'simulation_passed':True}));return None
    p=OUT/f'attempt-{len(attempts)+1:03d}';p.mkdir();return p

def main():
    global ATTEMPT
    ATTEMPT=choose_attempt()
    if ATTEMPT is None:return 0
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    origin={'date_started':'2026-11-27','circuit_base_commit':CIRCUIT_BASE,'run_source_commit':commit,
        'engine':'Icarus','scope':'Full timed program at nominal100kHz CPU/25.175MHz master,10ms source startup, selected digital chip delays, initially unknown SRAM. Qualified oscillator VDD held valid. Binary warm/local reset boundary, not analog/PVT/jitter/MTBF/POR/PCB approval.',
        'transformation':'Adapt previously verified ideal program runner to timed mode and nominal source startup; add read-only retirement progress every128instructions. Keep original architectural/WAIT/COMMIT/VRAM/frame assertions and simulated watchdog. Compiler inputs/images snapshotted; observed PPM retained.',
        'sources':[{'path':n,'sha256':digest(ROOT/n)} for n in ['tools/run_full_load_program.py','tools/tracked_simulation.py','tools/run_distributed_load_program.py','tools/run_system_cpu.py']],
        'limits':{'simulation_memory_mb':1024,'simulation_cpu_seconds':72000,'simulation_wall_seconds':86400,'output_mb_per_file':8},
        'simulation_passed':False}
    (ATTEMPT/'run-origin.json').write_text(json.dumps(origin,indent=2)+'\n')
    # Only the image filename is changed in the inherited in-process helper;
    # model, assertion and reference generation code remain on disk unchanged.
    helper=once(inspect.getsource(base.main),"OUT / 'frame-system-ideal.png'","OUT / 'frame-system-timed.png'")
    (ATTEMPT/'adapted-system-main.py').write_text(helper)
    exec(helper,base.__dict__)
    base.run=execute
    source=inspect.getsource(template.main)
    source=once(source,"folder = ROOT / 'verification/net30/program'",'folder = ATTEMPT')
    source=once(source,"sys.argv = [sys.argv[0], '--bench', 'program']","sys.argv = [sys.argv[0], '--bench', 'program', '--timed']")
    source=once(source,'memory.reset_domains.CPU_STARTUP_NS=100, memory.reset_domains.MASTER_STARTUP_NS=100;',
        'memory.reset_domains.CPU_STARTUP_NS=10000000, memory.reset_domains.MASTER_STARTUP_NS=10000000;')
    source=once(source,'        return text','''        progress="""
 integer next_progress=128;
 always @(posedge clk)begin
   #2000;
   if(n>=next_progress)begin
     $display("PROGRESS retired=%0d transactions=%0d simulated_ns=%0.3f PC=%h",n,transactions,$realtime,pc);
     $fflush();next_progress=next_progress+128;
   end
 end
"""
        text=once(text,'endmodule',progress+'endmodule')
        return text''')
    # The inherited wrapper otherwise replaces base.run with its1800s helper.
    old='''    original_run = base.run
    def run(command, work, timeout=1200):
        return original_run(command, work, timeout=1800 if command[0]=='vvp' else timeout)
    base.run = run'''
    source=once(source,old,'    base.run = execute')
    source=source.replace('system-program-ideal.json','system-program-timed.json')
    source=source.replace('Full ideal boot/frame through native common-request controller and configured source outputs with scaled periods/startup, initially unknown SRAM. No analog oscillator, jitter/POR/MTBF/PVT or timed full program qualification.',origin['scope'])
    source=source.replace("'tools/run_distributed_load_program.py'","'tools/run_distributed_load_program.py', 'tools/run_full_load_program.py', 'tools/tracked_simulation.py'")
    (ATTEMPT/'adapted-program-runner.py').write_text(source)
    env=dict(globals());exec(source,env);result=env['main']()
    report_path=ATTEMPT/'system-program-timed.json';report=json.loads(report_path.read_text())
    execution=report['runs'][0].get('execution',{})
    output=execution.get('stdout','')
    expected={'retirements':132197,'transactions':232576,'vram_transactions':32771,'frame_pixels':76800}
    matches=re.findall(r'^RESULT (.*)$',output,re.M)
    fields=dict(re.findall(r'(\w+)=(\d+)',matches[0])) if len(matches)==1 else {}
    exact_counts=all(fields.get(k)==str(v) for k,v in expected.items())
    memory_checks=bool(re.search(r'MEMORY_MODEL ram_valid_writes=\d+ vram_valid_writes=\d+ ram_aborts=0 vram_aborts=0 fixture_defaults=0',output))
    if not exact_counts or not memory_checks:
        report['failures'].append('complete-counts-or-unseeded-memory-check')
        result=1
    report.update(circuit_base_commit=CIRCUIT_BASE,run_source_commit=commit,source_snapshots=SNAPSHOTS,
        observed_frame_sha256=digest(ATTEMPT/'observed-frame.ppm') if (ATTEMPT/'observed-frame.ppm').is_file() else None,
        full_timed_program=True,exact_counts_verified=exact_counts,unseeded_no_aborts_verified=memory_checks,production_released=False)
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    state=json.loads((ATTEMPT/'run-state.json').read_text())
    state.update(status='complete',simulation_passed=not report['failures'] and all(r['passed'] for r in report['runs']),report=report_path.relative_to(ROOT).as_posix())
    save_state(ATTEMPT/'run-state.json',state)
    return result

if __name__=='__main__':raise SystemExit(main())
