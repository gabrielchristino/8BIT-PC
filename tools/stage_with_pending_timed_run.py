"""Stage one manifest while leaving one explicitly identified live run untouched."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from audit_pending_timed_run import audit

ROOT=Path(__file__).resolve().parents[1]
PENDING='verification/net27/full-timed/attempt-001/'

def git(*args,**kwargs):return subprocess.check_output(['git',*args],cwd=ROOT,**kwargs)

def main():
    assert len(sys.argv)==2
    path=(ROOT/sys.argv[1]).resolve()
    assert path.is_relative_to(ROOT) and path.name=='manifest.json'
    report=json.loads(path.read_text())
    assert git('rev-parse','HEAD').decode().strip()==report['base_git_commit']
    integrity=audit()
    assert integrity['snapshot_hashes_match'] and not integrity['simulation_passed']
    assert report['excluded_pending_run_prefix']==PENDING
    records={r['path']:r['sha256'] for r in report['files']}
    records[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    assert not any(name.startswith(PENDING) for name in records)
    for name,digest in records.items():
        item=(ROOT/name).resolve()
        assert item.is_relative_to(ROOT) and hashlib.sha256(item.read_bytes()).hexdigest()==digest,name
    pending=[];outsiders=[]
    for row in git('status','--porcelain=v1','-z','--untracked-files=all').split(b'\0'):
        if not row:continue
        assert row[:2] not in (b'R ',b' R',b'C ',b' C')
        name=row[3:].decode()
        if name.startswith(PENDING):
            assert row[:2]==b'??','A published run artifact was modified'
            pending.append(name)
        elif name not in records:outsiders.append(name)
    assert pending and not outsiders,outsiders
    subprocess.run(['git','add','--pathspec-from-file=-','--pathspec-file-nul'],cwd=ROOT,
        input=b'\0'.join(name.encode() for name in records)+b'\0',check=True)
    staged=set(git('diff','--cached','--name-only','-z').decode().strip('\0').split('\0'))
    assert staged<=records.keys()
    payload=git('cat-file','--batch',input=''.join(':'+name+'\n' for name in records).encode())
    offset=0
    for name,digest in records.items():
        end=payload.index(b'\n',offset);header=payload[offset:end].split()
        assert len(header)==3 and header[1]==b'blob',name
        size=int(header[2]);start=end+1
        assert hashlib.sha256(payload[start:start+size]).hexdigest()==digest,name
        assert payload[start+size:start+size+1]==b'\n'
        offset=start+size+1
    assert offset==len(payload)
    subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
    print(json.dumps({'staged_paths':len(staged),'index_blobs_verified':len(records),
        'excluded_pending_files':len(pending),'excluded_prefix':PENDING,
        'pending_inputs_unchanged':True,'unrelated_changes':outsiders}))

if __name__=='__main__':main()
