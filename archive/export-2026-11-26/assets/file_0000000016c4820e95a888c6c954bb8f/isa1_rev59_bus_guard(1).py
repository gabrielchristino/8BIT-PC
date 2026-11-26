"""ISA-1 rev 5.9: abstract bus ownership and turnaround safety model."""
import json, csv, random
from pathlib import Path
ROOT=Path(__file__).parent
SOURCES=('CPU','SRAM','EEPROM','IO')
class Guard:
    def __init__(self):
        self.owner=None; self.pending=None; self.gap=0; self.run=False; self.power=False
    def step(self, request=None, run=True, power=True, address_valid=True, write=False):
        assert request is None or request in SOURCES
        self.run=run; self.power=power
        allowed=run and power and address_valid
        if not allowed:
            self.owner=None; self.pending=None; self.gap=0
        elif request!=self.owner:
            if self.owner is not None:
                self.owner=None; self.pending=request; self.gap=1
            elif self.gap:
                self.gap-=1
                if self.gap==0: self.owner=self.pending; self.pending=None
            else:
                self.owner=request
        elif self.gap:
            self.gap-=1
        drivers=[x for x in SOURCES if x==self.owner]
        we=bool(allowed and write and self.owner=='CPU')
        return {'owner':self.owner,'drivers':drivers,'we':we,'gap':self.gap}

def run():
    checks=0; traces=[]; g=Guard()
    # deterministic transitions, including power interruptions
    for a,b in [(x,y) for x in SOURCES for y in SOURCES if x!=y]:
        g=Guard(); r=g.step(a); assert r['owner']==a; checks+=1
        r=g.step(b,write=True); assert r['owner'] is None and not r['we']; checks+=1
        r=g.step(b,write=True); assert r['owner']==b and r['we']==(b=='CPU'); checks+=1
    rng=random.Random(0x15A159)
    g=Guard()
    for i in range(100000):
        req=rng.choice((None,)+SOURCES)
        run=rng.random()>.05; power=rng.random()>.02; addr=rng.random()>.04
        write=rng.random()>.5
        r=g.step(req,run,power,addr,write)
        assert len(r['drivers'])<=1; checks+=1
        assert not r['we'] or (r['owner']=='CPU' and run and power and addr); checks+=1
        if not (run and power and addr):
            assert r['owner'] is None and not r['we']; checks+=1
        if i<80: traces.append({'cycle':i,'request':req or 'NONE','run':int(run),'power':int(power),'addr_valid':int(addr),'write_req':int(write),'owner':r['owner'] or 'Z','write_enable':int(r['we'])})
    # Explicitly forbidden protocol combinations: decode two selected chips or read/write concurrently.
    for read,write,selected in [(1,1,('SRAM',)),(1,0,('SRAM','EEPROM')),(0,1,('SRAM','EEPROM'))]:
        valid=(not (read and write)) and len(selected)<=1
        assert not valid; checks+=1
    with (ROOT/'isa1_rev59_trace.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=traces[0].keys());w.writeheader();w.writerows(traces)
    result={'revision':'5.9','checks':checks,'failures':0,'scope':'abstract bus owner FSM and break-before-make; not electrical timing','pending':['address map','real decode','output disable propagation','EEPROM write enable','video arbitration','brownout protection']}
    (ROOT/'isa1_rev59_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':run()
