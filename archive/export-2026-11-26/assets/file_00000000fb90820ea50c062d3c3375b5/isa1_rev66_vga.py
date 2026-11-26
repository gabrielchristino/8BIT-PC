import json
from pathlib import Path
f=6_293_750
checks=0
seen=[0]*19200
hs=vs=active=0
for y in range(525):
 for x in range(200):
  h=164<=x<188; v=490<=y<492; a=x<160 and y<480
  hs+=h; vs+=v; active+=a
  if a:
   addr=(y//4)*256+x
   assert 0<=addr<32768
   seen[(y//4)*160+x]+=1
   checks+=1
  checks+=1
assert all(n==4 for n in seen)
assert (hs,vs,active)==(24*525,2*200,160*480)
# ideal DAC, zero source impedance, 75 ohm termination
levels=[5*sum(1/r for bit,r in [(c&1,1400),(c&2,700)] if bit)/(1/75+1/1400+1/700) for c in range(4)]
assert all(abs(a-b)<0.04 for a,b in zip(levels,[0,.2333,.4667,.7]))
result=dict(checks_in_loop=checks,unique_pixels=len(seen),horizontal_hz=f/200,vertical_hz=f/200/525,slot_ns=1e9/f,visible_reads_per_second=active*f/(200*525),blank_slots=200*525-active,allocated_stride_bytes=120*256,used_bytes=19200,dac_volts=levels)
Path(__file__).with_name('isa1_rev66_results.json').write_text(json.dumps(result,indent=2))
print(result)
