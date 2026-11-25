"""Two-pass assembler; explicit origin, little-endian operands."""
import re,sys
OPS={'NOP':0,'LDA #':0x10,'LDB #':0x11,'ADD':0x20,'SUB':0x21,'AND':0x22,'OR':0x23,'XOR':0x24,'SHL':0x25,'SHR':0x26,'LDA @':0x30,'STA @':0x31,'LDX #':0x32,'LDA [X]':0x33,'STA [X]':0x34,'INX':0x35,'DEX':0x36,'JMP @':0x40,'JZ @':0x41,'JNZ @':0x42,'CALL @':0x50,'RET':0x51,'PUSH':0x52,'POP':0x53,'CMP':0x54,'HALT':255,'HLT':255}
def assemble(source,origin=0):
 labels={};items=[];pc=origin
 for line in source.upper().splitlines():
  line=line.split(';')[0].strip()
  if not line:continue
  if ':' in line:
   label,line=map(str.strip,line.split(':',1))
   if not re.fullmatch('[A-Z_][A-Z0-9_]*',label) or label in labels:raise ValueError('invalid/duplicate label '+label)
   labels[label]=pc
  if not line:continue
  parts=line.split(None,1);mn=parts[0];arg=parts[1].strip() if len(parts)>1 else ''
  key=mn if not arg else mn+' '+('[X]' if arg=='[X]' else '#' if arg.startswith('#') else '@')
  op=OPS[key];size=0 if not arg or arg=='[X]' else 1 if op in (16,17) else 2
  items.append((op,size,arg.lstrip('#')));pc+=1+size
  if pc>65536:raise ValueError('address overflow')
 out=bytearray()
 for op,size,arg in items:
  out.append(op)
  if size:
   v=labels[arg] if arg in labels else int(arg[:-1],16) if arg.endswith('H') else int(arg,0)
   if not 0<=v<1<<(size*8):raise ValueError('operand overflow')
   out.extend(v.to_bytes(size,'little'))
 return bytes(out)
if __name__=='__main__':
 from pathlib import Path
 Path(sys.argv[2]).write_bytes(assemble(Path(sys.argv[1]).read_text(),int(sys.argv[3],0) if len(sys.argv)>3 else 0))
