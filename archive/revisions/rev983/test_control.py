from control import * 
import random,json
rng=random.Random(94)
def state(m):return (m.pc,m.sp,m.a,m.b,m.x,m.z,m.c,m.halt,m.writes,bytes(m.ram),bytes(m.vram))
n=0
for op in ROM:
 for i in range(256):
  a,b=rng.randrange(256),rng.randrange(256);x=rng.choice([0,255,256,65535,0x8000,0x5000]);z,c=rng.randrange(2),rng.randrange(2)
  for cls in (CPU,ControlCPU):
   m=cls();m.boot=False;m.pc=0x4000;m.sp=0x7ffc;m.a=a;m.b=b;m.x=x;m.z=z;m.c=c;m.ram[0x4000:0x4003]=bytes([op,0,0x50]);m.ram[0x7ffc:0x7ffe]=b'\x34\x12';m.step(i%3)
   if cls is CPU:expected=state(m)
   else:assert state(m)==expected,(op,i)
  n+=1
# Verify actual method resolution and compare integrated execution.
assert ControlMachine.__mro__.index(ControlCPU)<ControlMachine.__mro__.index(CPU)
for cls in (AsyncMachine,ControlMachine):
 m=cls(3,2,0);m.boot=False;m.pc=0x4000;m.ram[0x4000:0x400a]=bytes([0x32,0,0x80,0x10,0x55,0x34,0x10,0,0x33,255]);
 while not m.halt:m.step()
 assert m.a==0x55 and m.vram[0]==0x55
r={'opcodes':len(ROM),'words':sum(map(len,TABLE.values())),'differential_cases':n,'integrated_programs':2,'failures':0};print(r);open('control_results.json','w').write(json.dumps(r))
