import itertools,json,csv
from pathlib import Path
P=Path(__file__).parent
# Thevenin model: hypothetical output resistance, not datasheet bounds.
R={3:(820,1640,3280),2:(700,1400)}
def volts(code,n,v=5,load=75,ro=0,tol=None):
    rs=[r*(1+t)+ro for r,t in zip(R[n],tol or [0]*n)]
    return sum(v/r for i,r in enumerate(rs) if code&(1<<(n-1-i)))/(1/load+sum(1/r for r in rs))
checks=0
rows=[]
for p in range(256):
    rgb=(p>>5,(p>>2)&7,p&3)
    assert (rgb[0]<<5|rgb[1]<<2|rgb[2])==p;checks+=1
    rows.append([p,*rgb,*[volts(c,n) for c,n in zip(rgb,(3,3,2))]])
assert len(set(tuple(r[4:]) for r in rows))==256;checks+=1
summary={}
for n in (3,2):
    peaks=[];steps=[];currents=[];scenarios=0
    for v,load,ro,tol in itertools.product((4.75,5,5.25),(71.25,75,78.75),(0,25,50),itertools.product((-.01,.01),repeat=n)):
        levels=[volts(c,n,v,load,ro,tol) for c in range(2**n)]
        delta=[b-a for a,b in zip(levels,levels[1:])];assert min(delta)>0;checks+=1
        peaks.append(levels[-1]);steps.extend(delta);scenarios+=1
        for c,out in enumerate(levels):
            currents.extend(abs((v if c&(1<<(n-1-i)) else 0)-out)/(r*(1+t)+ro) for i,(r,t) in enumerate(zip(R[n],tol)))
    summary[n]={'resistors_ohm':R[n],'nominal_levels_V':[volts(c,n) for c in range(2**n)],'peak_range_V':[min(peaks),max(peaks)],'min_step_V':min(steps),'max_pin_current_mA':1000*max(currents),'scenarios':scenarios}
with (P/'isa1_rev67_palette.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['pixel','r','g','b','red_V','green_V','blue_V']);w.writerows(rows)
result={'checks':checks,'channels':summary,'scope':'ideal static Thevenin sensitivity model; not electrical qualification'}
(P/'isa1_rev67_results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
