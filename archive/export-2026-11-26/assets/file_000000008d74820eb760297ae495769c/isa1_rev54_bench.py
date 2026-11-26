#!/usr/bin/env python3
"""ISA-1 rev5.4: independent edge-based behavioral bench (not electrical simulation)."""
import json, csv, random
from pathlib import Path
P=Path(__file__).parent
nets=json.loads((P/'isa1_rev52_corrected_nets.json').read_text())['nets']
checks=0
required={'SYS_CLK':7,'SUP_RESET_N':5,'PC_CLR_N':5,'CPU_RUN':3,'PC_LOAD_N_SAFE':5,'PC_COUNT_SAFE':6}
for net,minimum in required.items():
 assert len(nets[net])>=minimum,(net,len(nets[net]))
 checks+=1
for i in range(16):
 assert len(nets[f'PC_LOAD_D{i}'])==2
 checks+=1
class Bench:
 def __init__(self,pc=0):self.pc=pc;self.q=[0,0,0];self.valid=False
 def edge(self,sup,load_n=1,count=0,ea=0,ret=0,select_ret=0):
  old=self.q[:]; run=bool(sup and old[2]); clr=bool(sup and old[1]); load_safe=bool(load_n or not run); count_safe=bool(count and run)
  if not clr:self.pc=0
  elif not load_safe:self.pc=(ret if select_ret else ea)&65535
  elif count_safe:self.pc=(self.pc+1)&65535
  if not sup:self.q=[0,0,0];self.valid=False
  else:self.q=[1,old[0],old[1]];self.valid=bool(self.q[2])
  return {'sup':sup,'q1':self.q[0],'q2':self.q[1],'q3':self.q[2],'run_preedge':int(run),'clr_preedge':int(clr),'load_safe_preedge':int(load_safe),'count_safe_preedge':int(count_safe),'pc':self.pc}
# Exhaustively validate arbitrary PC state, with hostile requests throughout startup.
for initial in range(65536):
 b=Bench(initial)
 for step in range(3):
  result=b.edge(1,0,1,0xBEEF,0xFACE,step%2)
  assert b.pc==0,(initial,step,b.pc)
  checks+=1
 # fourth edge must honor load and count priority; run was asserted before edge
 result=b.edge(1,0,1,0xBEEF,0xFACE,1)
 assert b.pc==0xFACE
 checks+=1
 # brownout before next edge clears synchronizer immediately, not PC
 b.q=[0,0,0]  # asynchronous clear of 74HC74 on supervisor low
 result=b.edge(0,0,1,0xBEEF)
 assert b.pc==0 and not result['run_preedge']
 checks+=1
# Differential randomized test with independent reference transition
rng=random.Random(154)
for trial in range(250000):
 b=Bench(rng.randrange(65536)); b.q=[rng.randrange(2) for _ in range(3)]
 sup=rng.randrange(2);load_n=rng.randrange(2);count=rng.randrange(2);ea=rng.randrange(65536);ret=rng.randrange(65536);sel=rng.randrange(2)
 oldpc=b.pc;oldq=b.q[:]
 run=sup and oldq[2];clr=sup and oldq[1]
 expected=0 if not clr else ((ret if sel else ea) if run and not load_n else ((oldpc+1)&65535 if run and count else oldpc))
 got=b.edge(sup,load_n,count,ea,ret,sel)
 assert got['pc']==expected,(trial,got,expected)
 checks+=1
# Waveform example. Asynchronous supervisor assertion needs explicit external event handling.
b=Bench(0xA5A5);trace=[]
for step,(sup,load_n,count) in enumerate([(0,0,1),(1,0,1),(1,0,1),(1,0,1),(1,0,1),(1,1,1),(0,0,1),(1,0,1),(1,0,1),(1,0,1),(1,1,1)]):
 if not sup:b.q=[0,0,0] # async 74HC74 reset asserted before edge
 trace.append({'edge':step,**b.edge(sup,load_n,count,0xBEEF,0xFACE,0)})
with (P/'isa1_rev54_waveform.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=trace[0].keys());w.writeheader();w.writerows(trace)
result={'revision':'5.4','checks':checks,'errors':0,'scope':'behavioral edge model + partial netlist checks; not ERC, SPICE, or timing','caveats':['asynchronous supervisor assertion must be modeled between edges','74HC163 reset synchronous; PC cannot be guaranteed zero without clock','CPU_RUN combinational changes after edge; physical timing unverified','memory write protection not implemented','supervisor and oscillator still not connected']}
(P/'isa1_rev54_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,ensure_ascii=False))
