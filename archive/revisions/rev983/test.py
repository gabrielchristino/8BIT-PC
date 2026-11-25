from system import *
import json
from itertools import combinations
n=0
for boot in (False,True):
 for vb in range(4):
  for eb in range(2):
   for a in range(65536):
    k,p=decode(a,boot,vb,eb)
    assert 0<=p<(65536 if k=='io' else 32768)
    assert (k=='vram')==(0x8000<=a<0xa000)
    n+=1
m=Machine();m.boot=False
for start in range(200):
 m.h=start;m.v=0
 for bank in range(4):
  m.vb=bank
  list(m.bus(0x8000+start,start))
  g=m.bus(0x8000+start)
  while True:
   try:next(g)
   except StopIteration as e:assert e.value==start;break
assert m.slots==1600
for r in range(4):
 for c in range(16):
  m.keys={(r,c)}
  for row in range(4):
   m.row=row;assert m.columns()==(65535^(1<<c) if row==r else 65535)
m.keys={(0,0),(0,1),(1,0)};m.row=1;assert m.columns()==65532
for a,b in [(None,None),(1,None),(None,2)]:resolve(a,b)
try:resolve(1,1)
except RuntimeError:pass
else:raise AssertionError('contention')
m=Machine();m.boot=False;m.ram[:13]=bytes([0x32,0x00,0x80,0x10,0xAB,0x34,0x10,0,0x33,0xff,0,0,0]);
while not m.halt:m.step(2)
assert m.a==0xab and m.vram[0]==0xab and m.slots==2
m=Machine()
for _ in range(105000):m.tick()
assert (m.h,m.v,m.pixels)==(0,0,76800)
r={'decode_cases':n,'vram_transactions':1600,'single_key_scan_cases':256,'ghosting_example':1,'integrated_programs':1,'raster_ticks':105000,'failures':0}
print(r);open('results.json','w').write(json.dumps(r,indent=2))
