"""Derive the NET-02 CPU adapter from the preserved RTL-01 working version."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def transform_cpu():
    source=ROOT/"sim/rtl/isa1_cpu.sv"
    text=source.read_text()
    replacements=[
      ("output reg [15:0] pc,sp, output wire [15:0] x", "output reg [15:0] pc, output wire [15:0] sp,x"),
      ("pc<=0;sp<=16'h8000;x_register<=0", "pc<=0;x_register<=0"),
      ("case(sp_op) 1:sp<=sp+16'd1;2:sp<=sp-16'd1;endcase", "// SP is stored by the pin-connected stack bank at this same edge."),
      ("5:selected_address=sp-16'd1;", "5:selected_address=stack_sum;"),
      ("wire [1:0] flags=control_word[23:22];", """wire [1:0] flags=control_word[23:22];
 wire [15:0] stack_sum;
 wire sp_down=addr_sel==5 || sp_op==2;
 wire sp_update=safe && run && !halted && state==EXEC &&
                (!USE_HC191 || x_ready) && mem==0 && (sp_op==1 || sp_op==2);
 stack_bank_netlist stack_bank(clk,safe,sp_update,sp_down,sp,stack_sum);""")]
    for old,new in replacements:
        if text.count(old)!=1:raise ValueError("Unexpected source base: "+old)
        text=text.replace(old,new)
    out=ROOT/"sim/net02/isa1_cpu_stack.sv"
    out.write_text("// GENERATED NET-02 adapter. Source SHA256: "+hashlib.sha256(source.read_bytes()).hexdigest()+"\n"+text)
    return {"source":source.relative_to(ROOT).as_posix(),"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "output":out.relative_to(ROOT).as_posix(),"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
            "transformation":"Replace only SP storage/arithmetic by KiCad-exported package netlist; preserve guards, ROM and bus sequencing"}


def transform_bench(text):
    # Fixture-only writes seed physical register outputs; no changes to checks.
    import re
    def seed(match):
        value=match.group(1)
        return f"dut.stack_bank.U1.q=({value}) & 8'hff;dut.stack_bank.U2.q=(({value}) >> 8) ^ 8'h80;"
    text=re.sub(r"dut\.sp=([^;]+);",seed,text)
    return text


if __name__=="__main__":
    record=transform_cpu()
    folder=ROOT/"verification/net02";folder.mkdir(parents=True,exist_ok=True)
    (folder/"cpu-transformation.json").write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps(record))
