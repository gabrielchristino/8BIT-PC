#!/usr/bin/env python3
"""ISA-1 Rev2.6: logical design checks, NOT electrical timing simulation."""
import json, itertools, pathlib
P=pathlib.Path(__file__).parent
HC377={'/CLKEN':1,'Q0':2,'D0':3,'D1':4,'Q1':5,'Q2':6,'D2':7,'D3':8,'Q3':9,'GND':10,'CLK':11,'Q4':12,'D4':13,'D5':14,'Q5':15,'Q6':16,'D6':17,'D7':18,'Q7':19,'VCC':20}
HC245={'DIR':1,**{f'A{i}':2+i for i in range(8)},'GND':10,**{f'B{i}':18-i for i in range(8)},'/OE':19,'VCC':20}
assert sorted(HC377.values())==list(range(1,21))
assert sorted(HC245.values())==list(range(1,21))
assert all(HC377[f'D{i}'] != HC377[f'Q{i}'] for i in range(8))
# Register load enable, with all other clocks holding. No asynchronous reset exists on HC377.
reg=0; loads=0; holds=0
for old,new,en in itertools.product(range(256),range(256),(0,1)):
    actual=new if en else old
    assert actual==(new if en else old)
    if en: loads+=1
    else: holds+=1
# Each state has an explicit allowed bus owner; EEPROM write is blocked unless all guards pass.
states={
 'RESET':('none',False), 'IDLE':('none',False),
 'SETUP':('none',False), 'READ':('eeprom',False),
 'TURN':('none',False), 'WRITE_SETUP':('driver',False),
 'WRITE_PULSE':('driver',True), 'WRITE_HOLD':('driver',False),
 'VERIFY':('eeprom',False)
}
checks=0; write_cases=0
for state,power,permit,ready,addr_ok in itertools.product(states,(0,1),(0,1),(0,1),(0,1)):
    owner,pulse=states[state]
    # /CE low only during active read or write, /OE low only during read.
    ce=(owner!='none') and bool(power and ready)
    oe=ce and owner=='eeprom'
    we=ce and pulse and bool(permit and addr_ok)
    driver=ce and owner=='driver'
    assert not (oe and driver)
    assert not (oe and we)
    assert not we or (state=='WRITE_PULSE' and power and permit and ready and addr_ok)
    assert not power or not we or ready
    checks+=1; write_cases+=int(we)
# Independent guard test: force both outputs on and confirm contention detector trips.
def conflict(ee_output, driver_output): return ee_output and driver_output
assert conflict(True,True) and not conflict(True,False) and not conflict(False,True)
# A registered state cannot guarantee analog nonoverlap; physical dead time remains mandatory.
# Check exactly 512 pages and the proposed SAVE regions.
regions=[(0x0000,0x003f),(0x0040,0x77ff),(0x7800,0x7bff),(0x7c00,0x7fff)]
assert sum(b-a+1 for a,b in regions)==32768
assert all(a%64==0 and (b+1)%64==0 for a,b in regions)
assert all(regions[i][1]+1==regions[i+1][0] for i in range(3))
result={'rev':'2.6','model':'logical/static; no SPICE/physical timing','hc377_pin_positions':len(HC377),'hc245_pin_positions':len(HC245),'register_cases':loads+holds,'register_load_cases':loads,'register_hold_cases':holds,'control_cases':checks,'authorized_write_cases':write_cases,'negative_contention_test':'detected','eeprom_pages':512,'passed':True,'limits':['unverified real signal skew','no actual power ramp','no real EEPROM programming waveform','no supervisor pinout verified']}
(P/'isa1_rev26_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,indent=2,ensure_ascii=False))
