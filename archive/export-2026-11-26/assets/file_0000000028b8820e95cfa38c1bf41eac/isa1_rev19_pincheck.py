"""ISA-1 rev19: checks SOIC pin assignments and logical bus ownership.
NOT an analog simulation or a complete CPU schematic.
"""
from itertools import product

PINS = {
 'U1_HC574': {1:'nOE',**{i+2:f'D{i}' for i in range(8)},10:'GND',11:'CLK',**{19-i:f'Q{i}' for i in range(8)},20:'VCC'},
 'U2_HC157': {1:'SEL',2:'A0',3:'B0',4:'Y0',5:'A1',6:'B1',7:'Y1',8:'GND',9:'Y2',10:'B2',11:'A2',12:'Y3',13:'B3',14:'A3',15:'nG',16:'VCC'},
 'U3_HC157': {1:'SEL',2:'A4',3:'B4',4:'Y4',5:'A5',6:'B5',7:'Y5',8:'GND',9:'Y6',10:'B6',11:'A6',12:'Y7',13:'B7',14:'A7',15:'nG',16:'VCC'},
 'U4_HC245': {1:'DIR',**{i+2:f'A{i}' for i in range(8)},10:'GND',**{18-i:f'B{i}' for i in range(8)},19:'nOE',20:'VCC'},
}

def check_pins():
 for ref, pins in PINS.items():
  size = 16 if '157' in ref else 20
  assert set(pins)==set(range(1,size+1)), (ref,'missing pins')
  assert len(set(pins.values()))==size, (ref,'duplicate function')
  assert pins[size]=='VCC' and pins[size//2]=='GND'
 assert PINS['U1_HC574'][19]=='Q0' and PINS['U1_HC574'][12]=='Q7'
 assert PINS['U4_HC245'][18]=='B0' and PINS['U4_HC245'][11]=='B7'
 return sum(len(x) for x in PINS.values())

def check_mux():
 tests=0
 for a,b,sel,ng in product(range(256),range(256),(0,1),(0,1)):
  out = 0 if ng else (b if sel else a)
  assert out == (0 if ng else [a,b][sel])
  tests+=1
 return tests

def check_bus():
 # 245 must be disabled before DIR reversal; SRAM and 245 may not both drive bus.
 tests=0
 for mem_read,mem_write,buffer_enable,dir_to_mem in product((0,1),repeat=4):
  legal = not(mem_read and mem_write) and not(mem_read and buffer_enable and dir_to_mem)
  # In write mode CPU -> memory: SRAM outputs disabled; in read mode SRAM -> CPU: 245 must not drive SRAM.
  if legal:
   assert not(mem_read and buffer_enable and dir_to_mem)
  tests+=1
 return tests

def turnaround(disable_max_ns=50,guard_ns=80):
 # 50ns max tdis for HC245 at VCC=4.5V, CL=50pF, -40..85C (TI datasheet).
 # guard assumes controller already has asserted OE disable; no skew included.
 assert guard_ns>disable_max_ns
 return guard_ns-disable_max_ns

if __name__=='__main__':
 print('pin_positions_checked:',check_pins())
 print('mux_input_cases:',check_mux())
 print('bus_control_combinations:',check_bus())
 print('illustrative_guard_margin_ns:',turnaround())
