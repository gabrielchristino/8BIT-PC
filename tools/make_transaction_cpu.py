"""NET-03 CPU derivation: retain NET-02 SP, replace bus control and payload/MDR."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def transform_cpu():
    source=ROOT/"sim/net02/isa1_cpu_stack.sv";text=source.read_text()
    changes=[
      ("output reg [15:0] address", "output wire [15:0] address"),
      ("output reg [7:0] write_data", "output wire [7:0] write_data"),
      ("reg [3:0] microstep; reg [7:0] ir,mdr;", "reg [3:0] microstep; reg [7:0] ir; wire [7:0] mdr;"),
      ("reg pending, pending_write;", "reg bus_start; wire bus_ready,bus_done;"),
      ("assign request = safe && pending;\n assign write_enable = request && pending_write;", "// Bus qualifiers are driven by the exported IC netlist."),
      ("reg [15:0] selected_address;", """reg [15:0] selected_address;
 transaction_bank_netlist bus_bank(clk,reset_n,power_good,bus_start,mem==2,acknowledge,
   selected_address,value,read_data,bus_ready,bus_done,request,write_enable,address,write_data,mdr, );"""),
      ("ea<=0;ir<=0;mdr<=0;fetch_bank<=1;microstep<=0;", "ea<=0;ir<=0;fetch_bank<=1;microstep<=0;"),
      ("halted<=0;fault<=0;retired<=0;pending<=0;pending_write<=0;\n     address<=0;write_data<=0;state<=EXEC;", "halted<=0;fault<=0;retired<=0;bus_start<=0;state<=EXEC;"),
      ("RESPONSE: if(acknowledge) begin\n         if(!pending_write) mdr<=read_data;\n         pending<=0;state<=DROP;\n       end\n       DROP: if(!acknowledge) begin state<=EXEC;advance();end", "RESPONSE: if(bus_done) begin bus_start<=0;state<=DROP;end\n       DROP: if(bus_ready) begin state<=EXEC;advance();end"),
      ("address<=selected_address;write_data<=value;\n             pending_write<=mem==2;pending<=1;state<=RESPONSE;", "bus_start<=1;state<=RESPONSE;")]
    for old,new in changes:
        if text.count(old)!=1:raise ValueError("Unexpected NET-02 source: "+old)
        text=text.replace(old,new)
    dest=ROOT/"sim/net03/isa1_cpu_bus.sv"
    dest.write_text("// GENERATED NET-03; source SHA256 "+hashlib.sha256(source.read_bytes()).hexdigest()+"\n"+text)
    record={"source":source.relative_to(ROOT).as_posix(),"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "output":dest.relative_to(ROOT).as_posix(),"output_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
            "transformation":"Replace bus payload, write descriptor, MDR and transaction sequencing by KiCad pin netlist; keep SP, ROM, ISA and stack guards"}
    out=ROOT/"verification/net03";out.mkdir(parents=True,exist_ok=True)
    (out/"cpu-transformation.json").write_text(json.dumps(record,indent=2)+"\n")
    return record


if __name__=="__main__":print(json.dumps(transform_cpu()))
