"""Read-only integrity snapshot; never certify an unfinished simulation."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def audit():
    attempt=ROOT/'verification/net27/full-timed/attempt-001'
    origin=json.loads((attempt/'run-origin.json').read_text())
    records=json.loads((attempt/'compiler-inputs.json').read_text())
    checked=[]
    for row in origin['sources']:
        assert digest(ROOT/row['path'])==row['sha256'],row
        checked.append(row['path'])
    for row in records:
        snapshot=ROOT/row['snapshot']
        assert digest(snapshot)==row['sha256'],row
        original=row['original']
        prefix='/mnt/c/Users/gabri/projetos/isa1/'
        if original.startswith(prefix):
            relative=original[len(prefix):]
            assert digest(ROOT/relative)==row['sha256'],relative
            checked.append(relative)
    compile_result=json.loads((attempt/'compile-run.json').read_text())
    assert compile_result['exit']==0
    assert (attempt/'compile.stderr.log').read_bytes()==b''
    state=json.loads((attempt/'run-state.json').read_text())
    log=(attempt/'simulation.stdout.log').read_text()
    result={'date':'2026-11-26','scope':'Read-only integrity checkpoint during a pending full timed run. No final circuit pass asserted.',
        'run_source_commit':origin['run_source_commit'],'circuit_base_commit':origin['circuit_base_commit'],
        'source_paths_checked':checked,'snapshot_count':len(records),'snapshot_hashes_match':True,
        'state_at_read':state,'last_progress_at_read':log.splitlines()[-1] if log else None,
        'simulation_passed':False,'production_released':False,
        'tool_sha256':digest(Path(__file__))}
    return result

if __name__=='__main__':
    out=ROOT/'verification/net28/pending-run-integrity.json'
    result=audit();out.write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    print(json.dumps({'sources':len(result['source_paths_checked']),'snapshots':result['snapshot_count'],
        'pending_status':result['state_at_read']['status'],'last_progress':result['last_progress_at_read'],'simulation_passed':False}))
