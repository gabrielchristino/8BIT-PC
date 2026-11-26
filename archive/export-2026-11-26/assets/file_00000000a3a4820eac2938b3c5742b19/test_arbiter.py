from collections import Counter
# Abstract slots: video setup, video capture, CPU setup, CPU commit.
# A guard interval inside each slot is required in physical implementation.
class Arbiter:
    def __init__(self):
        self.phase=0; self.req=False; self.ack=False; self.sync=[False,False]; self.back=[False,False]; self.pending=None; self.active=None; self.mem=bytearray(32768); self.commits=0; self.pixel=0; self.h=0; self.v=0; self.result=None
    def submit(self,a,d):
        assert not self.req and not self.back[1] and self.pending is None
        self.pending=(a,d); self.req=True
    def cpu_edge(self):
        self.back=[self.ack,self.back[0]]
        if self.req and self.back[1]: self.req=False
        if not self.req and not self.back[1] and not self.ack: self.pending=None
    def tick(self,run=True):
        if not run:
            self.active=None; self.req=self.ack=False; self.sync=[False,False]; self.back=[False,False]; self.pending=None; self.phase=0; self.h=self.v=0; self.pixel=0; return
        self.sync=[self.req,self.sync[0]]
        if not self.sync[1]: self.ack=False
        if self.phase==1:
            self.pixel=self.mem[(self.v//4)*256+self.h] if self.h<160 and self.v<480 else 0
        if self.phase==2:
            self.active=self.pending if self.sync[1] and not self.ack else None
        if self.phase==3:
            if self.active is not None:
                a,d=self.active
                if d is None: self.result=self.mem[a]
                else: self.mem[a]=d
                self.commits+=1; self.ack=True; self.active=None
            self.h+=1
            if self.h==200: self.h=0; self.v=(self.v+1)%525
        self.phase=(self.phase+1)%4

def tests():
    n=0
    for phase in range(4):
      for period in range(1,18):
       for offset in range(period):
        for data in (None,0,255):
         a=Arbiter(); a.mem[123]=77
         for _ in range(phase): a.tick()
         a.submit(123,data)
         for t in range(300):
          a.tick()
          if t%period==offset: a.cpu_edge()
         assert a.commits==1 and a.pending is None
         assert a.mem[123]==(77 if data is None else data)
         if data is None: assert a.result==77
         n+=1
    resets=0
    for start in range(4):
     for cut in range(16):
      a=Arbiter()
      for _ in range(start): a.tick()
      a.submit(12,99)
      for _ in range(cut): a.tick()
      before=a.commits; old=a.mem[12]; a.tick(False)
      for _ in range(32): a.tick(); a.cpu_edge()
      assert a.commits==before and a.mem[12]==old
      a.submit(12,55)
      for _ in range(32): a.tick(); a.cpu_edge()
      assert a.commits==before+1 and a.mem[12]==55
      resets+=1
    a=Arbiter(); a.mem[:]=bytes(i%251 for i in range(32768)); pixels=0
    for v in range(525):
     for h in range(200):
      a.tick(); a.tick()
      assert a.pixel==(a.mem[(v//4)*256+h] if h<160 and v<480 else 0)
      a.tick(); a.tick(); pixels+=1
    assert (a.h,a.v,a.phase)==(0,0,0)
    print(f'{n} transactions; {resets} reset scenarios; {pixels} raster groups; all assertions passed')
if __name__=='__main__': tests()
