import json
from pathlib import Path
F=25_175_000/4
h=v=0; checks=0; active=hs=vs=blank=slots=0; addresses=set()
for i in range(200*525):
    assert (h,v)==(i%200,i//200); checks+=1
    visible=h<160 and v<480
    hsync=164<=h<188; vsync=490<=v<492
    hs+=hsync; vs+=vsync
    if visible:
        a=((v//4)<<8)|h
        assert 0<=a<32768; checks+=1
        addresses.add(a); active+=1
    else: blank+=1
    # Conservative: only horizontal blank, 2 guard ticks at each end.
    # Each transaction occupies four ticks: select, access, release, idle.
    if 162<=h<198 and (h-162)%4==0:
        assert not visible and h+3<198; checks+=1; slots+=1
    h+=1
    if h==200: h=0; v=(v+1)%525
assert (h,v)==(0,0) and len(addresses)==19200
assert hs==24*525 and vs==2*200 and active==160*480
r=dict(checks=checks,unique_pixels=len(addresses),active_ticks=active,blank_ticks=blank,hsync_ticks=hs,vsync_ticks=vs,slots_per_frame=slots,frame_hz=F/105000,slot_rate=slots*F/105000,tick_ns=1e9/F)
Path(__file__).with_name('isa1_rev68_results.json').write_text(json.dumps(r,indent=2)); print(r)
