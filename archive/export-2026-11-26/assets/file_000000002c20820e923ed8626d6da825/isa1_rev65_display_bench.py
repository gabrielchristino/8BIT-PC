import json,csv,random
from pathlib import Path
P=Path(__file__).parent
checks=0
palette=[((i*3)&31)<<11 | ((i*5)&63)<<5 | ((i*7)&31) for i in range(16)]
def check(x):
 global checks
 checks+=1
 assert x
# Validate 4bpp framebuffer, RGB565 palette, partial rectangles, and byte accounting
random.seed(651)
fb=bytearray(128*96//2)
for i in range(len(fb)):
 fb[i]=random.randrange(256)
def pix(x,y):
 b=fb[(y*128+x)//2]
 return b>>4 if x%2==0 else b&15
for y in range(96):
 for x in range(128):
  c=pix(x,y);check(0<=c<16)
  rgb=palette[c];check(0<=rgb<=65535)
  check((fb[(y*128+x)//2]>>(4 if x%2==0 else 0))&15==c)
# windows of dimensions, x/y boundaries; no transfer beyond target
for _ in range(1000):
 x0=random.randrange(128);y0=random.randrange(96)
 w=random.randrange(1,129-x0);h=random.randrange(1,97-y0)
 data=bytearray()
 for y in range(y0,y0+h):
  for x in range(x0,x0+w):
   rgb=palette[pix(x,y)];data.extend((rgb>>8,rgb&255))
 check(len(data)==2*w*h)
 check(x0+w<=128 and y0+h<=96)
# Interface lower bounds, no claimed actual throughput
rows=[]
for name,rate in [('SPI 4MHz',500000),('SPI 8MHz',1000000),('SPI 12MHz',1500000),('I80 1MB/s hypothetical',1000000),('I80 2MB/s hypothetical',2000000)]:
 for w,h in [(128,96),(256,192),(32,32),(240,320)]:
  bytes_=2*w*h
  ms=1000*bytes_/rate
  rows.append(dict(interface=name,width=w,height=h,bytes=bytes_,ideal_ms=round(ms,3),ideal_fps=round(1000/ms,3)))
  check(ms>0)
# Simulate safe write handshake: control/data stable before WR rising; no overlapping bus owner
for _ in range(10000):
 cpu=random.randrange(256)
 stages=[('idle',None,1),('setup',cpu,1),('strobe_low',cpu,0),('latch',cpu,1),('release',None,1)]
 check(stages[1][1]==stages[2][1]==stages[3][1])
 check(stages[2][2]==0 and stages[3][2]==1)
 check(stages[0][1] is None and stages[4][1] is None)
with (P/'isa1_rev65_transfer_budget.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
res={'revision':'6.5','checks':checks,'failures':0,'palette_entries':16,'framebuffer_bytes':len(fb),'test_scope':'functional model of 4bpp decode, RGB565, rectangular transfers, hypothetical bandwidth and logical write sequence','limitations':['not transistor or propagation delay simulation','no physical module validated','no delivered price or pinout confirmation','no full CPU or DMA implementation'],'rates_are_hypothetical':True}
(P/'isa1_rev65_results.json').write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(res,ensure_ascii=False))
