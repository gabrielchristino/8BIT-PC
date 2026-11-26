"""Ideal common-clock nibble model; no electrical timing."""
def count(q,down,enable):
    n=[(q>>(4*i))&15 for i in range(4)]
    terminal=0 if down else 15
    e=[enable and all(v==terminal for v in n[:i]) for i in range(4)]
    return sum(((v+(-1 if down else 1))&15 if e[i] else v)<<(4*i) for i,v in enumerate(n))
def stack_ok(sp,push,boot):
    floor=0x4000 if boot else 0
    return floor < sp <= 0x8000 if push else floor <= sp < 0x8000
if __name__=='__main__':
    c=s=0
    for q in range(65536):
        for down in (False,True):
            for en in (False,True):
                assert count(q,down,en)==((q+((-1 if down else 1) if en else 0))&65535); c+=1
        for boot in (False,True):
            for push in (False,True):
                floor=0x4000 if boot else 0
                valid=(q in range(floor+1,0x8001)) if push else (q in range(floor,0x8000))
                assert stack_ok(q,push,boot)==valid
                if valid:
                    addr=count(q,True,True) if push else q
                    assert floor<=addr<0x8000
                s+=1
    print(f'counter_cases={c}, stack_cases={s}, failures=0')
