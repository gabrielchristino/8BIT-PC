import json, random
from pathlib import Path
root=Path(__file__).parent
checks=0

def xor_and_increment(x):
    carry=1; out=0
    for bit in range(16):
        b=(x>>bit)&1
        out|=(b^carry)<<bit
        carry &= b
    return out

def adder_nibbles(x, subtract=False):
    # HC283 B nibble 0000 and Cin=1 for +1; B nibble 1111 and Cin=0 for -1.
    carry=0 if subtract else 1
    b=15 if subtract else 0
    out=0
    for n in range(4):
        total=((x>>(4*n))&15)+b+carry
        out|=(total&15)<<(4*n)
        carry=(total>>4)&1
    return out

for x in range(65536):
    assert xor_and_increment(x)==((x+1)&65535)
    assert adder_nibbles(x)==((x+1)&65535)
    assert adder_nibbles(x,True)==((x-1)&65535)
    checks+=3

# Counter cascade model: each 4-bit digit counts when all lower nibbles are 0xF.
def counter_increment(x):
    y=x
    for n in range(4):
        mask=(1<<(4*n))-1
        if (x&mask)==mask:
            nib=(x>>(4*n))&15
            y=(y&~(15<<(4*n)))|(((nib+1)&15)<<(4*n))
    return y
for x in range(65536):
    assert counter_increment(x)==((x+1)&65535)
    checks+=1

# Validate 16-bit CALL/RET stack pointer direction and wrap independently.
rng=random.Random(410)
for _ in range(50000):
    sp=rng.randrange(65536)
    assert adder_nibbles(adder_nibbles(sp,True),False)==sp
    checks+=1

result={
 'revision':'4.1', 'status':'behavioral_only', 'checks':checks,
 'all_passed':True,
 'pc_283':{'hc283':4,'registers_not_included':True},
 'pc_xor_and':{'hc86':4,'hc08':4,'xor_gates_used':16,'and_gates_used':14,'registers_not_included':True},
 'pc_counter':{'counter_4bit':4,'cascade_logic_required':True,'counter_part_and_timing_unverified':True},
 'sp_bidirectional_283':{'hc283':4,'B_all_bits':'direction_decrement','carry_in':'not_direction_decrement','requires_direction_buffer_and_timing_validation':True},
 'timing_or_power_validated':False
}
(root/'isa1_rev41_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,ensure_ascii=False))
