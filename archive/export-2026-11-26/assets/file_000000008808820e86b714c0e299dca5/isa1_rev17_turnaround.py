"""ISA-1 Rev17: bounded event simulation of bus turnaround. No vendor timing models.
Run: python3 isa1_rev17_turnaround.py
"""
from itertools import product

# Illustrative, deliberately assumed ranges in arbitrary time units.
# They are NOT 74HC/SRAM specifications.
OFF_DELAYS = range(0, 21)
ON_DELAYS = range(0, 21)
GUARDS = (0, 10, 20, 21)

# A transition requests old driver OFF at t=0 and new driver ON at t=guard.
# At equal timestamps, assume both are active (conservative boundary).
def overlap(old_off, new_on, guard):
    return old_off >= guard + new_on

def test_turnaround():
    total = 0
    failures = {g: 0 for g in GUARDS}
    for old_off, new_on in product(OFF_DELAYS, ON_DELAYS):
        for guard in GUARDS:
            failures[guard] += overlap(old_off, new_on, guard)
            total += 1
    assert failures[0] > 0
    assert failures[10] > 0
    assert failures[20] > 0  # exact boundary counted as unsafe
    assert failures[21] == 0
    return total, failures

# Physical owner of external D[7:0]: none, CPU, SRAM.
# A CPU->SRAM or SRAM->CPU change must pass through idle guard.
PHASE = {
    'IDLE': {'cpu': False, 'ram': False, 'ce_n': 1, 'oe_n': 1, 'we_n': 1},
    'READ': {'cpu': False, 'ram': True, 'ce_n': 0, 'oe_n': 0, 'we_n': 1},
    'WRITE_SETUP': {'cpu': True, 'ram': False, 'ce_n': 0, 'oe_n': 1, 'we_n': 1},
    'WRITE_PULSE': {'cpu': True, 'ram': False, 'ce_n': 0, 'oe_n': 1, 'we_n': 0},
    'WRITE_HOLD': {'cpu': True, 'ram': False, 'ce_n': 0, 'oe_n': 1, 'we_n': 1},
}

def check_phase(name):
    p = PHASE[name]
    assert not (p['cpu'] and p['ram']), name
    assert not (p['oe_n'] == 0 and p['we_n'] == 0), name
    assert p['we_n'] or (p['cpu'] and p['oe_n'] == 1 and p['ce_n'] == 0), name
    return True

def sequence(old, new):
    assert old in ('IDLE','READ','WRITE_HOLD')
    assert new in ('IDLE','READ','WRITE_SETUP')
    # guard is mandatory even for back-to-back READ/READ: conservative baseline
    return [old, 'IDLE', new] if old != 'IDLE' else ['IDLE', new]

def test_control():
    checks = 0
    for name in PHASE:
        check_phase(name); checks += 1
    for old, new in product(('IDLE','READ','WRITE_HOLD'), ('IDLE','READ','WRITE_SETUP')):
        path = sequence(old,new)
        for p in path:
            check_phase(p); checks += 1
        if old != 'IDLE': assert path[1] == 'IDLE'
    assert ['WRITE_SETUP','WRITE_PULSE','WRITE_HOLD'] == list(PHASE)[2:]
    # Reset must disable CPU drivers, SRAM output and SRAM write regardless of state.
    assert PHASE['IDLE'] == {'cpu': False,'ram':False,'ce_n':1,'oe_n':1,'we_n':1}
    return checks

if __name__ == '__main__':
    total, failures = test_turnaround()
    checks = test_control()
    print('PASS: bounded event timing scenarios:', total)
    print('Overlap cases by guard (arbitrary units):', failures)
    print('PASS: phase/control assertions:', checks)
    print('IMPORTANT: abstract delay ranges only; real component timing and PCB NOT validated')
