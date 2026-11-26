"""ISA-1 Rev3.2: abstract bus-cycle sequencer; NOT gate-level, HDL or PCB."""
import importlib.util,json,random
from pathlib import Path
p=Path(__file__).parent
spec=importlib.util.spec_from_file_location('ref',p/'isa1_rev07_emulator.py'); ref=importlib.util.module_from_spec(spec); import sys;sys.modules['ref']=ref;spec.loader.exec_module(ref)

class CycleCPU:
 def __init__(self,mem):
  self.mem=mem;self.pc=0;self.sp=0xbfff;self.a=0;self.b=0;self.z=0;self.c=0;self.halted=False;self.trace=[]
 def rd(self,addr):
  self.trace.append(('READ',addr&65535,0));return self.mem.read(addr)
 def wr(self,addr,val):
  self.trace.append(('WRITE',addr&65535,val&255));self.mem.write(addr,val)
 def fetch(self):
  v=self.rd(self.pc);self.pc=(self.pc+1)&65535;return v
 def word(self):return self.fetch()|(self.fetch()<<8)
 def set_a(self,v):self.a=v&255;self.z=int(self.a==0)
 def push(self,v):
  if not 0x4000<=self.sp<=0xbfff:raise RuntimeError('stack range')
  self.wr(self.sp,v);self.sp=(self.sp-1)&65535
 def pop(self):
  self.sp=(self.sp+1)&65535
  if not 0x4000<=self.sp<=0xbfff:raise RuntimeError('stack range')
  return self.rd(self.sp)
 def step(self):
  if self.halted:return
  op=self.fetch()
  if op==0:pass
  elif op==0x10:self.set_a(self.fetch())
  elif op==0x11:self.b=self.fetch()
  elif op==0x20:
   v=self.a+self.b;self.c=int(v>255);self.set_a(v)
  elif op==0x21:
   v=self.a-self.b;self.c=int(v>=0);self.set_a(v)
  elif op==0x22:self.set_a(self.a&self.b)
  elif op==0x23:self.set_a(self.a|self.b)
  elif op==0x24:self.set_a(self.a^self.b)
  elif op==0x25:self.c=(self.a>>7)&1;self.set_a(self.a<<1)
  elif op==0x26:self.c=self.a&1;self.set_a(self.a>>1)
  elif op==0x30:self.set_a(self.rd(self.word()))
  elif op==0x31:addr=self.word();self.wr(addr,self.a)
  elif op==0x40:self.pc=self.word()
  elif op==0x41:addr=self.word();self.pc=addr if self.z else self.pc
  elif op==0x50:
   addr=self.word();self.push(self.pc>>8);self.push(self.pc&255);self.pc=addr
  elif op==0x51:self.pc=self.pop()|(self.pop()<<8)
  elif op==0x52:self.push(self.a)
  elif op==0x53:self.set_a(self.pop())
  elif op==0xff:self.halted=True
  else:raise RuntimeError(f'unimplemented opcode {op:02x}')

# Bus event invariant: one transaction per abstract microcycle. Read/write distinct.
def check(seed=42):
 rng=random.Random(seed);count=0;events=0
 for _ in range(2000):
  m1=ref.Memory();m2=ref.Memory()
  # single-opcode programs in ROM, with randomly selected operands, branch targets, stack content
  op=rng.choice([0,0x10,0x11,0x20,0x21,0x22,0x23,0x24,0x25,0x26,0x30,0x31,0x40,0x41,0x50,0x51,0x52,0x53,0xff])
  addr=rng.choice([0x4000,0x7fff,0x8000,0xbfff,0xc000,0xe000,0x0000]);imm=rng.randrange(256)
  data=bytes([op,addr&255,(addr>>8)&255,imm]);m1.rom[:len(data)]=data;m2.rom[:len(data)]=data
  a=rng.randrange(256);b=rng.randrange(256);z=rng.randrange(2);c=rng.randrange(2)
  for m in (m1,m2):
   m.write(addr,imm);m.write(0xbfff,rng.randrange(256))
  # sync randomized stack bytes
  m2.ram[:]=m1.ram
  x=ref.CPU(m1,a=a,b=b,z=z,c=c);y=CycleCPU(m2);y.a=a;y.b=b;y.z=z;y.c=c
  err1=err2=None
  try:x.step()
  except RuntimeError as ex:err1=type(ex)
  try:y.step()
  except RuntimeError as ex:err2=type(ex)
  assert err1==err2,(op,err1,err2)
  if err1 is not None:continue
  assert (x.pc,x.sp,x.a,x.b,x.z,x.c,x.halted)==(y.pc,y.sp,y.a,y.b,y.z,y.c,y.halted),(op,x,y)
  assert m1.ram==m2.ram and m1.vram==m2.vram
  assert all(kind in ('READ','WRITE') for kind,_,_ in y.trace)
  count+=1;events+=len(y.trace)
 return {'matched_single_instruction_cases':count,'abstract_memory_microcycles':events,'seed':seed,'scope':'subset of rev07 ISA; no gates or timing','pcb_ready':False}
if __name__=='__main__':
 out=check();(p/'isa1_rev32_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
