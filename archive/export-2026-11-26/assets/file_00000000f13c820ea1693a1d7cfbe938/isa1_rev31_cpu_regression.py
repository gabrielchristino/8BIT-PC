"""ISA-1 rev 3.1: behavioral regression only; no gate-level/electrical claims."""
import json, random
from pathlib import Path
from isa1_rev09_model import CPU, OP
from isa1_rev07_emulator import Memory

checks=0

def verify(condition, message):
    global checks
    checks += 1
    if not condition: raise AssertionError(message)

def cpu_with(code):
    m=Memory(); m.rom[:len(code)]=bytes(code)
    return CPU(m),m

# Exhaustively test every pair of operands against independent integer specifications.
for opname in ('ADD','SUB','AND','OR','XOR','CMP'):
    for a in range(256):
        for b in range(256):
            c,m=cpu_with([OP[opname]])
            c.a=a; c.b=b; c.step()
            if opname=='ADD': expected=(a+b)&255; carry=int(a+b>255)
            elif opname=='SUB': expected=(a-b)&255; carry=int(a>=b)
            elif opname=='AND': expected=a&b; carry=0
            elif opname=='OR': expected=a|b; carry=0
            elif opname=='XOR': expected=a^b; carry=0
            else: expected=a; carry=int(a>=b)
            verify(c.a==expected, f'{opname} A {a} {b}')
            verify(c.z==int(((a-b)&255 if opname=='CMP' else expected)==0),f'{opname} Z {a} {b}')
            if opname in ('ADD','SUB','CMP'):
                verify(c.c==carry,f'{opname} C {a} {b}')

# ROM is immutable from normal CPU stores; RAM and VRAM writes are independent.
c,m=cpu_with([OP['LDAI'],0xA5,OP['STAA'],0x00,0x00,OP['STAA'],0x00,0x40,
              OP['STAA'],0x00,0xC0,OP['HALT']]); c.run()
verify(m.rom[0]==OP['LDAI'],'ROM modified')
verify(m.read(0x4000)==0xA5,'RAM store')
verify(m.read(0xC000)==0xA5,'VRAM store')

# Nested subroutine calls with return address ordering and stack balance.
code=[0]*0x40
code[0:4]=[OP['CALL'],0x10,0x00,OP['HALT']]
code[0x10:0x16]=[OP['CALL'],0x20,0x00,OP['LDAI'],0x7B,OP['RET']]
code[0x20]=OP['RET']
c,m=cpu_with(code); c.run()
verify(c.a==0x7B,'nested CALL result')
verify(c.sp==0xBFFF,'nested CALL stack balance')
verify(c.pc==4,'nested CALL return address')

# Branches consume operands even when not taken.
for z in (0,1):
    for name in ('JZ','JNZ'):
        c,m=cpu_with([OP[name],0x09,0x00,OP['HALT']]+[OP['NOP']]*5+[OP['HALT']])
        c.z=z; c.step()
        verify(c.pc==(9 if ((name=='JZ')==bool(z)) else 3),f'{name} branch {z}')

# The initial RAM address formula is checked independently against sequential address space.
m=Memory()
for addr in range(0x4000,0xC000):
    verify(m.ram_index(addr)==addr-0x4000,f'RAM address {addr:04x}')

result={'revision':'3.1','status':'behavioral_tests_passed','assertions':checks,
        'hardware_approved':False,'known_gaps':['no microcode','no gate-level netlist',
        'no physical timing','no RCA color encoder','no keyboard circuit',
        'no EEPROM writer sequencer','no reset/power supervisor selection']}
Path(__file__).with_name('isa1_rev31_results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
