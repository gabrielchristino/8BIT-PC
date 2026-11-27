"""Reuse the index-byte audit with exactly two identified pending attempts."""
import inspect
import json
import sys
import stage_with_pending_timed_run as original

PENDING=('verification/net27/full-timed/attempt-001/','verification/net30/full-timed/attempt-001/')

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
