from integrated import AsyncMachine
import json
n=steps=transactions=0
for cp in (1,2,3,5,11):
 for vp in (1,2,3):
  for phase in range(cp):
   for h in (0,159,161,192,196,199):
    m=AsyncMachine(cp,vp,phase);m.boot=False;m.h=h
    # LDX 8000; LDA 55; STA [X]; INX; LDA AA; STA [X]; DEX; LDA [X]; CALL 0020; HLT
    p=bytes.fromhex('32 00 80 10 55 34 35 10 AA 34 36 33 50 20 00 FF');m.ram[:len(p)]=p
    m.ram[32:36]=bytes.fromhex('35 33 51 FF')
    for _ in range(30):
     m.step(1)
     if m.halt:break
    assert m.halt and m.a==0xaa and m.x==0x8001 and m.sp==0x8000 and m.pc==16
    assert m.vram[:2]==b'\x55\xaa' and m.transactions==4 and m.writes==4
    n+=1;steps+=m.t;transactions+=m.transactions
r=dict(programs=n,ticks=steps,vram_transactions=transactions,failures=0);print(r);open('async_results.json','w').write(json.dumps(r,indent=2))
