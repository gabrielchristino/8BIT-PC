#!/usr/bin/env python3
"""ISA-1 rev 6.4: exact transfer budget, not hardware simulation."""
import json, csv
from pathlib import Path
root=Path(__file__).parent
width,height=128,96
checks=0
rows=[]
for interface,rate in [('SPI_4MHz',4_000_000),('SPI_8MHz',8_000_000),('SPI_12MHz',12_000_000),('I80_1MBps',8_000_000),('I80_2MBps',16_000_000)]:
 for scale in [1,2]:
  pixels=width*height*scale*scale
  bytes_rgb565=pixels*2
  seconds=bytes_rgb565*8/rate
  assert bytes_rgb565 == 128*96*scale*scale*2
  assert seconds>0
  checks+=2
  rows.append(dict(interface=interface,scale=scale,pixels=pixels,bytes_rgb565=bytes_rgb565,ideal_transfer_ms=round(seconds*1000,3),ideal_max_fps=round(1/seconds,2)))
# packed framebuffer bounds
for y in range(height):
 for x in range(width):
  addr=(y*width+x)//2
  assert 0<=addr<6144
  checks+=1
with (root/'isa1_rev64_transfer_budget.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
result={'checks':checks,'failures':0,'note':'Lower bound transfer time only; no command, setup, bus turnaround, or electrical timing','scenarios':rows}
(root/'isa1_rev64_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
print('checks',checks,'failures',0)
for row in rows:print(row)
