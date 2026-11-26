import itertools,json

def run(cp,phase,start,reset):
    req=ack=r1=r2=a1=a2=0
    state='idle'; stage=0; issued=done=writes=0; pending=False; pc=0; mem=0; captured=0
    for t in range(5000):
        if t==reset:
            req=ack=r1=r2=a1=a2=0; state='idle'; stage=0; pending=False; pc=0
            return 'reset',writes,done
        if t%cp==phase:
            a1,a2=ack,a1
            if pending and a2:
                assert captured==issued
                done+=1; pc+=1; req=0; pending=False
            elif not pending and not a2 and not req and issued<3 and t>=start:
                issued+=1; req=1; pending=True
        r1,r2=req,r1
        h=t%200
        if state=='idle' and r2 and 161<=h<=192:
            state='access';stage=0
        elif state=='access':
            stage+=1
            assert 161<=h<=196
            if stage==1:
                mem=issued; writes+=1
            if stage==4:
                captured=mem;ack=1;state='hold'
        elif state=='hold' and not r2:
            ack=0;state='idle'
        assert writes<=issued and done<=writes and pc==done
        if done==3 and not ack and not a2:
            assert writes==3
            return 'complete',writes,done
    raise AssertionError('timeout')

counts={'complete':0,'reset':0}
for cp in (1,2,3,5,8,13):
 for phase in range(cp):
  for start in range(200):
   for reset in (-1,162,163,164,165,166,170,201):
    result,*_=run(cp,phase,start,reset);counts[result]+=1
print(counts)
open('/mnt/data/isa1/isa1_rev73_results.json','w').write(json.dumps(counts,indent=2))
