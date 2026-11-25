from sequencer import *
import json
n=0; stalls=0; resets=0
for op in range(256):
 expected=FETCH+TABLE.get(op,[SAFE]);expected=expected[:next((i+1 for i,w in enumerate(expected) if unpack(w)['halt']=='HALT'),len(expected))]
 for delay in (0,1,3,10):
  s=Sequencer()
  for w in expected:
   assert s.word==w
   for _ in range(delay):
    before=vars(s).copy();assert not s.edge(ready=False,opcode=op);assert vars(s)==before;stalls+=1
   before=vars(s).copy();assert not s.edge(run=False,opcode=op);assert vars(s)==before
   assert s.edge(opcode=op)
  assert s.halted if op not in TABLE or op==255 else s.fetch and s.step==0
  n+=1
 for cut in range(len(expected)+1):
  s=Sequencer()
  for _ in range(cut):s.edge(opcode=op)
  assert not s.edge(reset=True,ready=False,run=False);assert s.address==4096 and not s.halted;resets+=1
used={4096+i for i in range(len(FETCH))}|{op*16+i for op,ws in TABLE.items() for i in range(len(ws))}
for a,w in enumerate(ROM):
 assert w<2**26
 if a not in used:assert w==SAFE
 assert sum(((w>>(8*i))&255)<<(8*i) for i in range(4))==w
r=dict(opcode_sequences=n,wait_edges=stalls,reset_cases=resets,rom_addresses=len(ROM),unused_addresses=len(ROM)-len(used),failures=0);print(r);open('sequencer_results.json','w').write(json.dumps(r,indent=2))
