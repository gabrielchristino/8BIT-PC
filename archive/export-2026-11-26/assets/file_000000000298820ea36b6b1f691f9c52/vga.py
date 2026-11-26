from collections import Counter
W,H=800,525

def signals(x,y):
 active=x<640 and y<480
 return active,not(656<=x<752),not(490<=y<492),((y>>2)*160+(x>>2)) if active else None

def test():
 pixels=Counter(); hs=vs=blank=0
 for y in range(H):
  for x in range(W):
   active,h,v,a=signals(x,y)
   hs+=not h;vs+=not v;blank+=not active
   if active:
    assert a==(y//4)*160+x//4
    pixels[a]+=1
 assert len(pixels)==19200 and set(pixels.values())=={16}
 assert hs==96*525 and vs==2*800 and blank==112800
 # row address using shift-add, exhaustive logical coordinates
 for y in range(120):
  for x in range(160):
   assert (y<<7)+(y<<5)+x==y*160+x
 print('420000 raster positions; 19200 addresses, each repeated 16 times; 19200 shift-add comparisons; all assertions passed')
 print('HSYNC low ticks',hs,'VSYNC low ticks',vs,'blank ticks',blank)
 print('frame Hz',25175000/(W*H),'logical pixel period ns',4e9/25175000)
if __name__=='__main__':test()
