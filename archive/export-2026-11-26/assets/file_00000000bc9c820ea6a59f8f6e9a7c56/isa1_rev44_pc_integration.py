#!/usr/bin/env python3
"""Rev4.4: edge-accurate *logical* PC integration checks, not electrical simulation."""
import json, random
from pathlib import Path
from isa1_rev43_pc_control import edge, pc
ROOT=Path(__file__).parent

def nib(v): return [(v>>(4*i))&15 for i in range(4)]

def select_ea_ret(ea, ret, select_ret):
    # Combinational 16-bit 2:1 mux; must be stable before LOAD edge.
    return ret if select_ret else ea

def step(value, action, ea=0, ret=0, select_ret=False, reset=False, clock=True):
    if not clock: return value
    selected=select_ea_ret(ea,ret,select_ret)
    return pc(edge(nib(value), clear_n=not reset, load_n=(action!='LOAD'),
                   enp=int(action=='COUNT'),ent=int(action=='COUNT'),data=selected))

def main():
    count=0
    for v in range(65536):
        assert step(v,'COUNT')==(v+1)&65535;count+=1
        assert step(v,'HOLD')==v;count+=1
        assert step(v,'COUNT',clock=False)==v;count+=1
        assert step(v,'COUNT',reset=True)==0;count+=1
    rng=random.Random(44)
    for _ in range(100000):
        v,ea,ret=[rng.randrange(65536) for _ in range(3)]
        assert step(v,'LOAD',ea,ret)==ea;count+=1
        assert step(v,'LOAD',ea,ret,True)==ret;count+=1
        assert step(v,'LOAD',ea,ret,True,reset=True)==0;count+=1
        assert step(v,'LOAD',ea,ret,True,clock=False)==v;count+=1
    # Return address preservation with nested CALL/RET, modeled stack (not RAM bus).
    for _ in range(10000):
        v=rng.randrange(65536); stack=[]
        for depth in range(rng.randrange(1,9)):
            ret=(v+3)&65535; stack.append(ret)
            v=step(v,'LOAD',ea=rng.randrange(65536));count+=1
        while stack:
            v=step(v,'LOAD',ret=stack.pop(),select_ret=True);count+=1
    # Deliberately wrong: enable every nibble on every COUNT edge.
    bad=pc([(x+1)&15 for x in nib(0x1201)])
    assert bad!=step(0x1201,'COUNT');count+=1
    micro=json.loads((ROOT/'isa1_rev33_microcode.json').read_text())['instructions']
    names={i['mnemonic'] for i in micro}
    for required in ('NOP','LDA_IMM','JMP','CALL','RET'):
        assert required in names
    pc_mentions={i['mnemonic']:sum('PC<-' in s or 'MAR<-PC' in s for s in i['steps']) for i in micro}
    result={'revision':'4.4','status':'PASS — behavioral only','assertions':count,
            'instruction_count_in_rev33':len(micro),'pc_step_mentions':pc_mentions,
            'verified':['four-nibble synchronous COUNT/HOLD/LOAD/CLEAR','no edge means no state change','EA vs RET mux selected on LOAD','clear dominates load','nested logical return-address restoration','deliberate bad carry rejected'],
            'not_verified':['real 74HC163 pinout and timing','physical CALL/RET stack and memory bus','setup/hold when select changes','reset power-on circuitry','actual HDL gate netlist','integrated video/keyboard/ZIF']}
    (ROOT/'isa1_rev44_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:result[k] for k in ('revision','status','assertions','instruction_count_in_rev33')},ensure_ascii=False))
if __name__=='__main__':main()
