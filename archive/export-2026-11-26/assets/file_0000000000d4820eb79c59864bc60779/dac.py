from itertools import product
R={3:(3240,1620,806),2:(1380,698)} # LSB first

def voltage(code,rs,load=75,high=5,low=0,rout=0):
    gs=[1/(r+rout) for r in rs]
    return sum(g*(high if code>>i&1 else low) for i,g in enumerate(gs))/(1/load+sum(gs))

def run():
    for n,rs in R.items():
        levels=[voltage(c,rs) for c in range(2**n)]
        print(n,'bits',rs,'levels', [round(v,5) for v in levels])
        for tol in (.01,.05):
            lo=10;hi=-10;step=10;err=0;count=0
            for signs in product((-1,1),repeat=n):
                rr=[r*(1+tol*s) for r,s in zip(rs,signs)]
                for supply,load,ro in product((4.75,5.25),(71.25,78.75),(0,30)):
                    vs=[voltage(c,rr,load,supply,rout=ro) for c in range(2**n)]
                    lo=min(lo,vs[-1]);hi=max(hi,vs[-1]);step=min(step,min(b-a for a,b in zip(vs,vs[1:])))
                    err=max(err,max(abs(v-.7*c/(2**n-1)) for c,v in enumerate(vs)));count+=len(vs)
            print('tol',tol,'cases',count,'white range',lo,hi,'min step',step,'max error',err)
            assert step>0
    for c in range(256):
        rgb=(voltage(c>>5,R[3]),voltage((c>>2)&7,R[3]),voltage(c&3,R[2]))
        assert all(0<=v<=.71 for v in rgb)
    print('256 RGB codes verified; nominal white current',sum(voltage((1<<n)-1,R[n])/75 for n in (3,3,2)))
    print('Conservative pin current upper bound',5.25/(698*.95))
if __name__=='__main__':run()
