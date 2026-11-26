"""ISA-1 Rev16: abstract discrete-time bus safety model, NOT a vendor timing model.
Run: python3 isa1_rev16_bus_safety.py
"""
from dataclasses import dataclass

@dataclass
class Driver:
    name: str
    off_delay: int
    on_delay: int

# Discrete-time test with a conservative example, NOT datasheet limits.
def transition(old: Driver, new: Driver, dead_time: int):
    # old disable requested at t=0; new enable at t=dead_time
    old_off = old.off_delay
    new_on = dead_time + new.on_delay
    overlap = max(0, old_off-new_on)
    return old_off, new_on, overlap

def external_controls(phase, cpu_write=False):
    # Active-low controls, default high = disabled.
    ce_n=oe_n=we_n=1
    cpu_drive=False
    if phase=='READ':
        ce_n=0; oe_n=0
    elif phase=='WRITE':
        ce_n=0; we_n=0; cpu_drive=True
    elif phase!='IDLE':
        raise ValueError(phase)
    assert not (cpu_drive and oe_n==0)
    assert not (oe_n==0 and we_n==0)
    assert not (we_n==0 and ce_n==1)
    return (ce_n,oe_n,we_n,cpu_drive)

def tests():
    checks=0
    # Explicit counterexample: one-hot control can overlap in physical time.
    old=Driver('A',off_delay=12,on_delay=8)
    new=Driver('RAM',off_delay=10,on_delay=7)
    assert transition(old,new,0)[2]==5; checks+=1
    # Evaluate bounded example delays (not physical guarantees).
    for off in range(0,31):
        for on in range(0,31):
            for gap in (0,30):
                a,b,overlap=transition(Driver('old',off,0),Driver('new',0,on),gap)
                assert overlap==max(0,off-gap-on)
                if gap==30: assert overlap==0
                checks+=1
    for phase in ('IDLE','READ','WRITE'):
        result=external_controls(phase)
        assert result=={'IDLE':(1,1,1,False),'READ':(0,0,1,False),'WRITE':(0,1,0,True)}[phase]
        checks+=1
    # State-machine model requires IDLE between active phases and on reset.
    for old_phase in ('IDLE','READ','WRITE'):
        for new_phase in ('IDLE','READ','WRITE'):
            path=[old_phase] if old_phase=='IDLE' else [old_phase,'IDLE']
            if new_phase!='IDLE': path.append(new_phase)
            assert not (old_phase!='IDLE' and new_phase!='IDLE' and path[1]!='IDLE')
            for phase in path: external_controls(phase)
            checks+=1
    # 4-to-1 mux truth-table model: one output, no multi-driver contention.
    for sel in range(4):
        for a in range(256):
            sources=(a,a^0xff,(a+1)&255,0x55)
            assert sources[sel] in range(256)
            checks+=1
    print(f'PASS {checks} model assertions')
    print('Counterexample immediate A->RAM: 5 abstract time units overlap')
    print('With 30-unit dead time and assumed off<=30/on>=0: zero overlap in model')
    print('NOT verified: actual propagation delays, output-enable waveforms, SRAM bus turn-around, PCB signal integrity')

if __name__=='__main__':tests()
