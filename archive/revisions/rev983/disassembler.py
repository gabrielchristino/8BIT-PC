from assembler import OPS,assemble
CANON={v:k for k,v in OPS.items() if k!='HLT'}
def disassemble(data):
 i=0
 while i<len(data):
  op=data[i];i+=1
  if op not in CANON:raise ValueError(f'invalid opcode {op:02X}')
  name=CANON[op];size=1 if op in (16,17) else 2 if name.endswith(('@','#')) else 0
  if i+size>len(data):raise ValueError('truncated operand')
  if size:
   v=int.from_bytes(data[i:i+size],'little');i+=size
   name=name.replace('@','')+f'{v:0{size*2}X}h'
  yield name
if __name__=='__main__':
 import json
 n=0
 for op,name in CANON.items():
  size=1 if op in (16,17) else 2 if name.endswith(('@','#')) else 0
  for v in range(1<<(8*size)):
   b=bytes([op])+v.to_bytes(size,'little');assert assemble('\n'.join(disassemble(b)))==b;n+=1
 print(n);open('disassembler_results.json','w').write(json.dumps({'roundtrips':n,'failures':0}))
