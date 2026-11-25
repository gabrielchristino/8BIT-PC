"""NET-08 removes execution/guard/fault procedural control from NET-07."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def transform_bench(text):
    return text.replace('dut.stack_checked=0;','dut.execution_bank.U1.q[4]=0;')


def transform():
    source=ROOT/'sim/net07/isa1_cpu_address.sv';s=source.read_text()
    changes=[('output wire z,c, output reg halted,retired, output reg [1:0] fault,','output wire z,c,halted,retired, output wire [1:0] fault,'),
      ('reg bus_start;','wire bus_start;'),('reg [1:0] state;','wire [1:0] state;'),
      ('reg x_load_request,x_load_completed;','wire x_load_request;'),('reg stack_checked;','wire stack_checked;')]
    for a,b in changes:
        if s.count(a)!=1:raise ValueError(a)
        s=s.replace(a,b)
    start=s.index(' wire x_count=');end=s.index(' assign x=',start)
    s=s[:start]+' wire x_count; wire [7:0] addr_n_bus; wire [3:0] mem_n_bus,x_n_bus;\n'+s[end:]
    start=s.index(' wire execute_pulse=');end=s.index(' microcode_bank_netlist',start)
    s=s[:start]+' wire execute_pulse,seq_advance;\n'+s[end:]
    s=s.replace('.pc_n(pc_n_bus));','.pc_n(pc_n_bus),.addr_n(addr_n_bus),.mem_n(mem_n_bus),.x_n(x_n_bus));')
    start=s.index(' task advance;');s=s[:start]+''' execution_bank_netlist execution_bank(execute_clk,reset_n,power_good,run,control_ready,
   !USE_HC191 || x_ready,x_done,USE_HC191!=0,boot,bus_ready,bus_done,dispatch,control_word[24],control_word[25],
   ir,addr_n_bus,mem_n_bus,x_n_bus,sp,execute_pulse,seq_advance,bus_start,x_load_request,x_count,stack_checked,halted,retired,fault,state);
 // Only the alternative ideal-X reference remains procedural here.
 always @(posedge execute_clk or negedge safe)begin
   if(!safe)x_register<=0;
   else if(!USE_HC191 && execute_pulse && control_ready)case(x_op)
     1:x_register<=ea;2:x_register<=x+16'd1;3:x_register<=x-16'd1;
   endcase
 end
endmodule
'''
    destination=ROOT/'sim/net08/isa1_cpu_execution.sv';destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text('// GENERATED NET-08 base SHA256 '+hashlib.sha256(source.read_bytes()).hexdigest()+'\n'+s)
    record={'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'output':destination.relative_to(ROOT).as_posix(),'output_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
      'transformation':'Replace execution FSM, bus/X load requests, guards, fault and retire by pin-connected HC174/gates; X alternative still reference RTL'}
    out=ROOT/'verification/net08';out.mkdir(parents=True,exist_ok=True)
    (out/'cpu-transformation.json').write_text(json.dumps(record,indent=2)+'\n');return record


if __name__=='__main__':print(json.dumps(transform()))
