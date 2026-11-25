from control import FETCH,TABLE,pack,unpack
# 13-bit address: fetch bank bit 12, opcode bits 11:4, step bits 3:0.
SAFE=pack(halt='HALT')
ROM=[SAFE]*8192
for op,words in TABLE.items():
 for i,w in enumerate(words):ROM[op*16+i]=w
for i,w in enumerate(FETCH):ROM[4096+i]=w
class Sequencer:
 def __init__(self):self.reset()
 def reset(self):self.fetch=True;self.ir=0;self.step=0;self.halted=False
 @property
 def address(self):return (4096 if self.fetch else self.ir*16)+self.step
 @property
 def word(self):return SAFE if self.halted else ROM[self.address]
 def edge(self,ready=True,run=True,reset=False,opcode=0):
  if reset:self.reset();return False
  if not run or not ready or self.halted:return False
  q=unpack(self.word)
  if q['halt']=='HALT':self.halted=True
  elif self.fetch and self.step==1:self.ir=opcode;self.fetch=False;self.step=0
  elif q['end']=='END':self.fetch=True;self.step=0
  else:self.step+=1
  return True
if __name__=='__main__':
 for lane in range(4):open(f'control_lane{lane}.bin','wb').write(bytes((w>>(8*lane))&255 for w in ROM))
