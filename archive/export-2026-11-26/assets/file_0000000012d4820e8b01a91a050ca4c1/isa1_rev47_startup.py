"""ISA-1 Rev4.7: abstract startup/PC contract; NOT a gate-level/electrical simulation."""
import json
from pathlib import Path

class Machine:
    def __init__(self):
        self.pc=None; self.state='POWER_UNSTABLE'; self.edges=0
    def tick(self, power_good, reset_request, load=None, count=False):
        if not power_good or reset_request:
            self.state='RESET_HELD'; self.pc=0; self.edges+=1
            return
        if self.state in ('POWER_UNSTABLE','RESET_HELD'):
            # Must first observe a clock edge with reset asserted in actual hardware.
            assert self.edges>0, 'Release without reset clock edge'
            self.state='RUN'; return
        if load is not None: self.pc=load&65535
        elif count: self.pc=(self.pc+1)&65535
        self.edges+=1

checks=0
for initial in range(65536):
    m=Machine();m.pc=initial
    m.tick(False,True); assert m.pc==0 and m.state=='RESET_HELD';checks+=1
    m.tick(True,False);assert m.pc==0 and m.state=='RUN';checks+=1
    m.tick(True,False,load=initial);assert m.pc==initial;checks+=1
    m.tick(True,False,count=True);assert m.pc==(initial+1)&65535;checks+=1
    m.tick(True,True,load=1234,count=True);assert m.pc==0;checks+=1
# Check a missing reset edge is rejected.
m=Machine()
try:
    m.tick(True,False)
except AssertionError:
    negative_test=True
else:
    negative_test=False
assert negative_test
result={'revision':'4.7','model':'behavioral contract only','checks':checks,'negative_test_pass':negative_test,'electrical_verified':False,'pcb_ready':False}
p=Path(__file__).with_name('isa1_rev47_results.json');p.write_text(json.dumps(result,indent=2)+'\n')
print(result)
