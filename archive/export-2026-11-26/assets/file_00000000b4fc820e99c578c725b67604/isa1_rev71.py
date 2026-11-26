# Behavioral handshake and exclusive VRAM ownership; not electrical simulation.
import json
from pathlib import Path

def run(period, phase, arrival, write):
    req=ack=r1=r2=a1=a2=False
    state='VIDEO'; issued=done=0; launched=False
    for t in range(1200):
        h=t%200
        if t%period==phase:
            a1,a2=ack,a1
            if not launched and t>=arrival:
                req=True; launched=True
            elif req and a2:
                req=False; done+=1
        r1,r2=req,r1
        if state=='VIDEO' and r2 and not ack and 161<=h<=193:
            state='SELECT'
        elif state=='SELECT': state='ACCESS'
        elif state=='ACCESS':
            issued+=1; state='RELEASE'
        elif state=='RELEASE': state='RESTORE'
        elif state=='RESTORE': state='VIDEO'; ack=True
        elif state=='VIDEO' and ack and not r2: ack=False
        video_read=h<=158 or h==199
        cpu_owner=state in ('SELECT','ACCESS','RELEASE')
        cpu_write=state=='ACCESS' and write
        cpu_read=state=='ACCESS' and not write
        assert not (video_read and state!='VIDEO'), (t,state)
        assert not (cpu_read and cpu_write)
        assert not cpu_write or cpu_owner
        if done and not ack and not r2 and state=='VIDEO': break
    assert issued==done==1, (period,phase,arrival,write,issued,done)
    return t+1

cases=cycles=0
for period in (1,2,3,5,8,13):
    for phase in range(period):
        for arrival in range(200):
            for write in (False,True):
                cycles+=run(period,phase,arrival,write); cases+=1
result={'cases':cases,'cycles':cycles,'failures':0,'scope':'integer tick behavioral model; no metastability, reset interruption or analog timing modeled'}
Path(__file__).with_name('isa1_rev71_results.json').write_text(json.dumps(result,indent=2))
print(result)
