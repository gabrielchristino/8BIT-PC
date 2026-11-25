"""NET-04 adapter: replace ROM/IR/microstep/fetch and SP decode, keep NET-03."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def transform_cpu():
    source=ROOT/"sim/net03/isa1_cpu_bus.sv";text=source.read_text()
    changes=[
     ('parameter ROM_FILE="control.hex"','parameter ROM_PREFIX="control_lane"'),
     ('reg [31:0] rom [0:8191];\n initial $readmemh(ROM_FILE,rom);\n reg fetch_bank; reg [3:0] microstep; reg [7:0] ir; wire [7:0] mdr;',
      'wire fetch_bank; wire [3:0] microstep; wire [7:0] ir; wire [7:0] mdr;\n wire control_ready,execute_clk,dispatch;'),
     ('wire x_count=USE_HC191 && state==EXEC && run && !halted && (x_op==2 || x_op==3);',
      'wire x_count=USE_HC191 && state==EXEC && run && !halted && control_ready && (x_op==2 || x_op==3);'),
     ('counter_load_candidate x_bank','counter_word_candidate x_bank'),
     ('assign control_address = {fetch_bank,fetch_bank?8\'b0:ir,microstep};\n assign control_word = rom[control_address];',
      '// Control address/word now come from the exported ROM/sequencer netlist.'),
     ("wire sp_down=addr_sel==5 || sp_op==2;\n wire sp_update=safe && run && !halted && state==EXEC &&\n                (!USE_HC191 || x_ready) && mem==0 && (sp_op==1 || sp_op==2);",'wire sp_down,sp_update;'),
     ('reg [15:0] selected_address;', '''reg [15:0] selected_address;
 wire execute_pulse=safe && state==EXEC && run && !halted && (!USE_HC191 || x_ready) && mem==0;
 wire seq_advance=(state==DROP && bus_ready) ||
   (state==X_LOAD && run && (x_done || x_load_completed)) ||
   (execute_pulse && !control_word[25] && !(USE_HC191 && x_op==1));
 microcode_bank_netlist #(.ROM_PREFIX(ROM_PREFIX)) micro_bank(
   .clk(clk),.reset_n(reset_n),.power_good(power_good),.advance_req(seq_advance),.execute_pulse(execute_pulse),.opcode(mdr),
   .control_ready(control_ready),.execute_clk(execute_clk),.dispatch(dispatch),.fetch(fetch_bank),.step(microstep),.ir(ir),
   .rom_address(control_address),.control_word(control_word),.sp_update(sp_update),.sp_down(sp_down));'''),
     ('if(fetch_bank && microstep==1) begin fetch_bank<=0;microstep<=0;ir<=value;stack_checked<=0;end\n     else if(control_word[24]) begin fetch_bank<=1;microstep<=0;retired<=1;end\n     else microstep<=microstep+1\'b1;',
      'if(fetch_bank && microstep==1) stack_checked<=0;\n     else if(control_word[24]) retired<=1;'),
     ('always @(posedge clk or negedge safe)','always @(posedge execute_clk or negedge safe)'),
     ('ea<=0;ir<=0;fetch_bank<=1;microstep<=0;','ea<=0;'),
     ('DROP: if(bus_ready)','DROP: if(bus_ready && control_ready)'),
     ('if(run && (x_done || x_load_completed))','if(run && control_ready && (x_done || x_load_completed))'),
     ('EXEC: if(run && !halted && (!USE_HC191 || x_ready))','EXEC: if(run && !halted && control_ready && (!USE_HC191 || x_ready))'),
     ('5:ir<=value;','5:begin end // IR is captured on dispatch by HC377.')]
    for old,new in changes:
        if text.count(old)!=1:raise ValueError('Unexpected NET-03 source: '+old)
        text=text.replace(old,new)
    counter_source=ROOT/'sim/hdl/counter_load_candidate.sv'
    counter=counter_source.read_text()
    for old,new in [('module counter_load_candidate','module counter_word_candidate'),
        ('reg request_seen, direction;','reg request_seen;\n    wire direction=down; // Direction already held by the opposite-phase control register.'),
        ('state<=INIT;request_seen<=0;direction<=0;','state<=INIT;request_seen<=0;'),
        ('            direction<=down;','')]:
        if counter.count(old)!=1:raise ValueError('Unexpected counter base: '+old)
        counter=counter.replace(old,new)
    (ROOT/'sim/net04/counter_word_candidate.sv').write_text('// GENERATED from '+hashlib.sha256(counter_source.read_bytes()).hexdigest()+'; CWR supplies held direction.\n'+counter)
    dest=ROOT/'sim/net04/isa1_cpu_microcode.sv';dest.write_text('// GENERATED NET-04 source SHA256 '+hashlib.sha256(source.read_bytes()).hexdigest()+'\n'+text)
    record={'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'output':dest.relative_to(ROOT).as_posix(),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
      'transformation':'Replace ROM/IR/microstep/fetch and SP decode by pin-connected bank; core clocks with same sequencer clock branch; preserve bus/SP/ISA'}
    record['counter_direction_source']={'path':counter_source.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(counter_source.read_bytes()).hexdigest(),
        'transformation':'Replace redundant negative-edge direction sampling by direction already held in registered control word'}
    out=ROOT/'verification/net04';out.mkdir(parents=True,exist_ok=True);(out/'cpu-transformation.json').write_text(json.dumps(record,indent=2)+'\n');return record


if __name__=='__main__':print(json.dumps(transform_cpu()))
