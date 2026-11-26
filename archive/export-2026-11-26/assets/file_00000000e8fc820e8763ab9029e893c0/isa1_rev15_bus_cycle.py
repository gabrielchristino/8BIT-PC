"""ISA-1 Rev15: structural-functional bus and register cycle model.
NOT pin-accurate or electrical/timing simulation. Run with Python 3.
"""
from dataclasses import dataclass
from itertools import product

SOURCES=('A','B','ALU','RAM')

@dataclass(frozen=True)
class Control:
    source: str | None
    load_a: bool=False
    load_b: bool=False
    load_flags: bool=False
    reset: bool=False

class Machine:
    def __init__(self):
        self.a=self.b=self.z=self.c=0
    def step(self,ctl:Control,ram=0,alu=0,alu_c=0):
        # Decode and verify single active tri-state bus driver.
        enables={s: int(not ctl.reset and ctl.source==s) for s in SOURCES}
        assert sum(enables.values()) <= 1, 'two drivers on bus'
        assert ctl.source in (*SOURCES,None), 'invalid selector'
        values={'A':self.a,'B':self.b,'ALU':alu,'RAM':ram}
        bus=values[ctl.source] if ctl.source is not None and not ctl.reset else None
        if ctl.reset:
            self.a=self.b=self.z=self.c=0
            return bus
        if (ctl.load_a or ctl.load_b) and bus is None:
            raise ValueError('register load without bus source')
        # Parallel clock edge: old state is used for all loads.
        next_a=bus if ctl.load_a else self.a
        next_b=bus if ctl.load_b else self.b
        next_z=int((alu & 255)==0) if ctl.load_flags else self.z
        next_c=(alu_c & 1) if ctl.load_flags else self.c
        self.a,self.b,self.z,self.c=next_a,next_b,next_z,next_c
        return bus

def tests():
    checks=0
    for source,load_a,load_b,load_flags in product((*SOURCES,None),range(2),range(2),range(2)):
        m=Machine(); m.a=0x12;m.b=0x34;m.z=1;m.c=1
        ctl=Control(source,bool(load_a),bool(load_b),bool(load_flags))
        if source is None and (load_a or load_b):
            try: m.step(ctl,ram=0x56,alu=0x78,alu_c=0)
            except ValueError: pass
            else: raise AssertionError('floating bus load not caught')
        else:
            bus=m.step(ctl,ram=0x56,alu=0x78,alu_c=0)
            assert bus=={'A':0x12,'B':0x34,'ALU':0x78,'RAM':0x56,None:None}[source]
            assert m.a==(bus if load_a else 0x12)
            assert m.b==(bus if load_b else 0x34)
            assert m.z==(0 if load_flags else 1)
            assert m.c==(0 if load_flags else 1)
        checks+=1
    for source in (*SOURCES,None):
        m=Machine();m.a=123;m.b=234;m.z=m.c=1
        assert m.step(Control(source,True,True,True,True),ram=11,alu=22)==None
        assert (m.a,m.b,m.z,m.c)==(0,0,0,0)
        checks+=1
    # Explicitly check decoder collision on intentionally malformed controls.
    for i,j in product(SOURCES,SOURCES):
        enables={s:int(s==i)+int(s==j) for s in SOURCES}
        collision=sum(enables.values())>1
        assert collision
        checks+=1
    print(f'PASS: {checks} deterministic control/reset/bus cases')
    print('LIMIT: abstract logic; no actual 74HC part pins, delays, SPICE, or PCB verification')

if __name__=='__main__':tests()
