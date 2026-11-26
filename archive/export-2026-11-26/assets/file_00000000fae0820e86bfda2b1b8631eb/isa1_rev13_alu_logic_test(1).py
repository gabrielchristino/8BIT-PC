"""ISA-1 Rev13: behavioral gate-block model of two cascaded 74HC283 4-bit adders.
This is NOT a SPICE model or a manufacturer's timing model.
"""

def hc283(a, b, cin):
    total = (a & 15) + (b & 15) + (cin & 1)
    return total & 15, (total >> 4) & 1

def alu_add(a, b, carry_in=0):
    lo, c4 = hc283(a, b, carry_in)
    hi, c8 = hc283(a >> 4, b >> 4, c4)
    result = lo | (hi << 4)
    return result, c8, int(result == 0)

def alu_sub(a, b):
    # A-B = A + (~B) + 1; carry=1 indicates no borrow.
    return alu_add(a, b ^ 255, 1)

def run():
    checks = 0
    for a in range(256):
        for b in range(256):
            for cin in (0, 1):
                result, carry, zero = alu_add(a, b, cin)
                expected = a + b + cin
                assert (result, carry, zero) == (expected & 255, expected >> 8, int((expected & 255) == 0))
                checks += 1
            result, carry, zero = alu_sub(a, b)
            assert (result, carry, zero) == ((a-b)&255, int(a >= b), int(a == b))
            checks += 1
    print(f'PASS: {checks:,} exhaustive logical cases (ADD with carry-in=0/1, SUB)')
    print('Scope: functional arithmetic only; no timing, pin-level, analog, or PCB validation')

if __name__ == '__main__':
    run()
