"""NET-06: separate A/B/EA/flags and source mux adapter from immutable NET-05."""
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def transform_bench(text):
    # Seed physical package Q for architectural fixtures, not top-level wires.
    paths={'a':'U1.q','b':'U2.q','z':'U5_0.q','c':'U5_1.q'}
    for field,target in paths.items():
        text=re.sub(r'dut\.'+field+r'\s*=', 'dut.register_bank.'+target+'=',text)
    return text


def transform():
    source=ROOT/'sim/net05/isa1_cpu_alu.sv';text=source.read_text()
    def replace(old,new):
        nonlocal text
        if text.count(old)!=1:raise ValueError('Unexpected base: '+old)
        text=text.replace(old,new)
    replace('output reg [7:0] a,b,','output wire [7:0] a,b,')
    replace('output reg z,c,halted,retired,','output wire z,c, output reg halted,retired,')
    replace('reg [15:0] ea;','wire [15:0] ea;\n wire [7:0] dst_n_bus; wire [3:0] flags_n_bus;')
    replace('wire [7:0] result; reg [7:0] value;', 'wire [7:0] result,value;')
    replace('.sp_update(sp_update),.sp_down(sp_down));','.sp_update(sp_update),.sp_down(sp_down),.dst_n(dst_n_bus),.flags_n(flags_n_bus));')
    start=text.index('   case(src)');end=text.index('   case(addr_sel)',start)
    text=text[:start]+text[end:]
    replace('pc<=0;x_register<=0;a<=0;b<=0;z<=0;c<=0;', 'pc<=0;x_register<=0;')
    replace('     ea<=0;\n','')
    start=text.index('           case(dst)');end=text.index('           case(pc_op)',start)
    text=text[:start]+text[end:]
    marker=' transaction_bank_netlist bus_bank'
    replace(marker,''' register_bank_netlist register_bank(execute_clk,reset_n,power_good,execute_pulse && control_ready,
   src,dst_n_bus,flags_n_bus,pc,mdr,result,carry,a,b,value,ea,z,c);
 transaction_bank_netlist bus_bank''')
    for pattern in (r'\ba\s*<=',r'\bb\s*<=',r'\bea(?:\[.*?\])?\s*<=',r'\bz\s*<=',r'\bc\s*<='):
        if re.search(pattern,text):raise ValueError('RTL storage remained: '+pattern)
    destination=ROOT/'sim/net06/isa1_cpu_registers.sv';destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text('// GENERATED NET-06 base SHA256 '+hashlib.sha256(source.read_bytes()).hexdigest()+'\n'+text)
    record={'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'output':destination.relative_to(ROOT).as_posix(),'output_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
      'transformation':'Replace A/B/EA/Z/C storage and source mux by pin-connected bank; reuse NET-04 decoded DST/FLAGS; preserve PC/address selection and execution RTL'}
    out=ROOT/'verification/net06';out.mkdir(parents=True,exist_ok=True)
    (out/'cpu-transformation.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


if __name__=='__main__':print(json.dumps(transform()))
