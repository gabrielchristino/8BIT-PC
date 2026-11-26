"""ISA-1 rev14: executable FUNCTIONAL models of discrete 74HC logic blocks.
NOT manufacturer pin-level models, HDL timing simulation, or electrical validation.
Run: python3 isa1_rev14_logic_sim.py
"""
from itertools import product
import random

def hc283(a, b, ci):
    s=(a&15)+(b&15)+(ci&1)
    return s&15, (s>>4)&1

def add8(a,b,ci):
    lo,c4=hc283(a,b,ci)
    hi,c8=hc283(a>>4,b>>4,c4)
    return lo|(hi<<4),c8

def alu(a,b,op,carry=0):
    a &=255; b &=255; carry &=1
    if op=='ADD': r,c=add8(a,b,0)
    elif op=='ADC': r,c=add8(a,b,carry)
    elif op=='SUB': r,c=add8(a,b^255,1)
    elif op=='SBC': r,c=add8(a,b^255,carry) # C=1 means no incoming borrow
    elif op=='AND': r,c=a&b,carry
    elif op=='OR': r,c=a|b,carry
    elif op=='XOR': r,c=a^b,carry
    else: raise ValueError(op)
    return r,c,int(r==0)

def expected(a,b,op,carry):
    if op=='ADD': n=a+b; r=n&255; c=n>>8
    elif op=='ADC': n=a+b+carry; r=n&255; c=n>>8
    elif op=='SUB': n=a-b; r=n&255; c=int(n>=0)
    elif op=='SBC': n=a-b-(1-carry); r=n&255; c=int(n>=0)
    elif op=='AND': r=a&b; c=carry
    elif op=='OR': r=a|b; c=carry
    elif op=='XOR': r=a^b; c=carry
    return r,c,int(r==0)

# A 74HC245-like output driver drives only when its OE is asserted.
# No model of rise/fall times, enable propagation, or voltage levels.
def resolve_bus(drivers):
    enabled=[(name,value) for name,value,oe in drivers if oe]
    if len(enabled)>1: raise RuntimeError('BUS_CONTENTION: '+','.join(n for n,_ in enabled))
    return enabled[0][1] if enabled else None

def run():
    cases=0
    for op in ('ADD','ADC','SUB','SBC','AND','OR','XOR'):
        carries=(0,1) if op in ('ADC','SBC','AND','OR','XOR') else (0,)
        for a,b,c in product(range(256),range(256),carries):
            got=alu(a,b,op,c)
            assert got==expected(a,b,op,c),(op,a,b,c,got,expected(a,b,op,c))
            cases+=1
    print(f'ALU PASS: {cases:,} exhaustive operation/operand/carry cases')
    # one-hot decode: 4 mutually exclusive bus sources, and an idle state
    for sel in range(5):
        drives=[('A',0x11,sel==0),('B',0x22,sel==1),('ALU',0x33,sel==2),('RAM',0x44,sel==3)]
        got=resolve_bus(drives)
        assert got==([0x11,0x22,0x33,0x44,None][sel])
    try:
        resolve_bus([('ROM',0x55,True),('RAM',0xaa,True)])
        raise AssertionError('Contention was not detected')
    except RuntimeError as e:
        assert 'BUS_CONTENTION' in str(e)
    print('BUS PASS: one-hot source selection and deliberately injected contention detected')
    # Model registers, reset, write-enable and flags for randomized instruction sequences.
    rng=random.Random(0x15A1)
    a=b=z=c=0
    steps=100_000
    for _ in range(steps):
        action=rng.randrange(10)
        if action==0: a=b=z=c=0 # synchronous conceptual reset
        elif action==1: a=rng.randrange(256)
        elif action==2: b=rng.randrange(256)
        else:
            op=('ADD','ADC','SUB','SBC','AND','OR','XOR')[action-3]
            olda,oldc=a,c
            a,c,z=alu(a,b,op,c)
            assert (a,c,z)==expected(olda,b,op,oldc)
            assert z==int(a==0) and 0<=a<=255 and c in (0,1)
            if op in ('AND','OR','XOR'): assert c==oldc
    print(f'STATE PASS: {steps:,} deterministic randomized register/flag transitions')
    print('LIMIT: functional models only. No pin-level netlist, propagation delays, SPICE, or PCB sign-off.')
if __name__=='__main__': run()
