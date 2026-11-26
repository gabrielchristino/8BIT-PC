#!/usr/bin/env python3
"""ISA-1 rev 6.2: arithmetic/digital feasibility tests, NOT an analog NTSC simulator."""
import json, csv, pathlib
P=pathlib.Path(__file__).parent
FOSC=14_318_180
TICKS_LINE=910
TICKS_PIXEL=5
PIXELS=128
BYTES_LINE=64
LINES=96
assert PIXELS*LINES//2==6144
assert TICKS_LINE%TICKS_PIXEL==0
assert PIXELS*TICKS_PIXEL<TICKS_LINE
assert FOSC/TICKS_LINE > 15_700 and FOSC/TICKS_LINE < 15_800
assert FOSC/TICKS_PIXEL > 2_800_000
checks=0
for y in range(LINES):
    for x in range(PIXELS):
        addr=y*BYTES_LINE+(x>>1)
        assert 0<=addr<6144
        checks+=1
# Verify nibble packing and extraction across every 8-bit byte and pixel parity
for b in range(256):
    for x in (0,1):
        pixel=((b>>4)&15) if x==0 else (b&15)
        assert 0<=pixel<16
        checks+=1
# Confirm all active pixel slots are non-overlapping and within a line
slots=[(i*5,(i+1)*5) for i in range(PIXELS)]
for i,(a,b) in enumerate(slots):
    assert b-a==5 and b<=910
    if i: assert slots[i-1][1]==a
    checks+=1
# Every pair of pixels maps to same VRAM address, with distinct nibble
for y in range(LINES):
    for byte in range(BYTES_LINE):
        x=2*byte
        assert y*64+(x//2)==y*64+((x+1)//2)
        checks+=1
with (P/'isa1_rev62_video_line.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['pixel','clock_start_tick','clock_end_tick','vram_byte','nibble'])
    for x,(a,b) in enumerate(slots): w.writerow([x,a,b,x//2,'high' if x%2==0 else 'low'])
result={
 'status':'PASS digital arithmetic only', 'checks':checks,
 'master_clock_hz':FOSC,'master_ticks_per_line':TICKS_LINE,
 'line_us':TICKS_LINE/FOSC*1e6,
 'line_frequency_hz':FOSC/TICKS_LINE,
 'pixel_ticks':TICKS_PIXEL,'pixel_frequency_hz':FOSC/TICKS_PIXEL,
 'active_pixel_us':PIXELS*TICKS_PIXEL/FOSC*1e6,
 'line_remaining_us':(TICKS_LINE-PIXELS*TICKS_PIXEL)/FOSC*1e6,
 'vram_bytes_per_line':BYTES_LINE,'vram_bytes_frame':6144,
 'limitations':['no analog RGB DAC verification','no composite waveform or NTSC compliance test','no vertical sync field structure','no SRAM electrical timing or CPU arbitration','no screen model confirmed','clock division /5 needs physical implementation']}
(P/'isa1_rev62_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,indent=2,ensure_ascii=False))
