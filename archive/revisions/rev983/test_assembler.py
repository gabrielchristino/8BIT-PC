from assembler import *
from microcode import EncodedMachine,ROM
from pathlib import Path
import json
assert set(OPS.values())==set(ROM)
assert assemble('JMP END\nNOP\nEND: HALT',0x4000)==bytes([0x40,4,0x40,0,255])
for s in ('LDA #256','JMP MISSING','X: NOP\nX: HALT','JMP -1'):
 try:assemble(s)
 except (ValueError,KeyError):pass
 else:raise AssertionError(s)
p=assemble(Path('diagnostic.asm').read_text(),0x4000);Path('diagnostic.bin').write_bytes(p)
for cp in (1,3,5):
 m=EncodedMachine(cp,2,0);m.boot=False;m.pc=0x4000;m.ram[0x4000:0x4000+len(p)]=p
 for _ in range(200):
  if m.halt:break
  m.step()
 assert m.halt and m.ram[0x5001]==0xa5 and m.sp==0x8000 and m.vram[:3]==bytes([224,28,3])
 assert all(m.vram[b*8192]==85 for b in (1,2,3))
r={'opcodes':len(set(OPS.values())),'diagnostic_bytes':len(p),'diagnostic_runs':3,'invalid_inputs_rejected':4};print(r);Path('assembler_results.json').write_text(json.dumps(r))
