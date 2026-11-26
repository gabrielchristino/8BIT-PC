#!/usr/bin/env python3
"""ISA-1 Rev4.3: synchronous four-nibble PC model; NOT electrical simulation."""
import json, random
from pathlib import Path

def edge(n, clear_n=1, load_n=1, enp=0, ent=0, data=0):
    # Assumed 74HC163 priority: synchronous clear > load > count > hold.
    old=n[:]
    if not clear_n: return [0]*4
    if not load_n: return [(data>>(4*i))&15 for i in range(4)]
    carry=[1, old[0]==15, all(x==15 for x in old[:2]), all(x==15 for x in old[:3])]
    return [(x + int(bool(enp and ent and carry[i])))&15 for i,x in enumerate(old)]

def pc(n):return sum(x<<(4*i) for i,x in enumerate(n))

def run():
    tests=0
    for value in range(65536):
        n=[(value>>(4*i))&15 for i in range(4)]
        assert pc(edge(n,enp=1,ent=1))==(value+1)&65535
        assert edge(n,enp=0,ent=1)==n
        assert edge(n,enp=1,ent=0)==n
        tests+=3
    rng=random.Random(431)
    for _ in range(100000):
        v=rng.randrange(65536); data=rng.randrange(65536)
        n=[(v>>(4*i))&15 for i in range(4)]
        assert pc(edge(n,clear_n=0,load_n=0,enp=1,ent=1,data=data))==0
        assert pc(edge(n,clear_n=1,load_n=0,enp=1,ent=1,data=data))==data
        tests+=2
    # A synchronous clear does NOT act until a clock edge.
    n=[5,4,3,2]; assert pc(n)==0x2345
    # Negative test: an intentionally broken ripple enable is detected.
    n=[15,15,0,0]
    bad=[(x+1)&15 for x in n]
    assert pc(bad)!=pc(edge(n,enp=1,ent=1))
    result={'revision':'4.3','status':'PASS (abstract synchronous model only)','assertions':tests+2,'clock_semantics':'all nibble enables evaluated from pre-edge state','assumptions':['synchronous clear takes priority over load','load takes priority over count','parallel load affects all nibbles on same edge'],'unverified':['manufacturer-specific 74HC163 truth table and pinout','actual max propagation delays and setup/hold','clock skew and fanout','reset oscillator availability','physical logic synthesis','full circuit/PCB']}
    p=Path(__file__).with_name('isa1_rev43_results.json');p.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__':run()
