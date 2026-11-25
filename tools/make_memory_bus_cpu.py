"""NET-13 CPU adapter: storage resides in pin-connected memory chip models."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def once(s,old,new):
    if s.count(old)!=1:raise ValueError('Unexpected base '+old[:80])
    return s.replace(old,new)


def main():
    base=ROOT/'sim/net12/isa1_memory_access.sv';s=base.read_text()
    s=s.replace('// NET-12 pin-derived access controller/decoder. Storage, bus data, MMIO and raster are simulation models.','// NET-13 pin-derived memory/controller/decoder. Device models are not silicon/PCB proof; MMIO/raster remain models.')
    s=once(s,'#(parameter TIMED=0)','#(parameter TIMED=0,FIXTURE_DEFAULTS=1)')
    s=once(s,' reg [7:0] ram[0:32767],vram[0:32767],eeprom[0:32767];\n integer ram_tag[0:32767],vram_tag[0:32767],rom_tag[0:32767];\n','')
    s=once(s,' integer generation=0,writes=0,transactions=0,vram_transactions=0,ram_writes=0,vram_writes=0;',
      ' integer generation=0,writes=0,transactions=0,vram_transactions=0;\n wire [31:0] ram_writes=frontend.U1.normal_writes,vram_writes=frontend.U2.normal_writes;\n wire [31:0] ram_aborts=frontend.U1.aborted_writes,vram_aborts=frontend.U2.aborted_writes;')
    s=once(s,' reg vram_slot=0;reg [7:0] read_value;reg [15:0] cols;',' reg vram_slot=0;reg [7:0] io_value;reg [15:0] cols;\n wire [7:0] pixel_bus;wire [14:0] video_address={v[8:2],h};')
    s=once(s,' initial begin for(i=0;i<32768;i=i+1)begin ram_tag[i]=-1;vram_tag[i]=-1;rom_tag[i]=-1;end end','')
    i=s.index(' // Grant prepared')
    s=s[:i]+''' // Verification-only epoch/pattern controls. No SRAM power-up state is
 // implied: the full boot program disables FIXTURE_DEFAULTS entirely.
 always @(generation or patterned_default)begin
   frontend.U1.generation=generation;frontend.U2.generation=generation;frontend.U3.generation=generation;
   frontend.U1.patterned_default=patterned_default;frontend.U2.patterned_default=patterned_default;frontend.U3.patterned_default=patterned_default;
   frontend.U1.fixture_seeded=FIXTURE_DEFAULTS;frontend.U2.fixture_seeded=FIXTURE_DEFAULTS;frontend.U3.fixture_seeded=FIXTURE_DEFAULTS;
 end
 memory_bus_netlist #(.TIMED(TIMED),.EARLY_ON(1)) frontend(
   .reset_n(reset_n),.power_good(power_good),.vram_owner(vram_owner),.data_drive(data_drive),.oe_n(oe_n),.we_n(we_n),
   .ram_address(ram_address),.vram_address(vram_address),.rom_address(rom_address),.video_address(video_address),.write_data(saved_data),
   .io_data(io_value),.cs_n(cs_n),.select(select),.read_data(bus_read),.video_data(pixel_bus));
'''+s[i:]
    a=s.index(' function [7:0] ram_read');b=s.index(' function [15:0] columns;')
    s=s[:a]+''' function [7:0] ram_read(input integer p);ram_read=frontend.U1.peek(p);endfunction
 function [7:0] vram_read(input integer p);vram_read=frontend.U2.peek(p);endfunction
 function [7:0] rom_read(input integer p);rom_read=frontend.U3.peek(p);endfunction
'''+s[b:]
    a=s.index(' always @* begin');b=s.index(' always @(posedge video_clk or negedge safe)begin',a)
    s=s[:a]+''' always @* begin
   io_value=8'hff;
   case(io_select)
     6'b000001:io_value={6'b0,vb};6'b000010:io_value={7'b0,eb};6'b000100:io_value={7'b0,!boot};
     6'b010000:io_value=cols[7:0];6'b100000:io_value=cols[15:8];default:io_value=8'hff;
   endcase
 end
'''+s[b:]
    a=s.index('     if(!we_n)begin');b=s.index('     if(io_commit)',a);s=s[:a]+s[b:]
    s=once(s,'vram_read((v/4)*256+h):0','pixel_bus:0')
    dest=ROOT/'sim/net13/isa1_memory_bus.sv';dest.write_text(s)
    oldrunner=ROOT/'tools/run_memory_access_cpu.py';r=oldrunner.read_text()
    r=once(r,"OUT=ROOT/'verification/net12/cpu'","OUT=ROOT/'verification/net13/cpu'")
    r=once(r,"'iteration':'NET-12'","'iteration':'NET-13'")
    r=r.replace("'hardware/memory_access/memory_access_netlist.sv','sim/net12/isa1_memory_access.sv'","'hardware/memory_bus_access/memory_access_netlist.sv','sim/net13/memory_devices.sv','hardware/memory_bus/memory_bus_netlist.sv','sim/net13/isa1_memory_bus.sv'")
    r=once(r,"'tools/make_memory_access_cpu.py','tools/run_memory_access_cpu.py'","'tools/make_memory_access_cpu.py','tools/run_memory_access_cpu.py','tools/make_memory_bus_cpu.py','tools/run_memory_bus_cpu.py','tools/build_memory_bus.py','tools/prepare_memory_bus_access.py','tools/build_memory_bus_access.py','hardware/memory_bus/design.json','hardware/memory_bus/package-functions.json','verification/net13/memory_bus.xml','hardware/memory_bus_access/design.json','hardware/memory_bus_access/package-functions.json','verification/net13/access/memory_access.xml'")
    r=once(r,'    return text\n','''    # Retain original fixture semantics by seeding the component arrays,
    # without wrapper storage or pretending that reset initializes SRAM.
    for old,new in [('ram_tag','frontend.U1.tag'),('vram_tag','frontend.U2.tag'),('rom_tag','frontend.U3.tag'),('ram','frontend.U1.mem'),('vram','frontend.U2.mem'),('eeprom','frontend.U3.mem')]:
        text=text.replace('memory.'+old+'[','memory.'+new+'[')
    if 'module tb_rtl_program;' in text:
        if timed:text=text.replace('isa1_memory #(.TIMED(1)) memory(', 'isa1_memory #(.TIMED(1),.FIXTURE_DEFAULTS(0)) memory(')
        else:text=text.replace('isa1_memory memory(', 'isa1_memory #(.FIXTURE_DEFAULTS(0)) memory(')
    if 'isa1_memory ' in text:
        text=text.replace('$finish;', '$display("MEMORY_MODEL ram_valid_writes=%0d vram_valid_writes=%0d ram_aborts=%0d vram_aborts=%0d fixture_defaults=%0d",memory.ram_writes,memory.vram_writes,memory.ram_aborts,memory.vram_aborts,memory.FIXTURE_DEFAULTS);$finish;')
    return text
''')
    r=r.replace('CPU + pin-derived memory payload/controller/decoder; storage, MMIO, data bus and raster/grant remain models; fixed access phases replace variable latency; CPU WAIT held, MMIO changes only at physical IO_COMMIT; no board signoff',
      'CPU + pin-derived SRAM/EEPROM/bus/decoder/controller with selected component timing; MMIO/raster/grant remain models; full boot starts with unknown unseeded SRAM; vector fixtures seed component arrays; no PCB/load/analog/PVT signoff')
    target=ROOT/'tools/run_memory_bus_cpu.py';target.write_text('# GENERATED by tools/make_memory_bus_cpu.py; predecessor sources preserved.\n'+r)
    (ROOT/'verification/net13/cpu').mkdir(parents=True,exist_ok=True)
    paths=[base,oldrunner,Path(__file__),dest,target]
    (ROOT/'verification/net13/adapter-origin.json').write_text(json.dumps({'date':'2026-11-25','transformation':'NET-12 simulation wrapper loses its storage/data-return stand-ins. Component models from KiCad memory bus now own bytes, tri-state buses and write edges. MMIO/raster/grant remain models; fixtures explicitly seed chip arrays and the full program disables artificial SRAM defaults.',
      'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]},indent=2)+'\n')
    print('Generated pin-memory CPU adapter; full boot SRAM starts unknown')


if __name__=='__main__':main()
