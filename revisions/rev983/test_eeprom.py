from eeprom import Programmer
import itertools,json
n=0
for a in range(32768):
 for p,r,x in itertools.product((False,True),repeat=3):
  m=Programmer(bytearray(32768));ok=m.request(a,85,power=p,run=r,executing_ram=x)
  assert ok==(p and r and x and a>=0x7800)
  if ok:
   assert not m.request(a,0,power=True,run=True,executing_ram=True)
   assert m.complete(power=True,run=True) and m.rom[a]==85
  else:assert not m.trace
  n+=1
for p,r in itertools.product((False,True),repeat=2):
 m=Programmer(bytearray(32768));assert m.request(0x7800,85,power=True,run=True,executing_ram=True);assert m.complete(power=p,run=r)==(p and r)
m=Programmer(bytearray(32768));m.request(0x7800,85,power=True,run=True,executing_ram=True);m.reset();assert not m.complete(power=True,run=True)
r={'permission_cases':n,'completion_cases':4,'reset_cases':1,'failures':0};print(r);open('eeprom_program_results.json','w').write(json.dumps(r))
