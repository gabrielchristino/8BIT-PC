from itertools import combinations,product
from collections import defaultdict
import json,random

def scan(keys):
    rows=[set() for _ in range(4)]
    for r,c in keys: rows[r].add(c)
    out=[]
    for r in range(4):
        cols=rows[r].copy()
        while True:
            nxt=cols.union(*(s for s in rows if s & cols))
            if nxt==cols:break
            cols=nxt
        out.append(cols)
    return out

def decode(rows):
    ambiguous=set()
    for a,b in combinations(range(4),2):
        common=rows[a]&rows[b]
        if len(common)>=2: ambiguous.update((r,c) for r in (a,b) for c in common)
    return {(r,c) for r,s in enumerate(rows) for c in s}-ambiguous,ambiguous

class Debounce:
    def __init__(self):self.last=None;self.count=0;self.active=set()
    def update(self,rows):
        safe,amb=decode(rows)
        snapshot=(frozenset(safe),frozenset(amb))
        if snapshot!=self.last:self.last=snapshot;self.count=1
        else:self.count+=1
        if self.count==3:
            new=safe|(self.active&amb)
            events=(new-self.active,self.active-new);self.active=new;return events
        return set(),set()

def test():
    n=ghost=0
    for k in range(4):
        for keys in combinations(product(range(4),range(16)),k):
            keys=set(keys);rows=scan(keys);safe,amb=decode(rows)
            assert safe<=keys
            if k<=2:assert safe==keys and not amb
            ghost+=bool(amb);n+=1
    rng=random.Random(89)
    for _ in range(10000):
        keys=set(rng.sample(list(product(range(4),range(16))),rng.randrange(65)))
        safe,amb=decode(scan(keys));assert safe<=keys
    d=Debounce();a={(0,0)};b=a|{(1,1)};g=a|{(0,1),(1,0)}
    for s in [a,set(),a,set()]:assert d.update(scan(s))==(set(),set())
    for _ in range(2):assert d.update(scan(a))==(set(),set())
    assert d.update(scan(a))==(a,set())
    for _ in range(3):assert d.update(scan(g))==(set(),set())
    for _ in range(2):assert d.update(scan(b))==(set(),set())
    assert d.update(scan(b))==(b-a,set())
    for _ in range(2):assert d.update(scan(set()))==(set(),set())
    assert d.update(scan(set()))==(set(),b)
    result=dict(exhaustive_snapshots=n,ambiguous_snapshots=ghost,random_snapshots=10000,debounce_sequence='passed')
    print(result);open('keyboard_results.json','w').write(json.dumps(result,indent=2))
if __name__=='__main__':test()
