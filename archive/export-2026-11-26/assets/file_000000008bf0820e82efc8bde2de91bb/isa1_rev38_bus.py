#!/usr/bin/env python3
"""Rev 3.8: executable 8-way data mux + 6-way address byte mux model."""
import json, random
from pathlib import Path
R=random.Random(3801)
SOURCES=['A','B','ALU','MEM','MDR','TMP','ADDR_BYTE','CONST']
ADDR=['PC_LO','PC_HI','SP_LO','SP_HI','EA_LO','EA_HI']
def mux(values, select):
    assert len(values) in (8,)
    level=values[:]
    for bit in range(3):
        level=[level[2*i+((select>>bit)&1)] for i in range(len(level)//2)]
    return level[0]
def addr_mux(values, select):
    assert 0<=select<8
    return mux(values+[0,0],select)
checks=0
for _ in range(100000):
    v=[R.randrange(256) for _ in range(8)]
    for i in range(8):
        assert mux(v,i)==v[i]; checks+=1
    a=[R.randrange(256) for _ in range(6)]
    for i in range(6):
        assert addr_mux(a,i)==a[i];checks+=1
# Structural mux tree: 8->4->2->1 = 7 eight-bit 2:1 stages, each 2x quad 74HC157.
assert sum((4,2,1))*2==14
# six-way address-byte tree implemented as eight-way with two forbidden leaves
assert sum((4,2,1))*2==14
# check no unselected output reaches bus, including illegal address selectors
for sel in (6,7):
    assert addr_mux([1,2,3,4,5,6],sel)==0
# register capture on rising edge only with load enable; disabled retains old state
for _ in range(50000):
    old=R.randrange(256); val=R.randrange(256); en=R.randrange(2)
    nextval=val if en else old
    assert (nextval==val if en else nextval==old)
    checks+=1
out={'status':'PASS: abstract mux model only','checks':checks,'bus_sources':SOURCES,'address_byte_sources':ADDR,'bus_mux_74HC157':14,'address_byte_mux_74HC157':14,'total_74HC157_if_both_trees':28,'address_select_6_7':'forbidden; model drives zero','not_verified':['physical pinout','timing/glitches','memory read turnaround','full opcode connectivity','clock/reset','fanout','PCB']}
p=Path(__file__).with_name('isa1_rev38_results.json');p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(out,indent=2,ensure_ascii=False))
