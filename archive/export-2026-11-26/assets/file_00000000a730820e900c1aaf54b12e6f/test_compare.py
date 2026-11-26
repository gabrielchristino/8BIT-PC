from itertools import product

def eq8(a,b):
    return not any(((a>>i)^(b>>i))&1 for i in range(8))

def cmp4(a,b,lower):
    for i in range(3,-1,-1):
        x,y=(a>>i)&1,(b>>i)&1
        if x!=y:return 1 if x else -1
    return lower

def cmp16(a,b):
    r=0
    for i in range(0,16,4):r=cmp4((a>>i)&15,(b>>i)&15,r)
    return r
n=0
for a,b in product(range(256),repeat=2):
    assert eq8(a,b)==(a==b);n+=1
print('eq8:',n)
n=0
for a,b,r in product(range(16),range(16),(-1,0,1)):
    assert cmp4(a,b,r)==((a>b)-(a<b) if a!=b else r);n+=1
print('cmp4:',n)
n=0
for a in range(65536):
    for b in (0,0x3fff,0x4000,0x7fff,0x8000,0xffff):
        assert cmp16(a,b)==((a>b)-(a<b));n+=1
print('cmp16:',n)
print('total:',65536+768+n,'failures: 0')
