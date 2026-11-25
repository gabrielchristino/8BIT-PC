import itertools,json,zlib,struct
from pathlib import Path
# Keyboard validation moved to keyboard.py (commercial undioded membranes).
from keyboard import test as keyboard_test
keyboard_test()
# Two 1024-byte slots, marker last, CRC includes generation and length.
def record(seq,payload):
 body=struct.pack('<IH',seq,len(payload))+payload
 return b'\xa5'+body+struct.pack('<I',zlib.crc32(body))
def read(slot):
 if slot[0]!=165:return None
 seq,size=struct.unpack('<IH',slot[1:7])
 if size>1013:return None
 body=slot[1:7+size]
 if zlib.crc32(body)!=struct.unpack('<I',slot[7+size:11+size])[0]:return None
 return seq,bytes(slot[7:7+size])
def newer(a,b):return 0<((a-b)&0xffffffff)<0x80000000
def recover(slots):
 a,b=map(read,slots)
 return b if a is None or (b is not None and newer(b[0],a[0])) else a
cuts=0
for size in (0,1,31,255,1013):
 for seq in (0,42,0xffffffff):
  old=record(seq,b'old'); new=record((seq+1)&0xffffffff,bytes(i%256 for i in range(size)))
  ops=[(0,0)]+list(enumerate(new[1:],1))+[(0,165)]
  target=bytearray(record((seq-1)&0xffffffff,b'previous').ljust(1024,b'\xff'))
  for i,(addr,val) in enumerate(ops):
   assert recover([old,target])==(seq,b'old');cuts+=1
   target[addr]=val
  assert recover([old,target])==((seq+1)&0xffffffff,new[7:7+size]);cuts+=1
# Four-phase CDC, simultaneous sampling of previous values, ideal flops.
def link(cp,vp,phase,start):
 req=ack=r1=r2=a1=a2=0; issued=done=0; pending=False; stage=0; state=0; mem={}; captured=None; writes=0; h=0
 for t in range(20000):
  old=req,ack,r1,r2,a1,a2
  if t%cp==phase:
   a1,a2=old[1],old[4]
   if pending and old[5]:
    assert captured==((issued-1)//2+17);done+=1;pending=False;req=0
   elif not pending and not old[5] and not req and issued<6 and t>=start:
    issued+=1;req=1;pending=True
  if t%vp==0:
   r1,r2=old[0],old[2]
   if state==0 and old[3] and 161<=h<=192:state=1;stage=0
   elif state==1:
    stage+=1;assert 161<=h<=196
    if stage==2:
     addr=(issued-1)//2
     if issued%2:mem[addr]=addr+17;writes+=1
     captured=mem[addr]
    if stage==4:ack=1;state=2
   elif state==2 and not old[3]:ack=0;state=0
   h=(h+1)%200
  assert done<=issued and writes<=3
  if done==6 and not ack and not a2 and not a1:return t+1
 raise AssertionError('timeout')
links=steps=0
for cp in (1,2,3,5,11):
 for vp in (1,2,3):
  for phase in range(cp):
   for start in range(0,200,7):
    steps+=link(cp,vp,phase,start);links+=1
r=dict(eeprom_cut_boundaries=cuts,cdc_scenarios=links,cdc_ticks=steps,failures=0)
print(r);Path('validation_results.json').write_text(json.dumps(r,indent=2))
