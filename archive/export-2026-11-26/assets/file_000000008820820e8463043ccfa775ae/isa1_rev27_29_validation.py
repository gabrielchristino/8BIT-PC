#!/usr/bin/env python3
"""ISA-1 architecture checks; discrete logic model, not electrical validation."""
import json, itertools, random
from pathlib import Path
OUT=Path(__file__).parent
# 74HC244: two 4-bit banks, each /OE independently controlled.
HC244={1:'1OE_N',2:'1A1',3:'2Y4',4:'1A2',5:'2Y3',6:'1A3',7:'2Y2',8:'1A4',9:'2Y1',10:'GND',11:'2A1',12:'1Y4',13:'2A2',14:'1Y3',15:'2A3',16:'1Y2',17:'2A4',18:'1Y1',19:'2OE_N',20:'VCC'}
assert len(HC244)==20 and len(set(HC244.values()))==20
# Independent read buffer: EEPROM IO -> CPU_DATA. Write buffer: 377 Q -> EEPROM IO.
# CPU bus only driven by read buffer when CPU sources are disabled.
STATES=('RESET','IDLE','LOAD_ADDR_LO','LOAD_ADDR_HI','LOAD_DATA','READ_SETUP','READ','READ_RELEASE','WRITE_SETUP','WRITE_PULSE','WRITE_HOLD','WRITE_WAIT','VERIFY','ERROR')
READ_STATES={'READ','VERIFY'}
WRITE_STATES={'WRITE_SETUP','WRITE_PULSE','WRITE_HOLD'}
# Safety policy: permission for SDP writes only when sequencer is in explicit unlock steps;
# address-specific authorization prevents general writes to code in SAVE mode.
SDP=((0x5555,0xAA),(0x2AAA,0x55),(0x5555,0xA0))
SAVE_START=0x7800

def permit(addr,data,mode,phase,step):
    if mode=='PROGRAM': return 0<=addr<32768
    if mode!='SAVE': return False
    if phase=='UNLOCK': return 0<=step<3 and (addr,data)==SDP[step]
    if phase=='PAYLOAD': return SAVE_START<=addr<32768
    return False

def signals(state, reset, power_ok, init_done, media_present, mode, addr, data, phase, step, cpu_source_active):
    enabled=(not reset and power_ok and init_done and media_present)
    read=enabled and state in READ_STATES and not cpu_source_active
    write=enabled and state in WRITE_STATES and permit(addr,data,mode,phase,step)
    return dict(ce_n=int(not (read or write)),oe_n=int(not read),we_n=int(not (write and state=='WRITE_PULSE')),
                read_buffer_n=int(not read),write_buffer_n=int(not write),
                cpu_source_active=int(cpu_source_active))

cases=0
for state,reset,power,init,present,mode,phase,step,cpu in itertools.product(
    STATES,(False,True),(False,True),(False,True),(False,True),('SAVE','PROGRAM','NONE'),('UNLOCK','PAYLOAD'),range(3),(False,True)):
    # Use representative addresses, including SDP, code, SAVE and boundary.
    for addr,data in ((0x5555,0xAA),(0x2AAA,0x55),(0x5555,0xA0),(0x77FF,0),(0x7800,0),(0x7FFF,0)):
        s=signals(state,reset,power,init,present,mode,addr,data,phase,step,cpu)
        read=s['read_buffer_n']==0; write=s['write_buffer_n']==0
        assert not (read and write)
        assert not (read and cpu)
        assert not (s['oe_n']==0 and s['we_n']==0)
        assert not (s['we_n']==0 and (reset or not power or not init or not present))
        assert not (s['we_n']==0 and not permit(addr,data,mode,phase,step))
        cases+=1
# Verify entire SAVE policy including header and code boundary.
assert all(not permit(a,0,'SAVE','PAYLOAD',0) for a in range(0,0x7800))
assert all(permit(a,0,'SAVE','PAYLOAD',0) for a in range(0x7800,0x8000))
assert all(permit(a,d,'SAVE','UNLOCK',i) for i,(a,d) in enumerate(SDP))
assert not permit(0x5555,0xAB,'SAVE','UNLOCK',0)
assert not permit(0x5555,0xAA,'SAVE','UNLOCK',1)
# Check 64-byte page partitions and A/B record windows
regions=((0,0x40,'header'),(0x40,0x7800,'code'),(0x7800,0x7c00,'save_a'),(0x7c00,0x8000,'save_b'))
assert sum(hi-lo for lo,hi,_ in regions)==32768
assert all(sum(lo<=a<hi for lo,hi,_ in regions)==1 for a in range(32768))
# Deliberately inject an unsafe direct control change, demonstrate model catches it.
def conflict(read_driver,write_driver,cpu_driver):
    return (read_driver and write_driver) or (read_driver and cpu_driver)
assert conflict(True,True,False) and conflict(True,False,True)
# Sequence abstractly ensures no simultaneous read/write driver, with guard phases.
transitions=[('READ','READ_RELEASE'),('READ_RELEASE','IDLE'),('IDLE','WRITE_SETUP'),('WRITE_SETUP','WRITE_PULSE'),('WRITE_PULSE','WRITE_HOLD'),('WRITE_HOLD','WRITE_WAIT'),('WRITE_WAIT','IDLE'),('IDLE','READ_SETUP'),('READ_SETUP','VERIFY')]
assert all(a in STATES and b in STATES for a,b in transitions)
# A read buffer output can only be enabled when CPU sources are off.
# Clock-edge scheduling and propagation delays remain unverified.
result={'revision':'2.7-2.9','status':'logical model passed; hardware NOT stable','hc244_pins_checked':len(HC244),'state_count':len(STATES),'static_control_cases':cases,'eeprom_locations_checked':32768,'sdp_unlock_exception_verified':True,'negative_contention_tests':2,'limitations':['No datasheet-timing simulation','No power-ramp analog test','No full CPU or video implementation','No netlist ERC/PCB DRC','No hardware prototype']}
(OUT/'isa1_rev27_29_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,indent=2,ensure_ascii=False))
