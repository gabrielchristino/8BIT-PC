#!/usr/bin/env python3
"""ISA-1 rev5.8: functional bus/SRAM bench; not an electrical simulator."""
import json, random, csv
from pathlib import Path
P=Path(__file__).resolve().parent
class BusError(Exception): pass
class Bench:
 def __init__(self):
  self.ram=bytearray(32768); self.pc=0; self.sp=0x7fff; self.ea=0; self.ret=0
  self.run=False; self.power_good=False; self.addr_valid=False; self.cycles=0; self.log=[]
 def cycle(self, address=0, drivers=None, read=False, write=False, data=None, target='ram'):
  drivers=drivers or {}
  active={k:v for k,v in drivers.items() if v is not None}
  if len(active)>1: raise BusError('multiple active drivers: '+','.join(active))
  if any(not 0<=v<=255 for v in active.values()): raise BusError('invalid byte')
  if read and write: raise BusError('simultaneous read/write')
  if write and not active: raise BusError('write without data driver')
  if write and 'SRAM' in active: raise BusError('SRAM drives during write')
  if read and active: raise BusError('external driver active during SRAM read')
  if not 0<=address<32768: raise BusError('SRAM address out of range')
  allowed=self.power_good and self.run and self.addr_valid
  result=None
  if write and allowed:
   if target!='ram': raise BusError('unimplemented target')
   self.ram[address]=next(iter(active.values()))
  if read and allowed: result=self.ram[address]
  self.cycles+=1
  self.log.append(dict(cycle=self.cycles,address=address,drivers=';'.join(active),read=int(read),write=int(write),permit=int(allowed),value=result if read else (next(iter(active.values())) if active else None)))
  return result
 def call(self, dest):
  if not (self.run and self.power_good and self.addr_valid): raise BusError('CPU not ready')
  if not 0<=dest<=65535: raise BusError('invalid destination')
  saved=self.pc; self.ea=dest
  for b in ((saved>>8)&255,saved&255):
   self.sp=(self.sp-1)&0xffff
   self.cycle(self.sp,{'CPU':b},write=True)
  self.pc=self.ea
 def ret_op(self):
  if not (self.run and self.power_good and self.addr_valid): raise BusError('CPU not ready')
  low=self.cycle(self.sp,read=True); self.sp=(self.sp+1)&0xffff
  high=self.cycle(self.sp,read=True); self.sp=(self.sp+1)&0xffff
  self.ret=(high<<8)|low; self.pc=self.ret

def run():
 checks=0; failures=[]; b=Bench(); b.addr_valid=True
 # Unsafe writes must be blocked for all combinations except fully ready.
 for pg in (False,True):
  for cpu in (False,True):
   for valid in (False,True):
    b.power_good=pg; b.run=cpu; b.addr_valid=valid; b.ram[42]=0xA5
    b.cycle(42,{'CPU':0x5a},write=True)
    assert b.ram[42]==(0x5a if pg and cpu and valid else 0xa5)
    checks+=1
 b.power_good=b.run=b.addr_valid=True
 # exhaustive byte read/write, addresses chosen at SRAM boundaries
 for address in (0,1,255,256,32766,32767):
  for value in range(256):
   b.cycle(address,{'CPU':value},write=True)
   assert b.cycle(address,read=True)==value
   checks+=2
 # explicit contention / illegal access tests
 cases=[dict(address=1,drivers={'CPU':1,'EEPROM':2}),dict(address=1,drivers={'SRAM':3},write=True),dict(address=1,drivers={'CPU':3},read=True),dict(address=1,write=True),dict(address=32768,read=True),dict(address=1,read=True,write=True)]
 for case in cases:
  try: b.cycle(**case); failures.append(str(case))
  except BusError: checks+=1
 assert not failures
 # CALL/RET on physical byte-array SRAM model; avoid stack wrap into ROM space.
 rng=random.Random(158)
 for trial in range(200):
  b=Bench(); b.power_good=b.run=b.addr_valid=True; b.sp=0x7fff; b.pc=rng.randrange(65536)
  frames=[]
  for depth in range(32):
   frames.append((b.pc,b.sp)); b.call(rng.randrange(65536)); checks+=2
  for depth in range(32):
   expected,sp=frames.pop(); b.ret_op(); assert b.pc==expected and b.sp==sp; checks+=3
 # reset blocking after prior successful writes
 b=Bench(); b.power_good=b.run=b.addr_valid=True; b.cycle(10,{'CPU':77},write=True)
 b.run=False; b.cycle(10,{'CPU':99},write=True); assert b.ram[10]==77; checks+=1
 # Write illustrative trace, not full 10k+ cycles
 demo=Bench(); demo.power_good=demo.run=demo.addr_valid=True; demo.pc=0x1234
 demo.cycle(0x100,{'CPU':0x42},write=True); demo.cycle(0x100,read=True); demo.call(0x4567); demo.ret_op()
 with (P/'isa1_rev58_trace.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=demo.log[0].keys());writer.writeheader();writer.writerows(demo.log)
 result={'revision':'5.8','checks':checks,'failures':failures,'status':'PASS','scope':'Python behavioral model of 32KB SRAM and bus protocol','limitations':['no electrical simulation','no SRAM datasheet timing','no video DMA arbitration','no KiCad ERC','no real 74HC output enable timing'],'example_trace_cycles':demo.cycles}
 (P/'isa1_rev58_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__': run()
