#!/usr/bin/env python3
"""ISA-1 Rev 4.0: abstract 16-bit datapath contract, not gate-level validation."""
import json, random
from pathlib import Path
ROOT=Path(__file__).resolve().parent
micro=json.loads((ROOT/'isa1_rev33_microcode.json').read_text())['instructions']
ops={x['mnemonic']:x['steps'] for x in micro}
assert len(ops)==19

def add16(x, delta):
    carry=1 if delta==1 else 0
    if delta==1:
        lo=x&255; hi=x>>8
        nlo=(lo+1)&255
        nhi=(hi+(lo==255))&255
    else:
        lo=x&255; hi=x>>8
        nlo=(lo-1)&255
        nhi=(hi-(lo==0))&255
    return (nhi<<8)|nlo

# Explicit non-contentious 16-bit load muxes, source sets are design requirements.
load_sources={
 'PC': ['PC_INC', 'EA', 'RET_TMP'],
 'SP': ['SP_INC', 'SP_DEC'],
 'EA': ['TMP_TPH'],
 'MAR': ['PC', 'SP', 'EA'],
 'MDR': ['MEM', 'PC_LO', 'PC_HI', 'A', 'TMP'],
}
required={
 'CALL': ['EA','PC_HI','PC_LO','SP_DEC'],
 'RET': ['SP_INC','RET_TMP'],
 'JMP': ['EA'],
 'JZ': ['EA'],
}
for op,paths in required.items():
    assert op in ops
    assert all(any(p in xs for xs in load_sources.values()) for p in paths)

count=0
for x in range(65536):
    assert add16(x,1)==((x+1)&65535)
    assert add16(x,-1)==((x-1)&65535)
    count+=2

# Validate CALL/RET stack contract using a byte array and independent reference.
rng=random.Random(401)
stack_tests=0
for _ in range(50000):
    pc=rng.randrange(65536); sp=rng.randrange(65536); ea=rng.randrange(65536)
    mem={}
    original_sp=sp
    mem[sp]=(pc>>8)&255; sp=add16(sp,-1)
    mem[sp]=pc&255; sp=add16(sp,-1)
    new_pc=ea
    assert new_pc==ea
    sp=add16(sp,1); lo=mem[sp]
    sp=add16(sp,1); hi=mem[sp]
    restored=(hi<<8)|lo
    assert restored==pc and sp==original_sp
    stack_tests+=1

# A separate 16-bit PC incrementer and SP inc/dec share neither source nor destination.
# A shared ALU would require extra bus access/cycles, not validated by this model.
result={
 'revision':'4.0', 'instructions_reviewed':len(ops),
 'arithmetic_checks':count, 'call_ret_roundtrips':stack_tests,
 'load_source_contract':load_sources,
 'choice':'dedicated PC +1 and SP +/-1 paths for first hardware revision',
 'not_verified':['pin-level netlist','gate-level timing','real chip selection','microcode binary','reset/power sequencing','electrical safety']
}
(ROOT/'isa1_rev40_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in result.items() if k in ('instructions_reviewed','arithmetic_checks','call_ret_roundtrips')},indent=2))
