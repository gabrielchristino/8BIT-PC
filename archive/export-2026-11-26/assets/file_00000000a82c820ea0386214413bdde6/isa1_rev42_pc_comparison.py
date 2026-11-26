#!/usr/bin/env python3
"""ISA-1 Rev4.2 behavioral comparison, not gate-level timing."""
import json, random
from pathlib import Path
MASK=0xffff
class Reference:
 def __init__(self): self.pc=0
 def step(self,op,val=0):
  if op=='RESET': self.pc=0
  elif op=='INC': self.pc=(self.pc+1)&MASK
  elif op in ('JMP','CALL','RET','LOAD'): self.pc=val&MASK
  elif op=='HOLD': pass
  else: raise ValueError(op)
  return self.pc
class RegAdder:
 def __init__(self): self.q=0
 def step(self,op,val=0):
  # 2 octal registers, 4 ripple-connected nibble adders, source mux.
  carry=1; result=0
  for nib in range(4):
   s=((self.q>>(4*nib))&15)+carry
   result|=(s&15)<<(4*nib)
   carry=s>>4
  if op=='RESET': self.q=0
  elif op=='INC': self.q=result
  elif op in ('JMP','CALL','RET','LOAD'): self.q=val&MASK
  elif op=='HOLD': pass
  else: raise ValueError(op)
  return self.q
class Cascaded163:
 def __init__(self): self.n=[0,0,0,0]
 def step(self,op,val=0):
  if op=='RESET': self.n=[0]*4
  elif op=='INC':
   # all enables computed from OLD values, then simultaneous edge
   old=self.n[:]
   en=[True,old[0]==15,old[0]==15 and old[1]==15,all(x==15 for x in old[:3])]
   self.n=[((x+int(e))&15) for x,e in zip(old,en)]
  elif op in ('JMP','CALL','RET','LOAD'):
   self.n=[(val>>(4*i))&15 for i in range(4)]
  elif op=='HOLD': pass
  else: raise ValueError(op)
  return sum(x<<(4*i) for i,x in enumerate(self.n))
def run():
 ref=Reference(); a=RegAdder(); b=Cascaded163(); checks=0; boundary=0
 def test(op,val=0):
  nonlocal checks
  r=ref.step(op,val)
  assert a.step(op,val)==r,(op,val,'adder',r,a.q)
  assert b.step(op,val)==r,(op,val,'counter',r,b.n)
  checks+=2
 # Exhaustive increment from every possible PC value, independent loads
 for v in range(65536):
  test('LOAD',v);test('INC');boundary+=1
 # carry boundaries and reset
 for v in (0,1,0x000f,0x00ff,0x0fff,0xffff,0x7fff,0xfffe):
  test('LOAD',v);test('INC');test('RESET');test('HOLD')
 rng=random.Random(0x15A1)
 ops=['INC']*60+['HOLD']*15+['JMP']*8+['CALL']*8+['RET']*8+['RESET']
 for _ in range(200000):
  op=rng.choice(ops); test(op,rng.randrange(65536))
 # Independent accounting: no auxiliary logic or pin/timing included
 result={'status':'PASS','scope':'behavioral state transitions only','exhaustive_start_values':boundary,'comparisons':checks,'random_steps':200000,'reference':'16-bit PC atomic load, reset, increment, hold','bom_estimate':{'reg_plus_adder':{'register_packages':2,'adder_packages':4,'load_mux_74hc157_packages':8,'subtotal':14},'counter_163':{'counter_packages':4,'load_mux_74hc157_packages':4,'carry_enable_logic_packages':'at least 1 (depends on logic synthesis)','subtotal_before_carry_logic':8}},'unverified':['actual 74HC163 variant/pinout/reset semantics','timing maximum and carry fanout','74HC163 load and count priority','clock/reset distribution','complete CALL/RET datapath','real PCB']}
 p=Path(__file__).with_name('isa1_rev42_results.json');p.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__':run()
