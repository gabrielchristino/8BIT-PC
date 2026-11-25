"""NET-05 adapter: preserve NET-04 and replace only the combinational ALU."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def transform():
    source=ROOT/'sim/net04/isa1_cpu_microcode.sv'
    text=source.read_text()
    text=text.replace('reg [8:0] arithmetic;\n reg [7:0] result, value;\n reg carry;',
      'wire [7:0] result; reg [7:0] value; wire carry,alu_zero;\n alu_bank_netlist alu_bank(a,b,alu,c,result,carry,alu_zero);')
    start=text.index('   arithmetic=0; result=0; carry=c;')
    end=text.index('   case(src)',start)
    text=text[:start]+text[end:]
    if 'arithmetic' in text or 'case(alu)' in text:raise ValueError('Incomplete ALU replacement')
    destination=ROOT/'sim/net05/isa1_cpu_alu.sv'
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text('// GENERATED NET-05 base SHA256 '+hashlib.sha256(source.read_bytes()).hexdigest()+'\n'+text)
    # Flags still compare the selected bus value, not necessarily the ALU result.
    record={'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'output':destination.relative_to(ROOT).as_posix(),'output_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
      'transformation':'Replace combinational ALU by XML pin-connected package bank; flags register and selected-value zero test preserved in RTL'}
    out=ROOT/'verification/net05';out.mkdir(parents=True,exist_ok=True)
    (out/'cpu-transformation.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


if __name__=='__main__':print(json.dumps(transform()))
