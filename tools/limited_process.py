"""Bound optional simulator evaluations without changing historical run helpers."""
import os
from pathlib import Path
import resource
import signal
import subprocess
import tempfile
import time

def run_limited(command,work,timeout=45,memory_mb=768,cpu_seconds=20,output_mb=2):
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(memory_mb*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_CPU,(cpu_seconds,)*2)
        resource.setrlimit(resource.RLIMIT_FSIZE,(output_mb*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='isa1-engine-output-') as temp:
        out=Path(temp)/'stdout';err=Path(temp)/'stderr';expired=False
        with out.open('wb') as stdout,err.open('wb') as stderr:
            process=subprocess.Popen(command,cwd=work,stdout=stdout,stderr=stderr,start_new_session=True,preexec_fn=limits)
            try:exit_code=process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                expired=True
                try:os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                exit_code=process.wait()
        return {'command':list(command),'exit':exit_code,'wall_timeout':expired,'seconds':round(time.monotonic()-start,3),
            'limits':{'memory_mb':memory_mb,'cpu_seconds':cpu_seconds,'output_mb_per_file':output_mb,'wall_seconds':timeout},
            'stdout':out.read_text(errors='replace'),'stderr':err.read_text(errors='replace')}
