"""NET-12 integration adapter; storage/MMIO/raster remain explicit models."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def once(s,old,new):
    if s.count(old)!=1:raise ValueError('Unexpected base '+old[:70])
    return s.replace(old,new)


def main():
    base=ROOT/'sim/rtl/isa1_memory.sv';original=base.read_text()
    interface=original[:original.index(');')+2]
    interface=interface.replace('module isa1_memory (','module isa1_memory #(parameter TIMED=0) (').replace('// Simulation-only memory/MMIO and VGA arbitration. No physical memory timing.','// NET-12 pin-derived access controller/decoder. Storage, bus data, MMIO and raster are simulation models.')
    helpers=original[original.index(' function [7:0] ram_read'):original.index(' task io_read;')]
    declarations='''
 reg [7:0] ram[0:32767],vram[0:32767],eeprom[0:32767];
 integer ram_tag[0:32767],vram_tag[0:32767],rom_tag[0:32767];
 integer generation=0,writes=0,transactions=0,vram_transactions=0,ram_writes=0,vram_writes=0;
 integer committed_kind,committed_address;reg committed_write=0;reg [7:0] committed_data;
 reg patterned_default=0;reg [63:0] keys=0;
 wire safe=reset_n && power_good;
 wire [15:0] saved_address;wire [7:0] saved_data;wire saved_write;
 wire accept,armed,bus_active,vram_owner,data_drive,oe_n,we_n,io_commit,read_capture;
 wire [3:0] select,cs_n;wire [5:0] io_select;wire [7:0] phase;
 wire [14:0] ram_address,vram_address,rom_address;wire [7:0] bus_read;
 reg vram_slot=0;reg [7:0] read_value;reg [15:0] cols;
 integer i;
 initial begin for(i=0;i<32768;i=i+1)begin ram_tag[i]=-1;vram_tag[i]=-1;rom_tag[i]=-1;end end
 memory_decode_netlist #(.TIMED(TIMED)) decode(saved_address,boot,eb,vb,1'b1,safe,select,io_select,ram_address,vram_address,rom_address);
 memory_access_netlist #(.TIMED(TIMED)) access_controller(
   .clk(video_clk),.reset_n(reset_n),.power_good(power_good),.request(request),.write_request(write_enable),.vram_slot(vram_slot),
   .address(address),.write_data(write_data),.read_bus(bus_read),.select(select),.ack(acknowledge),.accept(accept),.armed(armed),
   .held_write(saved_write),.bus_active(bus_active),.vram_owner(vram_owner),.data_drive(data_drive),.oe_n(oe_n),.we_n(we_n),.io_commit(io_commit),
   .read_capture(read_capture),.held_address(saved_address),.held_data(saved_data),.read_data(read_data),.cs_n(cs_n),.phase(phase));
 // Grant prepared in the opposite half cycle. Its final raster/clock circuit
 // and minimum/skew constraints are not implemented by this simulation model.
 always @(negedge video_clk or negedge safe)
   if(!safe)vram_slot<=0;else vram_slot<=h>=161 && h<=192;
'''
    behavior='''
 always @(keys or row)cols=columns();
 always @* begin
   read_value=8'hff;
   if(!oe_n)begin
     if(!cs_n[0])read_value=ram_read(ram_address);
     else if(!cs_n[1])read_value=vram_read(vram_address);
     else if(!cs_n[2])read_value=rom_read(rom_address);
   end
   if(!cs_n[3])case(io_select)
     6'b000001:read_value={6'b0,vb};6'b000010:read_value={7'b0,eb};6'b000100:read_value={7'b0,!boot};
     6'b010000:read_value=cols[7:0];6'b100000:read_value=cols[15:8];default:read_value=8'hff;
   endcase
 end
 // Selected data-return stimulus, not a vendor device/tri-state bus model.
 assign #(TIMED?220:0) bus_read=read_value;
 always @(posedge video_clk or negedge safe)begin
   if(!safe)begin boot<=1;vb<=0;eb<=0;row<=0;end
   else begin
     if(!we_n)begin
       if(!cs_n[0])begin ram[ram_address]<=saved_data;ram_tag[ram_address]<=generation;ram_writes=ram_writes+1;end
       else if(!cs_n[1])begin vram[vram_address]<=saved_data;vram_tag[vram_address]<=generation;vram_writes=vram_writes+1;end
     end
     if(io_commit)case(io_select)
       6'b000001:vb<=saved_data[1:0];6'b000010:eb<=saved_data[0];
       6'b000100:if(saved_data[0])boot<=0;6'b001000:row<=saved_data[1:0];
     endcase
     if(vram_owner && h<160)$fatal(1,"NET12 CPU owns VRAM during active video");
   end
 end
 always @(posedge acknowledge)if(safe)begin
   transactions=transactions+1;
   if(saved_write)writes=writes+1;
   if(select[1])vram_transactions=vram_transactions+1;
   committed_kind=select[0]?0:select[1]?1:select[2]?2:3;
   committed_address=select[0]?ram_address:select[1]?vram_address:select[2]?rom_address:saved_address;
   committed_write=saved_write;committed_data=saved_write?saved_data:0;
 end
 always @(posedge video_clk or negedge safe)begin
   if(!safe)begin h<=0;v<=0;pixel<=0;end
   else begin
     pixel<=h<160 && v<480?vram_read((v/4)*256+h):0;
     if(h==199)begin h<=0;v<=v==524?0:v+1'b1;end else h<=h+1'b1;
   end
 end
endmodule
'''
    dest=ROOT/'sim/net12/isa1_memory_access.sv';dest.write_text(interface+declarations+helpers+behavior)
    runner=ROOT/'tools/run_cpu_global.py';s=runner.read_text()
    s=once(s,"OUT=ROOT/'verification/net10'","OUT=ROOT/'verification/net12/cpu'")
    s=once(s,"'iteration':'NET-10'","'iteration':'NET-12'")
    s=once(s,"'sim/rtl/isa1_memory.sv'","'hardware/memory_decode/memory_decode_netlist.sv','hardware/memory_access/memory_access_netlist.sv','sim/net12/isa1_memory_access.sv'")
    s=once(s,"'tools/run_cpu_global.py'","'tools/run_cpu_global.py','tools/make_memory_access_cpu.py','tools/run_memory_access_cpu.py','tools/build_memory_access.py','hardware/memory_access/design.json','hardware/memory_access/package-functions.json','verification/net12/memory_access.xml','verification/net11/memory_decode.xml'")
    s=once(s,"        text=text.replace(' isa1_cpu dut(', ' isa1_cpu #(.TIMED(1)) dut(')","        text=text.replace(' isa1_cpu dut(', ' isa1_cpu #(.TIMED(1)) dut(')\n        text=text.replace('isa1_memory memory(', 'isa1_memory #(.TIMED(1)) memory(')")
    s=once(s,'    return text\n','''    # Fixed physical access phases replace the old variable-latency/ACK model.
    text=re.sub(r'memory\\.(latency|ack_hold)=[^;]+;', '',text)
    if 'held_state' in text:
        old='{pc,sp,x,a,b,z,c,halted,fault,boot,vb,eb,row}'
        if text.count(old)!=2:raise ValueError('WAIT fixture tuple changed')
        text=text.replace(old,"{pc,sp,x,a,b,z,c,halted,fault,6'b0}")
        # Peripheral effects occur at the physical IO_COMMIT before ACK; CPU
        # architectural registers remain strictly unchanged throughout WAIT.
        monitor="""
 always @(boot or vb or eb or row)if(active && req && reset_n && power_good)
   if(!memory.io_commit)$fatal(1,"MMIO change outside physical commit");
