"""Rev 4.9: clocked startup contract; abstract event model, NOT electrical simulation."""
import json
from pathlib import Path

class Startup:
    def __init__(self, initial_pc=0xBEEF):
        self.pc=initial_pc
        self.q1=self.q2=self.q3=0
        self.reset_n=False
        self.write_request=False
        self.events=[]
    @property
    def run(self): return bool(self.reset_n and self.q3)
    @property
    def pc_clear_n(self): return bool(self.reset_n and self.q2)
    @property
    def we_n(self): return not (self.run and self.write_request)
    def supervisor(self, good):
        self.reset_n=bool(good)
        if not good:
            self.q1=self.q2=self.q3=0
        self.events.append(('supervisor',good,self.pc,self.run,self.we_n))
    def clock(self):
        old1,old2,old3=self.q1,self.q2,self.q3
        # Synchronous PC clear: sample old q2 on the edge.
        if not self.pc_clear_n: self.pc=0
        elif self.run: self.pc=(self.pc+1)&65535
        if self.reset_n:
            self.q1=1;self.q2=old1;self.q3=old2
        else: self.q1=self.q2=self.q3=0
        self.events.append(('edge',self.reset_n,self.pc,self.run,self.we_n))

def test():
    checks=0
    for start in range(65536):
        s=Startup(start)
        s.write_request=True
        s.supervisor(False)
        assert s.pc==start and not s.run and s.we_n; checks+=3
        # Crucial: no clock while power bad. Release supervisor and start clock.
        s.supervisor(True)
        assert s.pc==start and not s.run and s.we_n; checks+=3
        s.clock()
        assert s.pc==0 and not s.run and s.we_n; checks+=3
        s.clock()
        assert s.pc==0 and not s.run and s.we_n; checks+=3
        s.clock()
        assert s.pc==0 and s.run and not s.we_n; checks+=3
        s.clock()
        assert s.pc==1 and s.run; checks+=2
        # Brownout must inhibit writes and execution without clock.
        s.supervisor(False)
        assert not s.run and s.we_n and s.pc==1; checks+=3
    # No edges => no run, no writes
    s=Startup(0x1234);s.supervisor(True);s.write_request=True
    assert not s.run and s.we_n and s.pc==0x1234; checks+=3
    # Interrupted start sequence must restart with three full edges.
    for cut in (0,1,2):
        s=Startup(0xABCD);s.supervisor(True)
        for _ in range(cut):s.clock()
        s.supervisor(False);s.supervisor(True)
        for _ in range(2):s.clock()
        assert not s.run and s.we_n;checks+=2
        s.clock();assert s.run and s.pc==0;checks+=2
    # A fault injected bypass of run must be flagged.
    s=Startup();s.supervisor(True);s.write_request=True
    faulty_we_n=not s.write_request
    assert faulty_we_n != s.we_n;checks+=1
    result={'revision':'4.9','checks':checks,'status':'PASS','scope':'event-driven behavioral contract, not pin-level or analog','supervisor_candidate':'TPS3808G50DBVR (pinout/threshold still require review)','logic_candidate':'SN74HC74D (2 ICs for 3 FFs)','architecture':'3 asynchronous-clear flip-flops, PC synchronous clear sampled for first two clocks; RUN after third','limitations':['no analog power ramp','no oscillator startup proof','no output propagation delay or setup/hold','no low-VCC write-inhibit guarantee','no complete schematics']}
    path=Path(__file__).with_name('isa1_rev49_results.json');path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':test()
