"""Rev 7.7–7.9 candidate: executable symbolic microsteps, not physical netlist."""
class CPU:
 def __init__(self):
  self.ram=bytearray(32768); self.rom=bytearray(32768); self.vram=bytearray(32768); self.reset(); self.cycles=0; self.writes=0
 def reset(self):
  self.pc=0; self.sp=0x8000; self.a=self.b=self.x=self.z=self.c=0; self.vb=self.eb=0; self.boot=True; self.halt=False
 def read(self,a):
  if a<0x4000 and self.boot:return self.rom[a]
  if a<0x8000:return self.ram[a]
  if a<0xa000:return self.vram[self.vb*8192+(a&8191)]
  if a>=0xc000:return self.rom[self.eb*16384+(a&16383)]
  return {0xa000:self.vb,0xa001:self.eb,0xa002:int(not self.boot)}.get(a,255)
 def write(self,a,d):
  if a<0x4000 and self.boot:return
  if a<0x8000:self.ram[a]=d
  elif a<0xa000:self.vram[self.vb*8192+(a&8191)]=d
  elif a==0xa000:self.vb=d&3
  elif a==0xa001:self.eb=d&1
  elif a==0xa002 and d&1:self.boot=False
 def bus(self,a,d=None,delay=0):
  yield ('ISSUE',a,d)
  for _ in range(delay):yield ('WAIT',a,d)
  if d is None:r=self.read(a)
  else:self.write(a,d);self.writes+=1;r=None
  yield ('COMMIT',a,d)
  return r
 def fetch(self,delay):
  r=yield from self.bus(self.pc,delay=delay);self.pc=(self.pc+1)&65535;return r
 def word(self,d):
  lo=yield from self.fetch(d);hi=yield from self.fetch(d);return lo|hi<<8
 def push(self,v,d):
  if not 0<self.sp<=0x8000 or (self.boot and self.sp<=0x4000):raise ValueError('stack overflow')
  a=self.sp-1;yield from self.bus(a,v,d);self.sp=a
 def pop(self,d):
  if not 0<=self.sp<0x8000 or (self.boot and self.sp<0x4000):raise ValueError('stack underflow')
  v=yield from self.bus(self.sp,delay=d);self.sp+=1;return v
 def seta(self,v):self.a=v&255;self.z=int(self.a==0)
 def micro(self,d=0):
  op=yield from self.fetch(d)
  if op==0:pass
  elif op==0x10:self.seta((yield from self.fetch(d)))
  elif op==0x11:self.b=yield from self.fetch(d)
  elif op in (0x20,0x21,0x54):
   v=self.a+self.b if op==0x20 else self.a-self.b
   self.c=int(v>255 if op==0x20 else v>=0)
   if op==0x54:self.z=int((v&255)==0)
   else:self.seta(v)
  elif op in (0x22,0x23,0x24):self.seta({0x22:self.a&self.b,0x23:self.a|self.b,0x24:self.a^self.b}[op])
  elif op==0x25:self.c=self.a>>7;self.seta(self.a<<1)
  elif op==0x26:self.c=self.a&1;self.seta(self.a>>1)
  elif op==0x32:self.x=yield from self.word(d)
  elif op in (0x35,0x36):
   delta=1 if op==0x35 else -1;lo=(self.x&255)+delta;hi=((self.x>>8)+(lo//256))&255;self.x=(hi<<8)|(lo&255)
  elif op in (0x30,0x31,0x33,0x34):
   a=self.x if op in (0x33,0x34) else (yield from self.word(d))
   if op in (0x30,0x33):self.seta((yield from self.bus(a,delay=d)))
   else:yield from self.bus(a,self.a,d)
  elif op in (0x40,0x41,0x42,0x50):
   a=yield from self.word(d)
   if op==0x50:
    yield from self.push(self.pc>>8,d);yield from self.push(self.pc&255,d)
   if op in (0x40,0x50) or (op==0x41 and self.z) or (op==0x42 and not self.z):self.pc=a
  elif op==0x51:
   lo=yield from self.pop(d);hi=yield from self.pop(d);self.pc=lo|hi<<8
  elif op==0x52:yield from self.push(self.a,d)
  elif op==0x53:self.seta((yield from self.pop(d)))
  elif op==255:self.halt=True
  else:raise ValueError(f'unknown opcode {op:02x}')
  yield ('END',None,None)
 def step(self,d=0):
  if self.halt:return
  for event in self.micro(d):self.cycles+=1