"""
        text=text.replace('endmodule',monitor+'endmodule')
    return text
''')
    s=once(s,'Joined CPU only; delayed scenario uses scaled slow CPU/video stimuli, not physical VGA timing or full PVT signoff',
      'CPU + pin-derived memory payload/controller/decoder; storage, MMIO, data bus and raster/grant remain models; fixed access phases replace variable latency; CPU WAIT held, MMIO changes only at physical IO_COMMIT; no board signoff')
    target=ROOT/'tools/run_memory_access_cpu.py';target.write_text('# GENERATED by tools/make_memory_access_cpu.py from NET-10 runner.\n'+s)
    (ROOT/'verification/net12/cpu').mkdir(parents=True,exist_ok=True)
    files=[base,runner,Path(__file__),dest,target]
    (ROOT/'verification/net12/adapter-origin.json').write_text(json.dumps({'date':'2026-11-25','transformation':'Original memory interface/helpers retained; behavioral transaction FSM replaced by NET-12 pin controller and NET-11 decoder. Arrays/MMIO/raster/slot/data-return remain simulation models; fixtures distinguish physical peripheral commit from CPU commit.',
      'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]},indent=2)+'\n')
    print('Generated NET-12 simulation adapter and separate CPU runner')


if __name__=='__main__':main()
