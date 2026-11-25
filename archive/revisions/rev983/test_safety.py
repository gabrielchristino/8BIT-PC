from integrated import AsyncMachine,ResetAbort
import json
n=0
for cp in (1,2,5):
 for phase in range(cp):
  for addr in (0x4000,0x8000):
   for cut in range(40):
    for power in (False,True):
     m=AsyncMachine(cp,1,phase);m.boot=False;m.h=150
     g=m.bus(addr,0x55,delay=3)
     for i in range(cut):
      try:next(g)
      except StopIteration:break
     if power:m.power_good=False
     m.reset(); before=bytes(m.ram),bytes(m.vram)
     try:
      for _ in g:pass
     except ResetAbort:pass
     assert before==(bytes(m.ram),bytes(m.vram))
     assert not (m.req or m.ack or m.r1 or m.r2 or m.a1 or m.a2)
     m.power_good=True;m.boot=False
     for _ in m.bus(addr,0xaa):pass
     assert m.read(addr)==0xaa
     n+=1
for addr in (0x4000,0x8000):
 m=AsyncMachine(2,1,0);m.boot=False;m.power_good=False
 try:
  for _ in m.bus(addr,0x55):pass
 except ResetAbort:pass
 else:raise AssertionError('unsafe accepted')
 assert m.read(addr)==0
 n+=1
print(n);open('safety_results.json','w').write(json.dumps({'cases':n,'failures':0}))
