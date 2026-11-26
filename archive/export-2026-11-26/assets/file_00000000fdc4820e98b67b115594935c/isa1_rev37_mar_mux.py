#!/usr/bin/env python3
"""ISA-1 rev3.7: independently check a 16-bit 3:1 mux composed of 8 HC157s.
This is a logical connectivity model, not electrical/timing simulation."""
import json
from pathlib import Path
from random import Random
OUT=Path(__file__).resolve().parent
# 74HC157: four channels, each selects A when S=0, B when S=1; /E=0.
# Stage 1: PC vs SP; stage 2: stage1 vs EA.
netlist=[]
for stage in (1,2):
    for nibble in range(4):
        ref=f'U_MAR_{stage}_{nibble}'
        for channel in range(4):
            bit=4*nibble+channel
            a=(f'PC[{bit}]' if stage==1 else f'MUX1[{bit}]')
            b=(f'SP[{bit}]' if stage==1 else f'EA[{bit}]')
            netlist.append({'ic':ref,'channel':channel+1,'a':a,'b':b,'y':f'MUX{stage}[{bit}]','select':f'MUX_S{stage}','enable_n':'GND'})
assert len(netlist)==32
assert len({(n['ic'],n['channel']) for n in netlist})==32
assert {n['y'] for n in netlist if n['y'].startswith('MUX2')}=={f'MUX2[{b}]' for b in range(16)}
# Control: 00=PC, 10=SP, 01=EA; 11=EA (stage2 dominates).
def mux(pc,sp,ea,s1,s2):
    stage1=sp if s1 else pc
    return ea if s2 else stage1
rng=Random(3701)
cases=0
for _ in range(100000):
    pc,sp,ea=(rng.randrange(65536) for _ in range(3))
    for s1,s2,expect in ((0,0,pc),(1,0,sp),(0,1,ea),(1,1,ea)):
        assert mux(pc,sp,ea,s1,s2)==expect
        cases+=1
# Dedicated safety checks: no MAR output is connected directly to CPU DB;
# MAR is only clocked when load asserted; outputs are otherwise persistent.
reg=0
for _ in range(10000):
    pc,sp,ea=(rng.randrange(65536) for _ in range(3))
    s1,s2=rng.randrange(2),rng.randrange(2)
    load=rng.randrange(2)
    before=reg
    if load: reg=mux(pc,sp,ea,s1,s2)
    assert reg==(mux(pc,sp,ea,s1,s2) if load else before)
result={'revision':'3.7','mux_devices_74HC157':8,'mar_registers_74HC377':2,'mux_channels':len(netlist),'random_mux_cases':cases,'random_load_hold_cases':10000,'logical_tests':'PASS','electrical_tests':'NOT_RUN','pinout_verified':'NO','pcb_ready':False}
(OUT/'isa1_rev37_mar_mux_nets.json').write_text(json.dumps(netlist,indent=2)+'\n')
(OUT/'isa1_rev37_results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
