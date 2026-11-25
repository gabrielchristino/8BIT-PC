from alu_gates import add4,alu
# 8:1 mux per bit, six distinct data sources; arithmetic shared.
def mux_alu(a,b,op,old):
 sub=op in ('SUB','CMP'); inv=b^(255 if sub else 0)
 lo,c=add4(a&15,inv&15,int(sub)); hi,c=add4(a>>4,inv>>4,c)
 sources=(lo|(hi<<4),a&b,a|b,a^b,(a<<1)&255,a>>1,0,0)
 sel={'ADD':0,'SUB':0,'CMP':0,'AND':1,'OR':2,'XOR':3,'SHL':4,'SHR':5}[op]
 out=sum(((sources[sel]>>i)&1)<<i for i in range(8))
 z=int(not any((out>>i)&1 for i in range(8)))
 carry=(c if sel==0 else a>>7 if sel==4 else a&1 if sel==5 else old)
 return out,z,carry
# Four nibble adders: add 0001 or FFFF; modulo 65536.
def step16(x,dec):
 k=65535 if dec else 1; c=0; out=0
 for i in range(0,16,4):
  n,c=add4((x>>i)&15,(k>>i)&15,c);out|=n<<i
 return out

def test():
 n=0
 for a in range(256):
  for b in range(256):
   for op in ('ADD','SUB','CMP','AND','OR','XOR','SHL','SHR'):
    for old in (0,1):
     assert mux_alu(a,b,op,old)==alu(a,b,op,old);n+=1
 m=0
 for x in range(65536):
  for dec in (False,True):
   assert step16(x,dec)==(x+(-1 if dec else 1))%65536;m+=1
 print({'alu_cases':n,'step16_cases':m,'failures':0})
if __name__=='__main__':test()
