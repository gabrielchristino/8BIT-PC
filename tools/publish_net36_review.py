"""Publish only the audited NET36 manifest, leaving the NET30 attempt untracked."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def command(*args, input=None, timeout=120):
    result=subprocess.run(['git',*args],cwd=ROOT,input=input,capture_output=True,timeout=timeout)
    assert result.returncode==0,(args,result.stdout.decode(errors='replace'),result.stderr.decode(errors='replace'))
    return result.stdout


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--publish',action='store_true')
    args=parser.parse_args()
    manifest_path=ROOT/'verification/net36/manifest.json'
    manifest=json.loads(manifest_path.read_text())
    assert command('rev-parse','HEAD').decode().strip()==manifest['base_commit']
    assert manifest['net27_accepted'] and not manifest['net30_accepted'] and not manifest['production_released']
    pending=manifest['excluded_active_prefix']
    records={r['path']:r['sha256'] for r in manifest['files']}
    records[manifest_path.relative_to(ROOT).as_posix()]=hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    assert not any(name.startswith(pending) for name in records)
    for name,sha in records.items():
        path=(ROOT/name).resolve()
        assert path.is_relative_to(ROOT) and hashlib.sha256(path.read_bytes()).hexdigest()==sha,name
    outsiders=[]
    for row in command('status','--porcelain=v1','-z','--untracked-files=all').split(b'\0'):
        if not row:continue
        assert row[:2] not in [b'R ',b' R',b'C ',b' C']
        name=row[3:].decode()
        if name.startswith(pending):
            assert row[:2]==b'??',name
        elif name not in records:
            outsiders.append(name)
    assert not outsiders,outsiders
    # Fetch/read the live remote tree before staging or publishing.
    command('fetch','origin','main',timeout=120)
    remote_before=command('rev-parse','origin/main').decode().strip()
    assert remote_before==manifest['base_commit'],'Remote advanced; inspect before proceeding'
    tree=command('ls-tree','-r','origin/main')
    command('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join(n.encode() for n in records)+b'\0')
    staged=set(command('diff','--cached','--name-only','-z').decode().strip('\0').split('\0'))
    assert staged==records.keys(),(len(staged),len(records))
    # Compare index blob bytes, not merely working-tree files or normalized text.
    payload=command('cat-file','--batch',input=''.join(':'+n+'\n' for n in records).encode())
    offset=0
    for name,sha in records.items():
        end=payload.index(b'\n',offset)
        header=payload[offset:end].split()
        assert len(header)==3 and header[1]==b'blob',name
        size=int(header[2]);start=end+1
        assert hashlib.sha256(payload[start:start+size]).hexdigest()==sha,name
        assert payload[start+size:start+size+1]==b'\n'
        offset=start+size+1
    assert offset==len(payload)
    command('diff','--cached','--check')
    result=dict(staged=len(staged),index_blobs_verified=len(records),excluded_active_prefix=pending,
        remote_before=remote_before,remote_tree_sha256=hashlib.sha256(tree).hexdigest(),
        git_version=command('--version').decode().strip(),force_push=False)
    if args.publish:
        result['commit_output']=command('commit','-m','NET36 audit completed NET27 boot and review sync hold-up requirements').decode()
        commit=command('rev-parse','HEAD').decode().strip()
        command('push','origin','HEAD:main',timeout=180)
        remote=command('ls-remote','origin','refs/heads/main',timeout=120).decode().split()[0]
        assert remote==commit,(remote,commit)
        result.update(published_commit=commit,remote_verified=True)
        # Receipt is local post-commit evidence; no self-referential manifest.
        (ROOT/'verification/net36/publication-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
