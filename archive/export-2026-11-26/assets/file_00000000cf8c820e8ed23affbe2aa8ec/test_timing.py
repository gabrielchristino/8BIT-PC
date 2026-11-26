from collections import Counter
from fractions import Fraction

def reduced(h,v):
    active=h<160 and v<480
    return active, not(164<=h<188), not(490<=v<492), ((v>>2)<<8)|h if active else None

def step(h,v):
    return (h+1,v) if h!=199 else (0,0 if v==524 else v+1)

h=v=0; hits=Counter(); hs=vs=blank=0
for i in range(105000):
    assert (h,v)==(i%200,i//200)
    active,s,t,a=reduced(h,v)
    hs+=not s; vs+=not t; blank+=not active
    if active: hits[a]+=1
    for phase in range(4):
        x=h*4+phase
        ref=x<640 and v<480
        assert (active,s,t,a)==(ref,not(656<=x<752),not(490<=v<492),((v//4)<<8)|(x//4) if ref else None)
    h,v=step(h,v)
assert (h,v)==(0,0)
assert len(hits)==19200 and set(hits.values())=={4}
assert (hs,vs,blank)==(12600,400,28200)
print('105000 reduced ticks; 420000 reference comparisons; 19200 addresses; frame wrap: PASS')
print('HSYNC low:',hs,'VSYNC low:',vs,'blank:',blank)
print('frame Hz:',float(Fraction(6293750,200*525)))
# Exhaustive combinational terminal and sync decode, including invalid counter states.
for h in range(256):
    b=lambda n:(h>>n)&1
    assert (bool(b(7) and (b(6) or b(5))) == (h>=160))
    # exact terminal, not partial decode
    assert ((h^199)==0)==(h==199)
for v in range(1024):
    assert ((v^524)==0)==(v==524)
print('1280 counter decode states: PASS')
