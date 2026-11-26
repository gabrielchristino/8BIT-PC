"""Stage one audited engineering manifest and compare real index blob bytes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def git(*args,**kwargs):return subprocess.check_output(['git',*args],cwd=ROOT,**kwargs)


def main():
    assert len(sys.argv)==2,'Pass the reviewed manifest path'
    path=(ROOT/sys.argv[1]).resolve()
    assert path.is_relative_to(ROOT) and path.name=='manifest.json'
    data=json.loads(path.read_text())
    assert git('rev-parse','HEAD').decode().strip()==data['base_git_commit']
    records={r['path']:r['sha256'] for r in data['files']}
    records[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    for name,expected in records.items():
        item=(ROOT/name).resolve()
        assert item.is_relative_to(ROOT) and hashlib.sha256(item.read_bytes()).hexdigest()==expected,name
    outsiders=[]
    for row in git('status','--porcelain=v1','-z','--untracked-files=all').split(b'\0'):
        if not row:continue
        assert row[:2] not in (b'R ',b' R',b'C ',b' C'),'Unexpected rename/copy'
        name=row[3:].decode('utf-8')
        if name not in records:outsiders.append(name)
    assert not outsiders,'Unrelated changes left untouched: '+repr(outsiders)
    subprocess.run(['git','add','--pathspec-from-file=-','--pathspec-file-nul'],
                   input=b'\0'.join(n.encode() for n in records)+b'\0',cwd=ROOT,check=True)
    staged=set(git('diff','--cached','--name-only','-z').decode().strip('\0').split('\0'))
    assert staged<=records.keys(),'Unexpected staged path'
    payload=git('cat-file','--batch',input=''.join(':'+n+'\n' for n in records).encode())
    offset=0
    for name,expected in records.items():
        end=payload.index(b'\n',offset)
        header=payload[offset:end].split()
        assert len(header)==3 and header[1]==b'blob',name
        size=int(header[2]);start=end+1
        assert hashlib.sha256(payload[start:start+size]).hexdigest()==expected,'Index bytes differ: '+name
        assert payload[start+size:start+size+1]==b'\n'
        offset=start+size+1
    assert offset==len(payload)
    subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
    print(json.dumps({'staged_paths':len(staged),'verified_index_blobs':len(records),
                      'all_index_sha256_match_manifest_and_working_bytes':True,'unrelated_changes':outsiders}))


if __name__=='__main__':main()
