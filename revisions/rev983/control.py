from alu_gates import alu as gate_alu
"""Candidate horizontal control fields; logical datapath, not electrical netlist."""
from microcode import ROM,NAMES,EncodedCPU,EncodedMachine
from integrated import AsyncMachine
from cpu import CPU
# Each field selects exactly one source or destination. Bus transactions block until commit.
FIELDS=[('addr',3,['-','PC','EA','X','SP','SP-1']),('src',3,['-','A','PCH','PCL','MDR','ALU']),('dst',3,['-','A','B','EAL','EAH','IR']),('mem',2,['-','RD','WR']),('pc',2,['-','INC','EA','EA_Z','EA_NZ']),('sp',2,['-','INC','DEC']),('x',2,['-','EA','INC','DEC']),('alu',4,['-','ADD','SUB','AND','OR','XOR','SHL','SHR','CMP']),('flags',2,['-','Z','ZC']),('end',1,['-','END']),('halt',1,['-','HALT'])]
# PC needs five encodings.
FIELDS[4]=('pc',3,FIELDS[4][2])
def pack(**kw):
 w=shift=0
 for k,b,vals in FIELDS:
  w|=vals.index(kw.pop(k,'-'))<<shift;shift+=b
 assert not kw
 return w
def unpack(w):
 out={}
 for k,b,vals in FIELDS:out[k]=vals[w&((1<<b)-1)];w>>=b
 assert not w
 return out
def rd(addr,dst,**kw):return [pack(addr=addr,mem='RD'),pack(src='MDR',dst=dst,**kw)]
def fetch(dst):return rd('PC',dst,pc='INC',**({'flags':'Z'} if dst=='A' else {}))
def push(src):return [pack(addr='SP-1',src=src,mem='WR'),pack(sp='DEC')]
def pop(dst):return rd('SP',dst,sp='INC',**({'flags':'Z'} if dst=='A' else {}))
FETCH=fetch('IR'); TABLE={}
for op,seq in ROM.items():
 out=[]
 for w in seq:
  n=NAMES[w>>8];arg=w&255
  if n.startswith('FETCH_'):out+=fetch({'A':'A','B':'B','LO':'EAL','HI':'EAH'}[n[6:]])
  elif n.startswith('X_'):out.append(pack(x={'LOAD':'EA','INC':'INC','DEC':'DEC'}[n[2:]]))
  elif n.startswith('READ_'):out+=rd(n[5:],'A',flags='Z')
  elif n.startswith('WRITE_'):out.append(pack(addr=n[6:],src='A',mem='WR'))
  elif n=='JUMP':out.append(pack(pc=['EA','EA_Z','EA_NZ'][arg]))
  elif n.startswith('PUSH_'):out+=push({'H':'PCH','L':'PCL','A':'A'}[n[5:]])
  elif n.startswith('POP_'):out+=pop({'LO':'EAL','HI':'EAH','A':'A'}[n[4:]])
  elif n=='ALU':
   alu={0x20:'ADD',0x21:'SUB',0x22:'AND',0x23:'OR',0x24:'XOR',0x25:'SHL',0x26:'SHR',0x54:'CMP'}[arg]
   out.append(pack(alu=alu,src='ALU',dst='-' if alu=='CMP' else 'A',flags='Z' if alu in ('AND','OR','XOR') else 'ZC'))
  elif n=='END':out.append(pack(end='END'))
  elif n=='HALT':out.append(pack(halt='HALT'))
  else:raise AssertionError(n)
 TABLE[op]=out
class ControlCPU(CPU):
 def micro(self,d=0):
  ea=mdr=ir=0
  def execute(w):
   nonlocal ea,mdr,ir
   q=unpack(w); a,b=self.a,self.b; alu=q['alu']; carry=self.c
   if alu!='-':
    v,_,carry=gate_alu(a,b,alu,carry)
   else:v=0
   val={'-':0,'A':a,'PCH':self.pc>>8,'PCL':self.pc&255,'MDR':mdr,'ALU':v&255}[q['src']]
   if q['mem']!='-':
    if q['addr']=='SP-1' and (not 0<self.sp<=0x8000 or self.boot and self.sp<=0x4000):raise ValueError('stack overflow')
    if q['addr']=='SP' and (not 0<=self.sp<0x8000 or self.boot and self.sp<0x4000):raise ValueError('stack underflow')
    addr={'PC':self.pc,'EA':ea,'X':self.x,'SP':self.sp,'SP-1':self.sp-1}[q['addr']]
    r=yield from self.bus(addr,None if q['mem']=='RD' else val,d)
    if q['mem']=='RD':mdr=r
   dst=q['dst']
   if dst=='A':self.a=val
   elif dst=='B':self.b=val
   elif dst=='EAL':ea=(ea&0xff00)|val
   elif dst=='EAH':ea=(ea&255)|(val<<8)
   elif dst=='IR':ir=val
   if q['flags']!='-':self.z=int(val==0)
   if q['flags']=='ZC':self.c=carry
   p=q['pc']
   if p=='INC':self.pc=(self.pc+1)&65535
   elif p=='EA' or p=='EA_Z' and self.z or p=='EA_NZ' and not self.z:self.pc=ea
   if q['sp']!='-':self.sp+=1 if q['sp']=='INC' else -1
   if q['x']!='-':self.x=ea if q['x']=='EA' else (self.x+(1 if q['x']=='INC' else -1))&65535
   if q['halt']=='HALT':self.halt=True
   yield ('CONTROL',w,None)
  for w in FETCH:yield from execute(w)
  if ir not in TABLE:self.halt=True;yield ('ILLEGAL',ir,None);return
  for w in TABLE[ir]:yield from execute(w)
class ControlMachine(AsyncMachine,ControlCPU):pass
