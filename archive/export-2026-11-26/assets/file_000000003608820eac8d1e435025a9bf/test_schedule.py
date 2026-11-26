from itertools import product
T=1000/25.175
# N pixels, 4N ticks. VGA reads at 0,2,...; captures one tick later.
# Last capture at 2N-1, OE off at 2N; writer on at 2N+1;
# WE low at 2N+2, high at 2N+3, writer off at 2N+4.
# Next OE on at 4N (next block). Address CPU at 2N.
# Read CPU: OE stays on, capture at 2N+2, OE off at 2N+3.
def margins(n,d,g,aa=15):
 return {'video_setup':T-d-max(11.5+aa,7)-2.5-g,
 'video_hold':T-d-1-g,'sram_release':T-d-4-g,
 'address_before_WE':2*T-d-11.5-g,
 'data_before_WE_end':2*T-d-16-8-g,
 'write_pulse':T-d-9-g,'address_to_end':3*T-d-11.5-10-g,
 'write_hold':T-d-g,'cpu_release':(2*n-4)*T-d-16.5-g,
 'cpu_read_setup':2*T-d-11.5-aa-2.5-g,
 'cpu_read_hold':T-d-1-g}
for n in (2,4,8):
 m=margins(n,8,2); print(n,{k:round(v,3) for k,v in m.items()})
 print('sensitivity',sum(min(margins(n,d,g,a).values())>=0 for d,g,a in product((0,2,4,8,12),(0,2,4),(10,15,20))),'/45')
# Logical ping pong buffers: prefetch next group during current group.
# Start with blanking group before each active line. CPU writes after fetch.
for n in (2,4,8):
 mem=bytearray((i*17+3)%256 for i in range(32768)); groups=pixels=writes=0
 for v in range(525):
  buf=None
  for h in range(0,200,n):
   if h==0 and v<480: buf=bytes(mem[(v//4)*256:(v//4)*256+n])
   if h<160 and v<480:
    assert buf is not None and len(buf)==n; pixels+=len(buf)
   nxt=h+n
   expected=bytes(mem[(v//4)*256+nxt:(v//4)*256+nxt+n]) if nxt<160 and v<480 else None
   buf=expected
   a=((v//4)*256+nxt)%32768; mem[a]^=255; writes+=1
   assert buf==expected
   groups+=1
 assert pixels==76800 and groups==105000//n
 print('raster',n,groups,pixels,writes)
