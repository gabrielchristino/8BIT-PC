"""Resource-bounded persistent logs/state for a long foreground verification."""
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

def boot_id():return Path('/proc/sys/kernel/random/boot_id').read_text().strip()

def save_state(path,state):
    temporary=path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(state,indent=2)+'\n')
    temporary.replace(path)

def active(state):
    if state.get('status')!='running' or state.get('boot_id')!=boot_id():return False
    p=Path('/proc')/str(state.get('pid'))/'cmdline'
    try:return p.read_bytes().split(b'\0')[:-1]==[str(x).encode() for x in state['command']]
    except OSError:return False

def run_tracked(command,work,folder,phase,timeout,memory_mb,cpu_seconds,output_mb=8):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    stdout_path=folder/(phase+'.stdout.log');stderr_path=folder/(phase+'.stderr.log')
    state_path=folder/'run-state.json'
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(memory_mb*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_CPU,(cpu_seconds,)*2)
        resource.setrlimit(resource.RLIMIT_FSIZE,(output_mb*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    started=time.time();began=time.monotonic();expired=False
    state={'status':'starting','phase':phase,'command':list(map(str,command)),'cwd':str(work),'boot_id':boot_id(),
        'started_unix_seconds':started,'limits':{'memory_mb':memory_mb,'cpu_seconds':cpu_seconds,'wall_seconds':timeout,'output_mb_per_file':output_mb},
        'stdout_path':str(stdout_path),'stderr_path':str(stderr_path),'simulation_passed':False}
    save_state(state_path,state)
    with stdout_path.open('wb') as stdout,stderr_path.open('wb') as stderr:
        process=subprocess.Popen(command,cwd=work,stdout=stdout,stderr=stderr,preexec_fn=limits,start_new_session=True)
        state.update(status='running',pid=process.pid,process_group=process.pid)
        save_state(state_path,state)
        try:exit_code=process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            expired=True
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            exit_code=process.wait()
    state.update(status='process_finished',exit=exit_code,wall_timeout=expired,seconds=round(time.monotonic()-began,3),
        stdout_sha256=hashlib.sha256(stdout_path.read_bytes()).hexdigest(),stderr_sha256=hashlib.sha256(stderr_path.read_bytes()).hexdigest())
    save_state(state_path,state)
    (folder/(phase+'-run.json')).write_text(json.dumps(state,indent=2)+'\n')
    return {'command':list(map(str,command)),'exit':exit_code,'wall_timeout':expired,'seconds':state['seconds'],
        'stdout':stdout_path.read_text(errors='replace'),'stderr':stderr_path.read_text(errors='replace'),'limits':state['limits']}
