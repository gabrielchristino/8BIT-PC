"""Encoded abstract micro-operations, not physical control signals."""
from cpu import CPU
from integrated import AsyncMachine
# 16-bit word: operation [15:8], argument [7:0].
NAMES='END FETCH_A FETCH_B FETCH_LO FETCH_HI X_LOAD X_INC X_DEC ALU READ_EA WRITE_EA READ_X WRITE_X JUMP PUSH_H PUSH_L POP_LO POP_HI PUSH_A POP_A HALT'.split()
ID={n:i for i,n in enumerate(NAMES)}
def word(n,arg=0):return ID[n]<<8|arg
T={0:[],0x10:['FETCH_A'],0x11:['FETCH_B'],0x30:['FETCH_LO','FETCH_HI','READ_EA'],0x31:['FETCH_LO','FETCH_HI','WRITE_EA'],0x32:['FETCH_LO','FETCH_HI','X_LOAD'],0x33:['READ_X'],0x34:['WRITE_X'],0x35:['X_INC'],0x36:['X_DEC'],0x40:['FETCH_LO','FETCH_HI',('JUMP',0)],0x41:['FETCH_LO','FETCH_HI',('JUMP',1)],0x42:['FETCH_LO','FETCH_HI',('JUMP',2)],0x50:['FETCH_LO','FETCH_HI','PUSH_H','PUSH_L',('JUMP',0)],0x51:['POP_LO','POP_HI',('JUMP',0)],0x52:['PUSH_A'],0x53:['POP_A'],255:['HALT']}
for op in [*range(0x20,0x27),0x54]:T[op]=[('ALU',op)]
ROM={op:[word(*v) if isinstance(v,tuple) else word(v) for v in seq]+[word('END')] for op,seq in T.items()}
class EncodedCPU(CPU):
 def micro(self,d=0):
  op=yield from self.fetch(d);lo=hi=0
  if op not in ROM:
   self.halt=True;yield ("ILLEGAL",op,None);return
  for w in ROM[op]:
   n=NAMES[w>>8];arg=w&255;ea=lo|(hi<<8)
   if n=='END':yield ('END',None,None);return
   if n=='FETCH_A':self.seta((yield from self.fetch(d)))
   elif n=='FETCH_B':self.b=yield from self.fetch(d)
   elif n=='FETCH_LO':lo=yield from self.fetch(d)
   elif n=='FETCH_HI':hi=yield from self.fetch(d)
   elif n=='X_LOAD':self.x=ea
   elif n=='X_INC':self.x=(self.x+1)&65535
   elif n=='X_DEC':self.x=(self.x-1)&65535
   elif n=='ALU':
    a,b=self.a,self.b
    if arg in (0x20,0x21,0x54):
     v=a+b if arg==0x20 else a-b;self.c=int(v>255 if arg==0x20 else v>=0)
     if arg==0x54:self.z=int((v&255)==0)
     else:self.seta(v)
    elif arg==0x25:self.c=a>>7;self.seta(a<<1)
    elif arg==0x26:self.c=a&1;self.seta(a>>1)
    else:self.seta({0x22:a&b,0x23:a|b,0x24:a^b}[arg])
   elif n in ('READ_EA','READ_X'):self.seta((yield from self.bus(ea if n=='READ_EA' else self.x,delay=d)))
   elif n in ('WRITE_EA','WRITE_X'):yield from self.bus(ea if n=='WRITE_EA' else self.x,self.a,d)
   elif n=='JUMP':
    if arg==0 or (arg==1 and self.z) or (arg==2 and not self.z):self.pc=ea
   elif n=='PUSH_H':yield from self.push(self.pc>>8,d)
   elif n=='PUSH_L':yield from self.push(self.pc&255,d)
   elif n=='PUSH_A':yield from self.push(self.a,d)
   elif n=='POP_LO':lo=yield from self.pop(d)
   elif n=='POP_HI':hi=yield from self.pop(d)
   elif n=='POP_A':self.seta((yield from self.pop(d)))
   elif n=='HALT':self.halt=True
   else:raise AssertionError(n)
class EncodedMachine(AsyncMachine,EncodedCPU):pass
if __name__=='__main__':
 import json
 open('microcode.json','w').write(json.dumps({f'{k:02X}':[f'{w:04X}' for w in v] for k,v in ROM.items()},indent=2))
