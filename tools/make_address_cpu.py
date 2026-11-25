"""NET-07: substitute PC and address selection without changing NET-06."""
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def transform_bench(text):
    return re.sub(r'dut\.pc\s*=', '{dut.address_bank.U2.q,dut.address_bank.U1.q}=',text)


def transform():
    source=ROOT/'sim/net06/isa1_cpu_registers.sv';text=source.read_text()
    def replace(old,new):
        nonlocal text
        if text.count(old)!=1:raise ValueError('Unexpected base '+old)
        text=text.replace(old,new)
    replace('output reg [15:0] pc,','output wire [15:0] pc,')
    replace('reg [15:0] selected_address;', 'wire [15:0] selected_address; wire [7:0] pc_n_bus;')
    replace('.flags_n(flags_n_bus));','.flags_n(flags_n_bus),.pc_n(pc_n_bus));')
    start=text.index(' always @* begin');end=text.index(' task advance;',start)
    text=text[:start]+''' address_bank_netlist address_bank(execute_clk,reset_n,power_good,execute_pulse && control_ready,
   addr_sel,pc_n_bus,z,ea,x,sp,stack_sum,pc,selected_address);
'''+text[end:]
    replace('pc<=0;x_register<=0;','x_register<=0;')
    start=text.index('           case(pc_op)');end=text.index('           // SP is stored',start)
    text=text[:start]+text[end:]
    if re.search(r'\bpc\s*<=|selected_address\s*=',text):raise ValueError('Behavioral PC/address remained')
    destination=ROOT/'sim/net07/isa1_cpu_address.sv';destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text('// GENERATED NET-07 base SHA256 '+hashlib.sha256(source.read_bytes()).hexdigest()+'\n'+text)
    record={'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'output':destination.relative_to(ROOT).as_posix(),'output_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
      'transformation':'Replace PC storage/increment/branches and address mux by exported pin graph; PC_N decoder reused; execution/guards remain RTL'}
    out=ROOT/'verification/net07';out.mkdir(parents=True,exist_ok=True)
    (out/'cpu-transformation.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


if __name__=='__main__':print(json.dumps(transform()))
