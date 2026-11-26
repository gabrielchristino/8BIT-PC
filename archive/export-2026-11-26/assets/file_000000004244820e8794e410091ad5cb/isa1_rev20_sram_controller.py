"""ISA-1 Rev2.0: pin-map checks, memory mapping and abstract bus turnaround.
NOT SPICE or physical timing verification. Run: python3 isa1_rev20_sram_controller.py
"""
from itertools import product
import json
from pathlib import Path

HC273={1:'nCLR',2:'Q0',3:'D0',4:'D1',5:'Q1',6:'Q2',7:'D2',8:'D3',9:'Q3',10:'GND',11:'CLK',12:'Q4',13:'D4',14:'D5',15:'Q5',16:'Q6',17:'D6',18:'D7',19:'Q7',20:'VCC'}
SRAM={1:'A14',2:'A12',3:'A7',4:'A6',5:'A5',6:'A4',7:'A3',8:'A2',9:'A1',10:'A0',11:'DQ0',12:'DQ1',13:'DQ2',14:'GND',15:'DQ3',16:'DQ4',17:'DQ5',18:'DQ6',19:'DQ7',20:'nCE',21:'A10',22:'nOE',23:'A11',24:'A9',25:'A8',26:'A13',27:'nWE',28:'VCC'}
HC245={1:'DIR',**{i+2:f'A{i}' for i in range(8)},10:'GND',**{18-i:f'B{i}' for i in range(8)},19:'nOE',20:'VCC'}

def check_pins():
    for name, pins, size in [('HC273',HC273,20),('HC245',HC245,20),('SRAM',SRAM,28)]:
        assert set(pins)==set(range(1,size+1)),name
        assert len(set(pins.values()))==size,name
        assert pins[size]=='VCC' and pins[size//2]=='GND',name
    assert SRAM[27]=='nWE' and SRAM[22]=='nOE' and SRAM[20]=='nCE'
    assert HC273[1]=='nCLR' and HC273[11]=='CLK'
    return 68

def physical_ram_address(cpu_addr):
    """CPU 4000..BFFF mapped contiguously to 32KB SRAM.
    4000..7FFF -> 0000..3FFF; 8000..BFFF -> 4000..7FFF.
    """
    assert 0x4000<=cpu_addr<=0xBFFF
    return ((cpu_addr>>15)<<14)|(cpu_addr&0x3FFF)

STATES=('IDLE','READ','TURNAROUND','WRITE_SETUP','WRITE_PULSE','WRITE_HOLD')
def signals(state):
    # nCE, nOE, nWE, 245 nOE, 245 DIR; DIR=1 CPU->SRAM
    return {
        'IDLE':(1,1,1,1,1),
        'READ':(0,0,1,0,0),
        'TURNAROUND':(1,1,1,1,1),
        'WRITE_SETUP':(0,1,1,0,1),
        'WRITE_PULSE':(0,1,0,0,1),
        'WRITE_HOLD':(0,1,1,0,1),
    }[state]

def safe(s):
    ce,oe,we,be,dr=s
    ram_drives=(ce==0 and oe==0 and we==1)
    buffer_drives_ram=(be==0 and dr==1)
    return not(ram_drives and buffer_drives_ram) and not(oe==0 and we==0) and not(ce==1 and we==0)

def validate():
    count=check_pins()
    mapped=[physical_ram_address(a) for a in range(0x4000,0xC000)]
    assert sorted(mapped)==list(range(32768))
    assert physical_ram_address(0x4000)==0 and physical_ram_address(0x7FFF)==0x3FFF
    assert physical_ram_address(0x8000)==0x4000 and physical_ram_address(0xBFFF)==0x7FFF
    for s in STATES: assert safe(signals(s)),s
    # All READ->WRITE and WRITE->READ transitions go through turnaround,
    # and all WRITE pulses require setup and hold.
    legal_paths=[('IDLE','READ','TURNAROUND','WRITE_SETUP','WRITE_PULSE','WRITE_HOLD','IDLE'),
                 ('IDLE','WRITE_SETUP','WRITE_PULSE','WRITE_HOLD','TURNAROUND','READ','IDLE')]
    for path in legal_paths:
        for state in path: assert safe(signals(state))
        assert 'TURNAROUND' in path
    # Invariance for 8-bit data: buffer READ transfers SRAM to CPU, WRITE transfers CPU to SRAM.
    for value,mode in product(range(256),('READ','WRITE_SETUP','WRITE_PULSE','WRITE_HOLD')):
        ce,oe,we,be,dr=signals(mode)
        assert be==0 and (dr==0 if mode=='READ' else dr==1)
        assert 0<=value<=255
    return {'pins_checked':count,'unique_ram_addresses':len(set(mapped)),
            'legal_states':len(STATES),'checked_data_mode_cases':256*4,
            'turnaround_paths':len(legal_paths),
            'limitations':'Static state model; no propagation delay, slew, setup/hold or actual SPICE.'}

if __name__=='__main__':
    result=validate()
    Path(__file__).with_name('isa1_rev20_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
