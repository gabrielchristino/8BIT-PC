"""Exercise real subprocess limits and live-attempt detection, not HDL signoff."""
import hashlib
import json
from pathlib import Path
import signal
import sys
import tempfile
import threading
import time
from tracked_simulation import active,run_tracked

ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'verification/net27/preparation'
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    with tempfile.TemporaryDirectory(prefix='isa1-limit-check-') as tmp:
        work=Path(tmp)
        def check(name,code,predicate,wall=10,cpu=5):
            folder=out/name
            result=run_tracked([sys.executable,'-c',code],work,folder,name,wall,128,cpu,1)
            passed=predicate(result)
            rows.append({'case':name,'passed':passed,'result':result})
            assert passed,name
        check('normal',"print('RESULT helper=1')",lambda r:r['exit']==0 and r['stdout']=='RESULT helper=1\n')
        check('memory',"a=bytearray(512*1024**2)",lambda r:r['exit']!=0 and 'MemoryError' in r['stderr'])
        check('output',"import os\nwhile True: os.write(1,b'x'*65536)",lambda r:r['exit']!=0 and (out/'output/output.stdout.log').stat().st_size<=1024**2)
        check('cpu',"while True: pass",lambda r:r['exit'] in (-signal.SIGKILL,-signal.SIGXCPU),cpu=1)
        thread=threading.Thread(target=lambda:check('wall',"import time;time.sleep(30)",lambda r:r['wall_timeout'] and r['exit']==-signal.SIGKILL,wall=2))
        thread.start()
        live=False
        for _ in range(50):
            p=out/'wall/run-state.json'
            if p.exists():
                state=json.loads(p.read_text())
                if active(state):
                    live=True
                    wrong=dict(state,boot_id='different-boot')
                    assert not active(wrong)
                    break
            time.sleep(.02)
        thread.join()
        assert live and not active(json.loads((out/'wall/run-state.json').read_text()))
    record={'date':'2026-11-26','scope':'Process runner verification only; full timed ISA-1 program not executed by this check.',
        'python':sys.version,'live_detection_and_finished_rejection':True,'runs':rows,
        'sources':[{'path':name,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()} for name in ['tools/check_tracked_simulation.py','tools/tracked_simulation.py','tools/run_full_timed_program.py']],
        'passed':len(rows)==5 and all(r['passed'] for r in rows),'production_released':False}
    (out/'runner-check.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'helper_checks':len(rows),'passed':record['passed']}))

if __name__=='__main__':main()
