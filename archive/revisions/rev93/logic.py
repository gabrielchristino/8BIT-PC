"""Ideal digital models, no propagation delays or electrical levels."""
def hc163(q, clr_n, load_n, enp, ent, d):
    return 0 if not clr_n else d if not load_n else (q+1)&15 if enp and ent else q

def chain(q,n,clear=False,load=None,enable=True):
    out=0; carry=enable
    for i in range(n):
        old=(q>>(4*i))&15
        out |= hc163(old,not clear,load is None,enable,carry,0 if load is None else (load>>(4*i))&15)<<(4*i)
        carry=carry and old==15
    return out

def hc157(a,b,sel,g_n): return 0 if g_n else b if sel else a

def hc377(q,d,e_n): return q if e_n else d

def hc245(a,b,dir,oe_n): return (None,None) if oe_n else (None,a) if dir else (b,None)

def raster(h,v):
    wrap=h==199
    return chain(h,2,clear=wrap),chain(v,3,clear=wrap and v==524,enable=wrap)
