#!/usr/bin/env python3
"""ISA-1 Rev 2.4: abstract AT28C256 transaction and interlock verification.
NOT a physical timing simulation. Pin table transcribed from DS20006386B p4.
"""
import json
from pathlib import Path

PIN = {1:'A14',2:'A12',3:'A7',4:'A6',5:'A5',6:'A4',7:'A3',8:'A2',9:'A1',10:'A0',11:'IO0',12:'IO1',13:'IO2',14:'GND',15:'IO3',16:'IO4',17:'IO5',18:'IO6',19:'IO7',20:'CE_N',21:'A10',22:'OE_N',23:'A11',24:'A9',25:'A8',26:'A13',27:'WE_N',28:'VCC'}
assert set(PIN)==set(range(1,29))
assert len(set(PIN.values()))==28
assert {f'A{i}' for i in range(15)} <= set(PIN.values())
assert {f'IO{i}' for i in range(8)} <= set(PIN.values())

# Independent hardware-permission input required: SW request alone cannot authorize writes.
def control(reset, power_good, installed, hw_unlock, state):
    allowed = power_good and not reset and installed
    if state == 'READ' and allowed:
        return (0,0,1,False)  # CE_N, OE_N, WE_N, CPU driving bus?
    if state == 'WRITE' and allowed and hw_unlock:
        return (0,1,0,True)
    return (1,1,1,False)

checks=0
for reset in (False,True):
 for power_good in (False,True):
  for installed in (False,True):
   for hw_unlock in (False,True):
    for state in ('IDLE','READ','WRITE','TURNAROUND','UNKNOWN'):
     ce,oe,we,cpu_drives=control(reset,power_good,installed,hw_unlock,state)
     chip_drives = (ce==0 and oe==0 and we==1)
     assert not (chip_drives and cpu_drives)
     assert not (we==0 and (reset or not power_good or not installed or not hw_unlock))
     assert not (we==0 and oe==0)
     checks+=1

# All 32K EEPROM locations belong to exactly one of the prior logical partitions.
regions=[(0,64,'header'),(64,30720,'code'),(30720,31744,'save_a'),(31744,32768,'save_b')]
for a in range(32768):
    matches=[name for lo,hi,name in regions if lo<=a<hi]
    assert len(matches)==1,(a,matches)
# All SAVE pages are exactly aligned to 64-byte boundaries; avoids cross-page writes.
assert all((lo%64==0 and hi%64==0) for lo,hi,_ in regions)

def page_chunks(start, payload):
    assert 0 <= start <= 32768 and start+len(payload)<=32768
    p=0
    while p<len(payload):
        addr=start+p
        n=min(len(payload)-p,64-(addr%64))
        yield addr,payload[p:p+n]
        p+=n

page_tests=0
for start in range(0,32768,17):
    n=min(129,32768-start)
    chunks=list(page_chunks(start,bytes((i%256 for i in range(n)))))
    assert b''.join(c for _,c in chunks)==bytes((i%256 for i in range(n)))
    assert all(len(c)<=64 and (addr//64)==((addr+len(c)-1)//64) for addr,c in chunks)
    page_tests+=1

# Software Data Protection sequence: mandatory prefix before each protected transaction.
SDP=((0x5555,0xAA),(0x2AAA,0x55),(0x5555,0xA0))
def protected_write(start,payload):
    for addr,chunk in page_chunks(start,payload):
        yield {'unlock':SDP,'page':addr//64,'bytes':[(addr+i,b) for i,b in enumerate(chunk)]}

for tx in protected_write(0x783F,bytes(range(128))):
    assert tx['unlock']==SDP
    assert len(tx['bytes'])<=64
    assert len({a//64 for a,_ in tx['bytes']})==1

# Write permission is additionally constrained to media regions by firmware policy.
def region_write_allowed(address, mode):
    if mode=='SAVE': return 0x7840<=address<=0x7FFF
    if mode=='PROGRAM': return 0<=address<=0x7FFF
    return False
assert not any(region_write_allowed(a,'SAVE') for a in range(0x7840))
assert all(region_write_allowed(a,'SAVE') for a in range(0x7840,0x8000))

result={'pin_positions_checked':len(PIN),'control_combinations_checked':checks,'address_locations_checked':32768,'page_partition_cases_checked':page_tests,'sdp_sequence_hex':[[hex(a),hex(b)] for a,b in SDP],'model':'logic and transaction checks only; not IC propagation, power-fail or analog simulation','status':'passed'}
Path(__file__).with_name('isa1_rev24_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,indent=2,ensure_ascii=False))
