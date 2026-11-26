import json
from pathlib import Path
# Abstract synchronous transaction model; not a gate-level or CDC simulation.
# Each transaction uses SELECT, ACCESS, RELEASE, RESTORE, ACK.
checks=0; cases=0; aborted=0; committed=0
for start in range(200):
 for write in (False,True):
  for fault in ('none','reset','power'):
   for offset in (range(210) if fault!='none' else (-1,)):
    cases+=1; state='WAIT'; mem=0x35; cpu=(0x1234,0x7fff,0x42,3,5); snapshot=cpu; writes=0; ack=False
    for t in range(420):
     h=(start+t)%200
     safe=not(fault!='none' and t>=offset)
     if not safe:
      state='ABORT'; aborted+=1; break
     if state=='WAIT' and 161<=h<=193: state='SELECT'
     elif state=='SELECT': state='ACCESS'
     elif state=='ACCESS':
      if write: mem=0xa7; writes+=1
      else: result=mem
      state='RELEASE'
     elif state=='RELEASE': state='RESTORE'
     elif state=='RESTORE': state='ACK'; ack=True
     assert cpu==snapshot; checks+=1
     assert state not in ('SELECT','ACCESS','RELEASE','RESTORE') or 161<=h<=196; checks+=1
     assert writes<=1; checks+=1
     if ack:
      assert writes==int(write); checks+=1
      if not write: assert result==0x35; checks+=1
      committed+=1; break
    assert ack or state=='ABORT'; checks+=1
    assert mem==(0xa7 if writes else 0x35); checks+=1
out=dict(cases=cases,assertions=checks,completed=committed,aborted=aborted,model='abstract synchronous; fault at slot boundary; no analog or CDC validation')
Path(__file__).with_name('isa1_rev72_results.json').write_text(json.dumps(out,indent=2)); print(out)
