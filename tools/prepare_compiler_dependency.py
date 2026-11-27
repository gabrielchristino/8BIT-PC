"""Fetch/extract a build header package into a local dependency directory."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net26/tool-research'
DEP=Path('/home/gabri/.local/opt/isa1-cvc-deps')

def main():
    DEP.mkdir(parents=True,exist_ok=True)
    cmd=['apt-get','download','zlib1g-dev']
    r=subprocess.run(cmd,cwd=DEP,capture_output=True,text=True,timeout=180)
    report={'date':'2026-11-26','scope':'Build dependency extracted locally; no system package installation or project license/access change.',
        'download':{'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},'packages':[]}
    if r.returncode==0:
        packages=list(DEP.glob('zlib1g-dev_*.deb'));assert packages
        for p in packages:
            meta=subprocess.check_output(['dpkg-deb','-f',str(p),'Package','Version','Architecture'],text=True)
            command=['dpkg-deb','-x',str(p),str(DEP/'root')]
            result=subprocess.run(command,capture_output=True,text=True,timeout=30)
            report['packages'].append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'metadata':meta,'extract':{'command':command,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr}})
    (OUT/'cvc-dependency.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
    return r.returncode

if __name__=='__main__':raise SystemExit(main())
