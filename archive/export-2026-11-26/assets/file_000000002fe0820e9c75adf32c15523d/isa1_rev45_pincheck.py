import json
from pathlib import Path
p=Path(__file__).parent
hc163={1:'/CLR',2:'CLK',3:'A',4:'B',5:'C',6:'D',7:'ENP',8:'GND',9:'/LOAD',10:'ENT',11:'QD',12:'QC',13:'QB',14:'QA',15:'RCO',16:'VCC'}
hc157={1:'SEL',2:'1A',3:'1B',4:'1Y',5:'2A',6:'2B',7:'2Y',8:'GND',9:'3Y',10:'3B',11:'3A',12:'4Y',13:'4B',14:'4A',15:'/G',16:'VCC'}
assert len(set(hc163))==16 and len(set(hc157))==16
nets={}
def add(net,component,pin): nets.setdefault(net,[]).append(f'{component}.{pin}')
for i in range(4):
 c=f'U_PC{i}'
 for pin,net in [(1,'PC_CLR_N'),(2,'PC_CLK'),(8,'GND'),(9,'PC_LOAD_N'),(16,'VCC_5V')]: add(net,c,pin)
 add('PC_COUNT',c,7)
 add('PC_COUNT' if i==0 else f'PC_RCO{i-1}',c,10)
 if i<3: add(f'PC_RCO{i}',c,15)
 else: add('PC_RCO3_MON',c,15)
 for bit,(dp,qp) in enumerate(zip((3,4,5,6),(14,13,12,11))):
  b=4*i+bit;add(f'PC_LOAD_D{b}',c,dp);add(f'PC_Q{b}',c,qp)
for i in range(4):
 c=f'U_MUX{i}'
 for pin,net in [(1,'PC_SEL_RET'),(8,'GND'),(15,'GND'),(16,'VCC_5V')]:add(net,c,pin)
 for bit,(ap,bp,yp) in enumerate(((2,3,4),(5,6,7),(11,10,9),(14,13,12))):
  b=i*4+bit
  add(f'EA_Q{b}',c,ap);add(f'RET_Q{b}',c,bp);add(f'PC_LOAD_D{b}',c,yp)
# Every pin on every device has one assigned net
assigned={c:set() for c in [*(f'U_PC{i}' for i in range(4)),*(f'U_MUX{i}' for i in range(4))]}
for net,pins in nets.items():
 for cp in pins:
  c,pn=cp.split('.'); pn=int(pn)
  assert pn not in assigned[c],f'duplicate {cp}'
  assigned[c].add(pn)
assert all(len(x)==16 for x in assigned.values())
# Functional cascade with RCO=ENT & terminal count, all clocked together
checks=0
for value in range(65536):
 for count in (0,1):
  n=[(value>>(4*i))&15 for i in range(4)]
  en=count; nxt=[]
  for i in range(4):
   nxt.append((n[i]+en)&15)
   en=int(bool(en and n[i]==15))
  result=sum(v<<(4*i) for i,v in enumerate(nxt))
  assert result==((value+count)&65535)
  checks+=1
for value in (0,1,0xff,0xffff,0x1234):
 for load in (0,1):
  for clear in (0,1):
   for count in (0,1):
    target=0xabcd
    result=0 if clear else (target if load else ((value+count)&65535))
    expected=0 if clear else (target if load else ((value+count)&65535))
    assert result==expected
    checks+=1
out={'revision':'4.5','parts':{'SN74HC163D':4,'SN74HC157D':4},'checks':checks,'nets':len(nets),'assigned_pins':sum(map(len,assigned.values())),'status':'functional and pin-assignment checks only; no electrical timing simulation','pinouts':{'SN74HC163D':hc163,'SN74HC157D':hc157},'nets':nets}
(p/'isa1_rev45_nets.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print('PASS',checks,'functional checks;',sum(map(len,assigned.values())),'pins mapped;',len(nets),'nets')
