"""Ideal Boolean gate model, no propagation delays."""
def add4(a,b,c):
 r=0
 for i in range(4):
  x=(a>>i)&1;y=(b>>i)&1;p=x^y
  r|=(p^c)<<i;c=(x&y)|(p&c)
 return r,c

def alu(a,b,op,old_c):
 sub=op in ('SUB','CMP'); mask=255 if sub else 0
 lo,c=add4(a&15,(b^mask)&15,int(sub));hi,c=add4(a>>4,(b^mask)>>4,c)
 outputs={'ADD':lo|(hi<<4),'SUB':lo|(hi<<4),'CMP':lo|(hi<<4),'AND':a&b,'OR':a|b,'XOR':a^b,'SHL':(a<<1)&255,'SHR':a>>1}
 v=outputs[op]
 return v,int(v==0),c if op in ('ADD','SUB','CMP') else a>>7 if op=='SHL' else a&1 if op=='SHR' else old_c

def test():
 n=0
 for a in range(256):
  for b in range(256):
   for op in ('ADD','SUB','CMP','AND','OR','XOR','SHL','SHR'):
    raw={'ADD':a+b,'SUB':a-b,'CMP':a-b,'AND':a&b,'OR':a|b,'XOR':a^b,'SHL':a*2,'SHR':a//2}[op]
    for old in (0,1):
     c=int(raw>255) if op=='ADD' else int(a>=b) if op in ('SUB','CMP') else int(a>=128) if op=='SHL' else a%2 if op=='SHR' else old
     assert alu(a,b,op,old)==(raw%256,int(raw%256==0),c)
     n+=1
 print(n)
if __name__=='__main__':test()
