from system import Machine,decode
class ResetAbort(RuntimeError): pass

class AsyncMachine(Machine):
 def __init__(self,cp,vp,phase):
  super().__init__(); self.cp=cp;self.vp=vp;self.phase=phase;self.t=0;self.req=self.ack=self.r1=self.r2=self.a1=self.a2=0;self.stage=-1;self.payload=None;self.result=None;self.transactions=0
 def reset(self):
  super().reset()
  self.epoch=getattr(self,"epoch",0)+1
  self.req=self.ack=self.r1=self.r2=self.a1=self.a2=0
  self.stage=-1;self.payload=self.result=None;self.h=self.v=0;self.pixel=0;self.row=0
 def guard(self,epoch):
  if not self.power_good:
   self.reset();raise ResetAbort("unsafe supply")
  if epoch!=self.epoch:raise ResetAbort("reset")
 def edge(self):
  if not self.power_good:
   self.reset();self.t+=1;return False,0
  req,ack,r1,r2,a1,a2=self.req,self.ack,self.r1,self.r2,self.a1,self.a2
  cpu=self.t%self.cp==self.phase
  if cpu:self.a1,self.a2=ack,a1
  if self.t%self.vp==0:
   self.r1,self.r2=req,r1
   if self.stage==-1 and r2 and 161<=self.h<=192:self.stage=0
   elif 0<=self.stage<4:
    self.stage+=1;assert 161<=self.h<=196
    if self.stage==2:
     addr,data=self.payload
     if data is None:self.result=self.vram[addr]
     else:self.vram[addr]=data;self.writes+=1
     self.transactions+=1
    if self.stage==4:self.ack=1
   elif self.stage==4 and not r2:self.ack=0;self.stage=-1
   self.tick()
  self.t+=1
  return cpu,a2
 def cpu_edge(self):
  while True:
   if not self.power_good:
    self.reset();raise ResetAbort("unsafe supply")
   c,a=self.edge()
   if c:return a
 def bus(self,a,d=None,delay=0):
  return self._bus(a,d,delay,self.epoch)
 def _bus(self,a,d,delay,epoch):
  self.guard(epoch)
  yield ('ISSUE',a,d)
  self.guard(epoch)
  for _ in range(delay):self.cpu_edge();self.guard(epoch);yield ('WAIT',a,d);self.guard(epoch)
  kind,p=decode(a,self.boot,self.vb,self.eb)
  if kind=='vram':
   while self.req or self.a1 or self.a2 or self.ack:
    self.cpu_edge();self.guard(epoch);yield ('WAIT',a,d);self.guard(epoch)
   self.payload=(p,d);self.req=1
   for _ in range(10000):
    ack=self.cpu_edge();self.guard(epoch)
    if ack:break
    yield ('WAIT',a,d)
    self.guard(epoch)
   else:raise AssertionError('timeout')
   self.req=0;r=self.result
  else:
   self.cpu_edge();self.guard(epoch)
   if d is None:r=self.read(a)
   else:super().write(a,d);self.writes+=1;r=None
  yield ('COMMIT',a,d)
  self.guard(epoch)
  return r

 def write(self,a,d):
  raise RuntimeError("use bus for CPU writes; load fixtures explicitly")
 def micro(self,d=0):
  return self._instruction(d,self.epoch)
 def _instruction(self,d,epoch):
  g=super().micro(d)
  try:
   while True:
    self.guard(epoch)
    try:event=next(g)
    except StopIteration:return
    yield event
  finally:g.close()
