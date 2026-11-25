import json
from pathlib import Path
# Abstract shared reset, independent clock edges, two-stage synchronizers.
def run(cp, vp, phase, fault):
    mem={}; req=ack=0; rs=[0,0]; ac=[0,0]; ready=[0,0]; boot=0
    state=0; cpu='idle'; idx=0; writes=[]; reads=[]; epoch=0; aborted=0
    ops=[('w',17,91),('r',17,91),('w',17,203),('r',17,203)]
    for t in range(12000):
        if fault is not None and fault <= t < fault+11:
            if t==fault: aborted=int(cpu=='pending'); epoch+=1
            req=ack=0; rs=[0,0]; ac=[0,0]; ready=[0,0]; boot=0; state=0; cpu='idle'; idx=0
            continue
        oldreq,oldack,oldboot=req,ack,boot
        if t%vp==0:
            rs=[oldreq,rs[0]]; boot=min(2,boot+1)
            h=(t//vp)%200
            if state==0 and rs[1] and 161<=h<=193 and not ack:
                state=1
            elif state==1: state=2
            elif state==2:
                assert 161<=h<=195 and req and cpu=='pending'
                op,a,d=payload
                if op=='w': mem[a]=d; writes.append((epoch,idx))
                else: result=mem.get(a,0)
                state=3
            elif state==3: state=4
            elif state==4: state=0; ack=1
            elif ack and not rs[1]: ack=0
        if (t-phase)%cp==0:
            ac=[oldack,ac[0]]; ready=[oldboot==2,ready[0]]
            if cpu=='idle' and ready[1] and not ac[1] and idx<len(ops):
                payload=ops[idx]; req=1; cpu='pending'
            elif cpu=='pending' and ac[1]:
                if payload[0]=='r': assert result==payload[2]; reads.append((epoch,idx))
                req=0; cpu='rearm'; idx+=1
            elif cpu=='rearm' and not ac[1]: cpu='idle'
        if idx==4 and cpu=='idle' and (fault is None or t>fault+11):
            assert len(set(writes))==len(writes)
            assert [(e,i) for e,i in writes if e==epoch]==[(epoch,0),(epoch,2)]
            assert [(e,i) for e,i in reads if e==epoch]==[(epoch,1),(epoch,3)]
            return t+1,aborted
    raise AssertionError('timeout')
if __name__=='__main__':
    n=cycles=aborts=0
    for cp in (1,2,3,5,8):
      for vp in (1,2,3):
       for phase in range(cp):
        for fault in [None,*range(0,1000,7)]:
         t,a=run(cp,vp,phase,fault); n+=1; cycles+=t; aborts+=a
    r=dict(scenarios=n,simulated_ticks=cycles,resets=n-57,reset_while_pending=aborts,failures=0)
    print(r); Path(__file__).with_name('isa1_rev74_results.json').write_text(json.dumps(r,indent=2))
