from fractions import Fraction
from itertools import product
slot=Fraction(2_000_000_000,25_175_000)
print('Slot ns:',float(slot))
n=0
for mem in (10,12,15,20,55,70):
    margins=[]
    for mux,setup,guard in product((8,12,18),(4,6,10),(5,10,15)):
        margin=slot-mem-mux-setup-guard
        margins.append(margin)
        assert (margin>=0)==(mem+mux+setup+guard<=slot)
        n+=1
    print(f'{mem:2} ns: {sum(m>=0 for m in margins)}/27 feasible; worst {float(min(margins)):.3f} ns')
assert 200*525==105000
assert 160*480==76800
print('Cases:',n,'; visible-only blank slots:',105000-76800)
print('Ideal blank-only bytes/s:',float(Fraction(28200*25175000,420000)))
