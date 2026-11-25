from cpu import CPU
from logic import raster

def decode(a,boot,vb,eb):
 if boot and a<0x4000:return 'rom',a
 if a<0x8000:return 'ram',a
 if a<0xa000:return 'vram',vb*8192+(a&8191)
 if a<0xc000:return 'io',a
 return 'rom',eb*16384+(a&16383)

def resolve(*drivers):
 active=[d for d in drivers if d is not None]
 if len(active)>1:raise RuntimeError('bus contention')
 return active[0] if active else None

class Machine(CPU):
 def __init__(self):
  super().__init__(); self.h=self.v=0;self.slots=0;self.pixels=0;self.keys=set();self.row=0;self.power_good=True
 def tick(self):
  if self.h<160 and self.v<480:
   self.pixel=self.vram[(self.v//4)*256+self.h];self.pixels+=1
  else:self.pixel=0
  self.h,self.v=raster(self.h,self.v)
 def bus(self,a,d=None,delay=0):
  yield ('ISSUE',a,d)
  self.tick()
  for _ in range(delay):self.tick();yield ('WAIT',a,d)
  if decode(a,self.boot,self.vb,self.eb)[0]=='vram':
   while not 161<=self.h<=192:self.tick();yield ('WAIT',a,d)
   for phase in range(5):
    assert 161<=self.h<=196
    if phase==2:
     if d is None:r=self.read(a)
     elif self.power_good:self.write(a,d);self.writes+=1;r=None
     else:raise RuntimeError('power unsafe')
    self.tick();yield ('ACCESS',a,d)
   self.slots+=1
  else:
   if d is None:r=self.read(a)
   elif self.power_good:self.write(a,d);self.writes+=1;r=None
   else:raise RuntimeError('power unsafe')
  self.tick();yield ('COMMIT',a,d)
  return r
 def read(self,a):
  if a==0xa011:return self.columns()&255
  if a==0xa012:return self.columns()>>8
  return super().read(a)
 def write(self,a,d):
  if a==0xa010:self.row=d&3
  else:super().write(a,d)
 def columns(self):
  # Passive undioded matrix: connected components, active row low, others high-Z.
  rows={self.row};cols=set()
  while True:
   c=cols|{c for r,c in self.keys if r in rows};r=rows|{r for r,k in self.keys if k in c}
   if (r,c)==(rows,cols):return 65535^sum(1<<k for k in cols)
   rows,cols=r,c
