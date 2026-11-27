"""Evaluate a separately installed CVC source build; no ISA-1 license change."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/home/gabri/.local/opt/isa1-cvc-source')
EXPECTED='1c5e043ec33ef6f1fdbf38565501c944893a83cf'
OUT=ROOT/'verification/net26/tool-research'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip();assert commit==EXPECTED
    command=['make','-j2','cvc64','CC=gcc -std=gnu99 -MMD -fcommon',
        'INCS=-I../pli_incs -I/home/gabri/.local/opt/isa1-cvc-deps/root/usr/include',
        'LIBS=-L/home/gabri/.local/opt/isa1-cvc-deps/root/usr/lib/x86_64-linux-gnu -lm -ldl -lpthread -lz -lc']
    began=time.monotonic();r=subprocess.run(command,cwd=SOURCE/'src',capture_output=True,text=True,timeout=900)
    exe=SOURCE/'build64/cvc64'
    refs=['README.md','INSTALL','OSS-CVC-MODIFIED-ARTISTIC-LIC.TXT','src/Makefile','CHANGES.md']
    report={'date':'2026-11-26','source_url':'https://github.com/cambridgehackers/open-src-cvc','source_commit':commit,
       'purpose':'Internal simulator evaluation in separate dependency directory; engine/runtime not redistributed in ISA-1 repository, project access/license unchanged.',
       'license_source':'https://github.com/cambridgehackers/open-src-cvc/blob/master/OSS-CVC-MODIFIED-ARTISTIC-LIC.TXT',
       'build':{'command':command,'exit':r.returncode,'seconds':round(time.monotonic()-began,3),'stdout':r.stdout,'stderr':r.stderr},
       'source_files':[{'path':n,'sha256':hashlib.sha256((SOURCE/n).read_bytes()).hexdigest()} for n in refs],
       'evaluation_source':{'path':'tools/evaluate_compiled_simulator.py','sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
       'build_completed':r.returncode==0 and exe.is_file(),'simulation_equivalence_approved':False,'production_released':False}
    if exe.is_file():
        report['executable']={'path':str(exe),'sha256':hashlib.sha256(exe.read_bytes()).hexdigest()}
        help_result=subprocess.run([str(exe),'-h'],cwd=OUT,capture_output=True,text=True,timeout=30)
        report['help']={'exit':help_result.returncode,'stdout':help_result.stdout,'stderr':help_result.stderr}
    (OUT/'cvc-build.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'build_completed':report['build_completed'],'seconds':report['build']['seconds'],'exit':r.returncode,
        'tail':r.stderr[-2400:] if r.returncode else '', 'simulation_equivalence_approved':False}))
    return r.returncode

if __name__=='__main__':raise SystemExit(main())
