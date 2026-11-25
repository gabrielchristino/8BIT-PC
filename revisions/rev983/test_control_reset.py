from integrated import ResetAbort
from control import ControlMachine as AsyncMachine
import json
ops=[0,0x10,0x11,*range(0x20,0x27),*range(0x30,0x37),0x40,0x41,0x42,*range(0x50,0x55),255]
def fixture(op,cp):
 m=AsyncMachine(cp,1,0);m.boot=False;m.pc=0x4000;m.x=0x8000;m.a=0x55;m.b=3;m.sp=0x7ffc;m.h=150
 m.ram[0x4000:0x4003]=bytes([op,0,0x80 if op in (0x30,0x31,0x32) else 0x40]);m.ram[0x7ffc:0x7ffe]=b'\x00\x40'
 m.rom[:3]=bytes([0x40,0x40,0xc0]);m.rom[0x40]=255
 return m
def snapshot(m):return (m.pc,m.sp,m.a,m.b,m.x,m.z,m.c,m.vb,m.eb,m.boot,m.halt,m.row,bytes(m.ram),bytes(m.vram),bytes(m.rom),m.writes,m.transactions)
n=0
for op in ops:
 for cp in (1,3,5):
  baseline=fixture(op,cp);events=list(baseline.micro(2))
  for cut in range(len(events)+1):
   for power in (False,True):
    m=fixture(op,cp);g=m.micro(2)
    for _ in range(cut):next(g)
    if power:m.power_good=False
    else:m.reset()
    try:next(g)
    except ResetAbort:pass
    else:raise AssertionError((op,cut,power))
    assert (m.pc,m.sp,m.a,m.b,m.x,m.z,m.c,m.row)==(0,0x8000,0,0,0,0,0,0)
    assert not any((m.req,m.ack,m.r1,m.r2,m.a1,m.a2))
    before=snapshot(m)
    try:next(g)
    except StopIteration:pass
    assert snapshot(m)==before
    m.power_good=True;m.step();assert m.pc==0xc040;m.step();assert m.halt
    n+=1
m=fixture(0,1)
try:m.write(0x4000,1)
except RuntimeError:pass
else:raise AssertionError('direct write')
r={'opcodes':len(ops),'reset_cases':n,'failures':0};print(r);open('control_reset_results.json','w').write(json.dumps(r))
