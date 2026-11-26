import json
from pathlib import Path
T=4e9/25_175_000
# Counter and setup are provisional engineering allocations, not verified maxima.
rows=[]
for mux in (38,47):
 for ram in (25,45,55):
  for counter in (35,50):
   total=counter+mux+ram+20+10
   rows.append(dict(mux=mux,ram=ram,counter=counter,setup_budget=20,margin_budget=10,total_ns=total,slack_ns=T-total,passes=total<=T))
# One full raster: address launched one tick before display capture.
n=0
for v in range(525):
 for h in range(200):
  nh=(h+1)%200; nv=(v+(h==199))%525
  fetch=nh<160 and nv<480
  cpu=161<=h<197
  assert not (fetch and cpu)
  if fetch:
   addr=(nv//4)*256+nh
   assert 0<=addr<32768
   n+=1
result=dict(pixel_ns=T,scenarios=rows,failed=sum(not r['passes'] for r in rows),raster_ticks=105000,fetches=n,cpu_ticks_per_line=36,slots_per_frame=9*525,bytes_per_second=9*525/(T*1e-9*105000),scope='Arithmetic and raster model only; no electrical or CDC validation')
p=Path(__file__).parent/'isa1_rev69_results.json';p.write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='scenarios'},indent=2)); print(rows)
