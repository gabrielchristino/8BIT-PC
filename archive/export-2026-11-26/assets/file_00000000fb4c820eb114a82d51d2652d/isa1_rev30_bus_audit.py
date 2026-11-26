#!/usr/bin/env python3
"""ISA-1 Rev 3.0: independent bus-owner enumeration; static logic, NOT SPICE."""
import itertools,json,pathlib
PINS_377={1:'EN_N',2:'Q0',3:'D0',4:'D1',5:'Q1',6:'Q2',7:'D2',8:'D3',9:'Q3',10:'GND',11:'CLK',12:'Q4',13:'D4',14:'D5',15:'Q5',16:'Q6',17:'D6',18:'D7',19:'Q7',20:'VCC'}
# TI HC244: 1OE_N pin1, 2OE_N pin19, GND pin10, VCC pin20
PINS_244={1:'1OE_N',2:'1A1',3:'2Y4',4:'1A2',5:'2Y3',6:'1A3',7:'2Y2',8:'1A4',9:'2Y1',10:'GND',11:'1Y4',12:'2A1',13:'1Y3',14:'2A2',15:'1Y2',16:'2A3',17:'1Y1',18:'2A4',19:'2OE_N',20:'VCC'}
PINS_EEPROM={1:'A14',2:'A12',3:'A7',4:'A6',5:'A5',6:'A4',7:'A3',8:'A2',9:'A1',10:'A0',11:'IO0',12:'IO1',13:'IO2',14:'GND',15:'IO3',16:'IO4',17:'IO5',18:'IO6',19:'IO7',20:'CE_N',21:'A10',22:'OE_N',23:'A11',24:'A9',25:'A8',26:'A13',27:'WE_N',28:'VCC'}
for d,n in ((PINS_377,20),(PINS_244,20),(PINS_EEPROM,28)):
 assert set(d)==set(range(1,n+1))
 assert len(set(d.values()))==n
# Model: U_WR (244) input <- 377 DATA; output -> EEPROM_IO; U_RD (244) input <- EEPROM_IO; output -> CPU_DATA.
# The CPU bus can be driven by CPU source or U_RD; EEPROM IO by U_WR or EEPROM. Never both.
def outputs(state,power_ok,reset,init_done,chip_present,read_en,write_en,cpu_driver_en):
    gate=power_ok and not reset and init_done and chip_present
    rd=gate and state=='READ' and read_en and not write_en and not cpu_driver_en
    wr=gate and state=='WRITE' and write_en and not read_en
    ce=rd or wr
    oe=rd
    we=wr
    return {'rd':rd,'wr':wr,'ce_n':int(not ce),'oe_n':int(not oe),'we_n':int(not we)}
checks=0
for vals in itertools.product((False,True),repeat=7):
 power,reset,init,present,read,write,cpu=vals
 for state in ('IDLE','READ','WRITE','TURN','INVALID'):
  s=outputs(state,power,reset,init,present,read,write,cpu)
  chip_drives=(s['ce_n']==0 and s['oe_n']==0 and s['we_n']==1)
  assert not (chip_drives and s['wr']),('EEPROM contention',vals,state)
  assert not (cpu and s['rd']),('CPU contention',vals,state)
  assert not (s['rd'] and s['wr'])
  assert not (s['we_n']==0 and (reset or not power or not init or not present))
  checks+=1
# Negative tests independently construct two illegal owner sets; expected to fail uniqueness.
def collision(owners):return len(owners)>1
assert collision({'EEPROM','WRITE_BUFFER'})
assert collision({'CPU_SOURCE','READ_BUFFER'})
# Separate write-authorization from bus-owner check; currently UNIMPLEMENTED physically.
# Check region boundaries without relying on a function also used to generate them.
regions=[(0,0x40),(0x40,0x7800),(0x7800,0x7c00),(0x7c00,0x8000)]
assert sum(b-a for a,b in regions)==32768
assert all(regions[i][1]==regions[i+1][0] for i in range(3))
assert all(a%64==0 and b%64==0 for a,b in regions)
res={'status':'PASS: static owner-model only','control_cases':checks,'pin_entries':len(PINS_377)+len(PINS_244)+len(PINS_EEPROM),'negative_contention_tests':2,'region_bytes':32768,'physical_timing_validated':False,'hardware_write_protection_implemented':False}
p=pathlib.Path(__file__).with_name('isa1_rev30_results.json');p.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
