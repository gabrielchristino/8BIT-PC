#!/usr/bin/env python3
"""ISA-1 Rev18: executable architectural comparison, NOT a gate-level simulation."""
import random, json
from collections import Counter
R=random.Random(1801)
OPS=('MOV','ADD','ADC','SUB','AND','OR','XOR','LOAD','STORE','CALL','RET','BRZ')
N=50000
# Compare same abstract instruction stream: shared tri-state bus vs split source mux/result bus.
# Model transaction intent, not undocumented hardware or a finalized ISA encoding.
class Model:
 def __init__(self,split):
  self.split=split; self.reg=[0]*4; self.ram=bytearray(65536); self.z=0; self.c=0; self.sp=0xfffe; self.pc=0; self.bus_events=Counter(); self.hazards=0
 def access(self,kind):
  # A shared bus must change source between register, ALU and memory; split has one mux output.
  seq={'MOV':('reg','reg'),'ADD':('reg','alu'),'ADC':('reg','alu'),'SUB':('reg','alu'),'AND':('reg','alu'),'OR':('reg','alu'),'XOR':('reg','alu'),'LOAD':('mem','reg'),'STORE':('reg','mem'),'CALL':('reg','mem'),'RET':('mem','reg'),'BRZ':('reg',)}[kind]
  if self.split: self.bus_events['mux_select']+=len(seq)
  else:
   self.bus_events['tri_state_source_change']+=sum(a!=b for a,b in zip(seq,seq[1:])); self.bus_events['tri_state_drive']+=len(seq)
  if kind in ('LOAD','STORE','CALL','RET'): self.bus_events['external_access']+=1
 def step(self,op,a,b,imm):
  self.access(op); x=self.reg[a]; y=self.reg[b]; addr=(imm*257+13)&65535
  if op=='MOV': self.reg[a]=y
  elif op in ('ADD','ADC','SUB','AND','OR','XOR'):
   if op=='ADD': v=x+y
   elif op=='ADC': v=x+y+self.c
   elif op=='SUB': v=x-y
   elif op=='AND': v=x&y
   elif op=='OR': v=x|y
   else: v=x^y
   self.reg[a]=v&255; self.z=int(self.reg[a]==0)
   if op in ('ADD','ADC'): self.c=int(v>255)
   if op=='SUB': self.c=int(v>=0)
  elif op=='LOAD': self.reg[a]=self.ram[addr]
  elif op=='STORE': self.ram[addr]=x
  elif op=='CALL':
   self.sp=(self.sp-2)&65535; self.ram[self.sp]=self.pc&255; self.ram[(self.sp+1)&65535]=(self.pc>>8)&255; self.pc=addr
  elif op=='RET':
   self.pc=self.ram[self.sp]|(self.ram[(self.sp+1)&65535]<<8); self.sp=(self.sp+2)&65535
  elif op=='BRZ' and self.z: self.pc=addr
  self.pc=(self.pc+1)&65535
 def snapshot(self): return (tuple(self.reg),bytes(self.ram),self.z,self.c,self.sp,self.pc)

a=Model(False); b=Model(True); counts=Counter()
for i in range(N):
 op=OPS[R.randrange(len(OPS))]; r1=R.randrange(4);r2=R.randrange(4);imm=R.randrange(256)
 a.step(op,r1,r2,imm);b.step(op,r1,r2,imm);counts[op]+=1
 assert a.reg==b.reg and a.z==b.z and a.c==b.c and a.sp==b.sp and a.pc==b.pc,('mismatch',i,op)
assert a.ram==b.ram
# Bus turnaround model: worst-case disable and enable, inclusive simultaneous boundary treated unsafe.
# Values are ABSTRACT ticks, not measured ns.
turnaround=[]
for guard in (0,5,10,15,20,21):
 unsafe=0
 for disable in range(21):
  for enable in range(21):
   if guard+enable<=disable: unsafe+=1
 turnaround.append({'guard_ticks':guard,'unsafe_cases':unsafe,'cases':441})
# Invariant-based SRAM controller tests, including READ->WRITE and WRITE->READ.
class Controller:
 def __init__(self): self.phase='IDLE';self.ce=1;self.oe=1;self.we=1;self.cpu_drive=0
 def state(self,phase):
  self.phase=phase
  self.ce=int(phase=='IDLE');self.oe=int(phase!='READ');self.we=int(phase!='WRITE_PULSE');self.cpu_drive=int(phase in ('WRITE_SETUP','WRITE_PULSE','WRITE_HOLD'))
  assert not (self.oe==0 and self.cpu_drive),phase
  assert not (self.we==0 and (self.oe==0 or not self.cpu_drive or self.ce)),phase
  assert not (self.ce and (not self.oe or not self.we or self.cpu_drive)),phase
c=Controller(); transitions=0
for _ in range(10000):
 direction=R.choice(('READ','WRITE'))
 for state in (('IDLE','READ','IDLE') if direction=='READ' else ('IDLE','WRITE_SETUP','WRITE_PULSE','WRITE_HOLD','IDLE')):
  c.state(state);transitions+=1
out={'architecture_comparison':{'instructions':N,'same_architectural_state':True,'instruction_counts':dict(counts),'shared_bus_events':dict(a.bus_events),'split_bus_events':dict(b.bus_events)},'abstract_turnaround':turnaround,'sram_controller_state_checks':transitions,'limits':['No real gate timing, metastability, fanout, or analog behavior','Bus events are a conceptual cost proxy, NOT chip count or speed','Controller checks static states, not real pin transitions','ISA encoding and actual netlist are not frozen']}
print(json.dumps(out,indent=2));open('/mnt/data/isa1/isa1_rev18_results.json','w').write(json.dumps(out,indent=2)+'\n')
