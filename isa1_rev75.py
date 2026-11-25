import json
from pathlib import Path
from itertools import product
# Contract model, not actual microcode. Memory completion is a one-cycle event.
def run(ret,sp,flags,delays):
    s=dict(pc=ret,sp=sp,a=0x5a,b=0xa5,z=flags>>1,c=flags&1,step=0)
    mem={}; commits=starts=waits=0; low=high=0
    for i,delay in enumerate(delays):
        before=s.copy(); addr=(s['sp']-1)&65535 if i<2 else s['sp']; starts+=1
        for _ in range(delay):
            assert s==before; waits+=1
        if i<2:
            mem[addr]=(ret>>8) if i==0 else ret&255; s['sp']=addr
        else:
            if i==2: low=mem[addr]
            else: high=mem[addr]
            s['sp']=(addr+1)&65535
        s['step']+=1; commits+=1
    s['pc']=low|(high<<8)
    assert s['pc']==ret and s['sp']==sp and (s['z'],s['c'])==(flags>>1,flags&1)
    assert (s['a'],s['b'])==(0x5a,0xa5) and commits==starts==4
    return waits,commits
if __name__=='__main__':
    n=w=c=0
    for ret,sp,f,d in product((0,1,255,256,32767,32768,65535),(2,3,0x100,0x7fff),range(4),product((0,1,7,31),repeat=4)):
        a,b=run(ret,sp,f,d); n+=1; w+=a;c+=b
    r=dict(scenarios=n,wait_cycles=w,memory_commits=c,failures=0)
    print(r);Path(__file__).with_name('isa1_rev75_results.json').write_text(json.dumps(r,indent=2))
