"""ISA-1 rev3.3 symbolic microcode contract, NOT electrical implementation."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
# Each step is one abstract registered transaction or internal transfer.
F=['FETCH: MAR<-PC','READ: IR<-MEM[MAR], PC<-PC+1']
IMM=['FETCH: MAR<-PC','READ: TMP<-MEM[MAR], PC<-PC+1']
WORD=IMM+['FETCH: MAR<-PC','READ: TPH<-MEM[MAR], PC<-PC+1','INTERNAL: EA<-TPH:TMP']
D={
0x00:('NOP',[]),0x10:('LDA_IMM',IMM+['INTERNAL: A<-TMP, Z<-(A==0)']),
0x11:('LDB_IMM',IMM+['INTERNAL: B<-TMP']),
0x20:('ADD',['INTERNAL: {C,A,Z}<-A+B']),
0x21:('SUB',['INTERNAL: {C,A,Z}<-A-B; C=no-borrow']),
0x22:('AND',['INTERNAL: A,Z<-A&B; C preserved']),
0x23:('OR',['INTERNAL: A,Z<-A|B; C preserved']),
0x24:('XOR',['INTERNAL: A,Z<-A^B; C preserved']),
0x25:('SHL',['INTERNAL: C<-A7, A<-A<<1, Z<-zero']),
0x26:('SHR',['INTERNAL: C<-A0, A<-A>>1, Z<-zero']),
0x30:('LDA_ABS',WORD+['FETCH: MAR<-EA','READ: A<-MEM[MAR], Z<-(A==0)']),
0x31:('STA_ABS',WORD+['FETCH: MAR<-EA, MDR<-A','WRITE: MEM[MAR]<-MDR']),
0x40:('JMP',WORD+['INTERNAL: PC<-EA']),
0x41:('JZ',WORD+['INTERNAL: if Z then PC<-EA']),
0x50:('CALL',WORD+['INTERNAL: RETADDR<-PC','FETCH: MAR<-SP, MDR<-RETADDR.high','WRITE: MEM[MAR]<-MDR, SP<-SP-1','FETCH: MAR<-SP, MDR<-RETADDR.low','WRITE: MEM[MAR]<-MDR, SP<-SP-1','INTERNAL: PC<-EA']),
0x51:('RET',['INTERNAL: SP<-SP+1','FETCH: MAR<-SP','READ: TMP<-MEM[MAR]','INTERNAL: SP<-SP+1','FETCH: MAR<-SP','READ: TPH<-MEM[MAR]','INTERNAL: PC<-TPH:TMP']),
0x52:('PUSH_A',['FETCH: MAR<-SP, MDR<-A','WRITE: MEM[MAR]<-MDR, SP<-SP-1']),
0x53:('POP_A',['INTERNAL: SP<-SP+1','FETCH: MAR<-SP','READ: A<-MEM[MAR], Z<-(A==0)']),
0xff:('HALT',['INTERNAL: HALTED<-1'])}
# Deliberately avoid claiming exact cycle count: FETCH/READ pair denotes abstract phases.
assert len(D)==19
assert len({name for name,_ in D.values()})==len(D)
assert all(0<=op<256 for op in D)
assert all(not ('READ:' in s and 'WRITE:' in s) for _,steps in D.values() for s in steps)
assert all(not ('MEM[' in s and not (s.startswith('READ:') or s.startswith('WRITE:'))) for _,steps in D.values() for s in steps)
assert all(not s.startswith('WRITE:') or ('MAR' in steps[i-1] or steps[i-1].startswith('WRITE:')) for _,steps in D.values() for i,s in enumerate(steps) if s.startswith('WRITE:'))
# All instructions include common opcode fetch. No undocumented opcode is frozen.
rows=[{'opcode':f'{op:02X}','mnemonic':name,'steps':F+steps} for op,(name,steps) in sorted(D.items())]
result={'status':'PASS symbolic structural checks','opcode_count':len(rows),'max_abstract_steps':max(map(lambda r:len(r['steps']),rows)),'total_abstract_steps':sum(len(r['steps']) for r in rows),'excluded_unimplemented_opcodes':['32','33','34','35','36','42','54'],'limitations':['no gate-level simulation','no electrical timing','no verified pin-level schematic','conditional jump timing not optimized','memory access sequencing and SP updates require physical datapath']}
(ROOT/'isa1_rev33_microcode.json').write_text(json.dumps({'instructions':rows,'audit':result},indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,indent=2,ensure_ascii=False))
