"""Use existing index-byte audit with explicitly enumerated pending outputs."""
import inspect
import json
from pathlib import Path
import sys
import stage_with_pending_timed_run as original

PENDING=('verification/net27/full-timed/attempt-001/','verification/net30/jobs/',
    'verification/net30/program/','verification/net30/native-frame-results.json')

if __name__=='__main__':
    assert len(sys.argv)==2
    path=original.ROOT/sys.argv[1]
    assert tuple(json.loads(path.read_text())['excluded_pending_run_prefix'])==PENDING
    source=inspect.getsource(original.main)
    old="assert report['excluded_pending_run_prefix']==PENDING"
    assert source.count(old)==1
    source=source.replace(old,"assert tuple(report['excluded_pending_run_prefix'])==PENDING")
    env=dict(original.__dict__);env['PENDING']=PENDING
    exec(source,env);env['main']()
