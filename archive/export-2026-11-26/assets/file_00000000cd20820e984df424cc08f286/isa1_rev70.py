import json
from pathlib import Path

def decode(a, vb, eb, boot):
    if a<0x8000:
        if boot and a<0x4000: return 'EEPROM',a
        return 'RAM',a
    if a<0xa000:return 'VRAM',vb*8192+(a&8191)
    if a<0xc000:return ('BANK',a-0xa000) if a in (0xa000,0xa001,0xa002) else ('IO_RESERVED',a-0xa000)
    return 'EEPROM',eb*16384+(a&16383)

n=0
for vb in range(4):
 for eb in range(2):
  for boot in (False,True):
   for a in range(65536):
    d,p=decode(a,vb,eb,boot)
    assert 0<=p<({'RAM':32768,'VRAM':32768,'EEPROM':32768,'BANK':3,'IO_RESERVED':8192}[d])
    if not boot and a<32768: assert (d,p)==('RAM',a)
    n+=1
for p in range(32768):
 assert decode(0x8000+(p&8191),p>>13,0,False)==('VRAM',p)
 assert decode(0xc000+(p&16383),0,p>>14,False)==('EEPROM',p)
# Synchronous counters, including reset at terminal count; next address for prefetch.
h=v=0; fetches=slots=0
for tick in range(105000):
 assert (h,v)==(tick%200,tick//200)
 nh=0 if h==199 else h+1
 nv=(v+1)%525 if h==199 else v
 fetch=nh<160 and nv<480
 slot=161<=h<197
 assert not(fetch and slot)
 if fetch:
  p=(nv>>2)*256+nh
  assert decode(0x8000+(p&8191),p>>13,0,False)==('VRAM',p)
  fetches+=1
 slots+=int(slot and (h-161)%4==0)
 h,v=nh,nv
assert (h,v)==(0,0)
r=dict(map_cases=n,physical_address_roundtrips=65536,raster_ticks=105000,fetches=fetches,slots=slots,scope='Behavioral mapping and counter model; no electrical or CDC validation')
Path(__file__).with_name('isa1_rev70_results.json').write_text(json.dumps(r,indent=2));print(r)
