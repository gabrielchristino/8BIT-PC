import json
from pathlib import Path

SIZE=32768
regions=[('header',0x0000,0x0040),('code',0x0040,0x7800),('save_a',0x7800,0x7c00),('save_b',0x7c00,0x8000)]
assert regions[0][1]==0 and regions[-1][2]==SIZE
for a,b in zip(regions,regions[1:]): assert a[2]==b[1]
assert all(lo%64==0 and hi%64==0 for _,lo,hi in regions)
assert [hi-lo for _,lo,hi in regions]==[64,30656,1024,1024]
for address in range(SIZE):
    assert sum(lo<=address<hi for _,lo,hi in regions)==1

# Safety logic: outputs are permitted only with stable registered phase, reset released,
# valid power and write authorization. A software policy is NOT hardware isolation.
def controls(phase,reset_ok,power_ok,write_auth):
    live=reset_ok and power_ok
    ce_n=not (live and phase in ('READ','WRITE'))
    oe_n=not (live and phase=='READ')
    we_n=not (live and phase=='WRITE' and write_auth)
    cpu_drive=live and phase=='WRITE' and write_auth
    eeprom_drive=live and phase=='READ'
    return dict(ce_n=ce_n,oe_n=oe_n,we_n=we_n,cpu_drive=cpu_drive,eeprom_drive=eeprom_drive)

cases=0
for phase in ('IDLE','READ','TURN','WRITE_SETUP','WRITE','WRITE_HOLD','POLL'):
 for r in (False,True):
  for p in (False,True):
   for w in (False,True):
    x=controls(phase,r,p,w);cases+=1
    assert not (x['cpu_drive'] and x['eeprom_drive'])
    assert not (not x['we_n'] and not x['oe_n'])
    assert x['we_n'] or (r and p and w and phase=='WRITE')
    if not (r and p): assert x['ce_n'] and x['oe_n'] and x['we_n']

# Compare two candidate organizations. Counts are interface-only lower-bound examples,
# not BOM totals. 15 address latches: 2 x octal; data latch: 1 x octal;
# bus transceiver: 1 x octal; separate control registers and glue not counted.
comparison={
 'dedicated_latched_port':{'address_registers_8bit':2,'data_registers_8bit':1,'transceivers_8bit':1,'pros':'isolates slow EEPROM from CPU memory cycles; stable address during write','cons':'extra registers and explicit firmware I/O sequencing'},
 'memory_mapped_window':{'address_registers_8bit':0,'data_registers_8bit':0,'transceivers_8bit':'0 or more depending on bus design','pros':'natural load/store instructions; fewer dedicated registers','cons':'consumes address window; /WE qualification, decoding, CPU bus timing and reset still required'}
}
results={'revision':'2.5','regions':[{'name':n,'start':f'{lo:04X}','end_inclusive':f'{hi-1:04X}','bytes':hi-lo} for n,lo,hi in regions],'addresses_checked':SIZE,'static_control_cases':cases,'static_checks':'PASS','architecture_comparison':comparison,'limitations':'Abstract boolean model only; no propagation delays, supervisor IC, voltage ramp, or hardware timing verified'}
out=Path(__file__).with_name('isa1_rev25_results.json');out.write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'addresses_checked':SIZE,'control_cases':cases,'result':'PASS'},ensure_ascii=False))
