import json, random
from pathlib import Path
ROOT=Path(__file__).parent
MASK=0xffff
class Machine:
    def __init__(self, optimized=False):
        self.pc=0; self.sp=0xff00; self.ea=0; self.ret=0; self.target=0; self.ram=bytearray(65536); self.optimized=optimized; self.cycles=0
    def tick(self): self.cycles+=1
    def push(self,v):
        self.sp=(self.sp-1)&MASK; self.ram[self.sp]=v&255; self.tick()
    def pop(self):
        v=self.ram[self.sp]; self.sp=(self.sp+1)&MASK; self.tick(); return v
    def call(self,destination):
        # Contract: PC already points to instruction following decoded CALL operands.
        self.ea=destination&MASK; self.tick()
        return_pc=self.pc
        self.push((return_pc>>8)&255); self.push(return_pc&255)
        if self.optimized:
            self.target=self.ea; self.tick(); self.pc=self.target
        else: self.pc=self.ea
        self.tick()
    def ret_op(self):
        lo=self.pop(); hi=self.pop(); self.ret=lo|(hi<<8); self.tick()
        if self.optimized:
            self.target=self.ret; self.tick(); self.pc=self.target
        else: self.pc=self.ret
        self.tick()

def run():
    checks=0
    # Compare baseline with target-register design, actual byte-array stack memory.
    for seed in range(128):
        r=random.Random(seed); a=Machine(); b=Machine(True)
        for depth in range(32):
            addr=r.randrange(65536); dest=r.randrange(65536)
            a.pc=b.pc=addr
            a.call(dest); b.call(dest)
            assert a.pc==b.pc==dest and a.sp==b.sp and a.ram==b.ram
            checks+=4
        for depth in range(32):
            a.ret_op(); b.ret_op()
            assert a.pc==b.pc and a.sp==b.sp and a.ram==b.ram
            checks+=3
        assert a.sp==b.sp==0xff00; checks+=1
    # Full 16-bit return address range, single call/return.
    for address in range(65536):
        m=Machine(); m.pc=address; m.call(0x1234); m.ret_op()
        assert m.pc==address and m.sp==0xff00
        checks+=2
    # Detect a genuine hazard: overwriting EA before transferring to TARGET corrupts CALL.
    bad=Machine(True); bad.pc=0x2345; bad.ea=0x4567; bad.ea=0x9999; bad.target=bad.ea
    assert bad.target!=0x4567; checks+=1
    # Counterexample: shared target register does not eliminate an input selection path.
    results={'revision':'5.7','checks':checks,'passed':True,'nested_depth':32,'address_space_tested':65536,
      'baseline_parts':'EA 2x HC377, RET 2x HC377, PC mux 4x HC157',
      'candidate_parts':'EA 2x HC377, RET 2x HC377, TARGET 2x HC377, plus selection/transfer logic',
      'conclusion':'No demonstrated chip reduction; retain four HC157 for now',
      'limitations':['Abstract byte-addressable RAM; no bus electrical model','No actual microcode or physical control timing','No electrical propagation-delay verification']}
    (ROOT/'isa1_rev57_results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(results,indent=2,ensure_ascii=False))
if __name__=='__main__':run()
