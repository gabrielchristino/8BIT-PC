"""NET-09 maps main X synchronously; retains HC191 configuration for comparison."""
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def transform_bench(text):
    return re.sub(r'dut\.x_register\s*=', '{dut.x_register_bank.U2.q,dut.x_register_bank.U1.q}=',text)


def transform():
    source=ROOT/'sim/net08/isa1_cpu_execution.sv';s=source.read_text()
    if s.count('reg [15:0] x_register;')!=1:raise ValueError('Unexpected X base')
    s=s.replace('reg [15:0] x_register;','wire [15:0] x_register;')
    s=s.replace('wire execute_pulse,seq_advance;', 'wire execute_pulse,seq_advance,execute_accept,write_mode;')
    s=s.replace('execute_pulse && control_ready','execute_accept').replace('bus_start,mem==2,acknowledge','bus_start,write_mode,acknowledge')
    s=s.replace('execution_bank_netlist execution_bank','execution_bank_net09 execution_bank').replace('halted,retired,fault,state);','halted,retired,fault,state,execute_accept,write_mode);')
    start=s.index(' // Only the alternative ideal-X reference');s=s[:start]+''' x_register_bank_netlist x_register_bank(execute_clk,reset_n,power_good,
   !USE_HC191 && execute_accept,x_n_bus,ea,x_register);
endmodule
'''
    destination=ROOT/'sim/net09/isa1_cpu_pins.sv';destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text('// GENERATED NET-09 base SHA256 '+hashlib.sha256(source.read_bytes()).hexdigest()+'\n'+s)
    record={'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'output':destination.relative_to(ROOT).as_posix(),'output_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
      'transformation':'Replace main X RTL register/arithmetic with synchronous pin-connected bank and expose native execution-accept/write-mode gates; USE_HC191=1 remains separate reference alternative, not main board BOM'}
    out=ROOT/'verification/net09';out.mkdir(parents=True,exist_ok=True)
    (out/'cpu-transformation.json').write_text(json.dumps(record,indent=2)+'\n');return record


if __name__=='__main__':print(json.dumps(transform()))
