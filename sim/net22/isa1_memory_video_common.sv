`timescale 1ns/1ps
// NET-13 pin-derived memory/controller/decoder. Device models are not silicon/PCB proof; MMIO/keyboard/controller and raster/slot/capture are native pin netlists; switch contacts are ideal functional stimuli.
// Epoch-tagged byte arrays permit independent fixtures without copying 96 KiB.
module isa1_memory #(parameter TIMED=0,FIXTURE_DEFAULTS=1,CONTROL_EARLY=0,RESET_POLICY=1,parameter realtime BANK_ASSERT_NS=19000) (
 input wire clk,video_clk,reset_n,power_good,request,write_enable,
 input wire [15:0] address,input wire [7:0] write_data,
 output wire acknowledge,output wire [7:0] read_data,
 output wire boot,output wire [1:0] vb,row,output wire eb,
 output wire [7:0] pixel,output wire [7:0] h,output wire [9:0] v
);
 integer generation=0,writes=0,transactions=0,vram_transactions=0;
 wire [31:0] ram_writes=frontend.U1.normal_writes,vram_writes=frontend.U2.normal_writes;
 wire [31:0] ram_aborts=frontend.U1.aborted_writes,vram_aborts=frontend.U2.aborted_writes;
 integer committed_kind,committed_address;reg committed_write=0;reg [7:0] committed_data;
 reg patterned_default=0;reg [63:0] keys=0;
 wire raw_safe=reset_n && power_good;
 wire backend_clk;
 wire bank_memory_n,bank_keyboard_n,bank_decode_n,safe_memory,safe_keyboard;
 wire cpu_core_clk,cpu_reset_n,access_clk,keyboard_clk,bank_reset_n,safe;
 schmitt_reset_netlist #(.TIMED(TIMED),.RESOLVE_LATE(RESET_POLICY),
   .ASSERT_DELAY(TIMED?BANK_ASSERT_NS:1),.RELEASE_DELAY(TIMED?42000:4)) reset_domains(
   raw_safe,backend_clk,clk,bank_reset_n,cpu_reset_n,safe,
   bank_memory_n,bank_keyboard_n,bank_decode_n,safe_memory,safe_keyboard,
   cpu_core_clk,access_clk,keyboard_clk);
 wire [15:0] saved_address;wire [7:0] saved_data;wire saved_write;
 wire accept,armed,bus_active,vram_owner,data_drive,oe_n,we_n,io_commit,read_capture;
 wire [3:0] select,cs_n;wire [5:0] io_select;wire [7:0] phase;
 wire [14:0] ram_address,vram_address,rom_address;wire [7:0] bus_read;
 wire vram_slot,key_ready;wire [7:0] io_value;tri [3:0] row_wires;tri [15:0] column_wires;
 wire [7:0] pixel_bus;wire [14:0] video_address={v[8:2],h};
 wire capture_clk,visible,hsync_n,vsync_n,raster_ready;
 integer i;
 defparam raster.RESOLVE_LATE=RESET_POLICY;
 defparam peripheral.RESOLVE_LATE=RESET_POLICY;

 memory_decode_netlist #(.TIMED(TIMED)) decode(saved_address,boot,eb,vb,1'b1,bank_decode_n,select,io_select,ram_address,vram_address,rom_address);
 system_access_netlist #(.TIMED(TIMED),.EARLY(CONTROL_EARLY)) access_controller(
   .clk(access_clk),.reset_n(bank_memory_n),.power_good(1'b1),.request(request),.write_request(write_enable),.vram_slot(vram_slot),.key_ready(key_ready),.io_col_lo(io_select[4]),.io_col_hi(io_select[5]),
   .address(address),.write_data(write_data),.read_bus(bus_read),.select(select),.ack(acknowledge),.accept(accept),.armed(armed),
   .held_write(saved_write),.bus_active(bus_active),.vram_owner(vram_owner),.data_drive(data_drive),.oe_n(oe_n),.we_n(we_n),.io_commit(io_commit),
   .read_capture(read_capture),.held_address(saved_address),.held_data(saved_data),.read_data(read_data),.cs_n(cs_n),.phase(phase));
 // Verification-only epoch/pattern controls. No SRAM power-up state is
 // implied: the full boot program disables FIXTURE_DEFAULTS entirely.
 always @(generation or patterned_default)begin
   frontend.U1.generation=generation;frontend.U2.generation=generation;frontend.U3.generation=generation;
   frontend.U1.patterned_default=patterned_default;frontend.U2.patterned_default=patterned_default;frontend.U3.patterned_default=patterned_default;
   frontend.U1.fixture_seeded=FIXTURE_DEFAULTS;frontend.U2.fixture_seeded=FIXTURE_DEFAULTS;frontend.U3.fixture_seeded=FIXTURE_DEFAULTS;
 end
 memory_bus_netlist #(.TIMED(TIMED),.EARLY_ON(1)) frontend(
   .reset_n(bank_memory_n),.power_good(safe_memory),.vram_owner(vram_owner),.data_drive(data_drive),.oe_n(oe_n),.we_n(we_n),
   .ram_address(ram_address),.vram_address(vram_address),.rom_address(rom_address),.video_address(video_address),.write_data(saved_data),
   .io_data(io_value),.cs_n(cs_n),.select(select),.read_data(bus_read),.video_data(pixel_bus));
 // Master input feeds the KiCad pin raster; backend and capture are its
 // registered divided clocks. MMIO and its readiness now come from the native peripheral.
 video_common_clock_netlist #(.TIMED(TIMED),.EARLY_CAPTURE(1)) raster(
   video_clk,reset_n,power_good,pixel_bus,backend_clk,capture_clk,vram_slot,
   visible,hsync_n,vsync_n,raster_ready,h,v,pixel);
 function [7:0] ram_read(input integer p);ram_read=frontend.U1.peek(p);endfunction
 function [7:0] vram_read(input integer p);vram_read=frontend.U2.peek(p);endfunction
 function [7:0] rom_read(input integer p);rom_read=frontend.U3.peek(p);endfunction
 // Actual sampled columns and MMIO state come ONLY from the pin netlist.
 keyboard_500_netlist #(.TIMED(TIMED)) peripheral(
   keyboard_clk,bank_keyboard_n,safe_keyboard,io_commit,io_select,saved_data,row_wires,column_wires,
   boot,eb,vb,row,io_value,key_ready);
 genvar rr,cc;
 generate for(rr=0;rr<4;rr=rr+1)begin:MEMBRANE_ROW
   for(cc=0;cc<16;cc=cc+1)begin:MEMBRANE_COLUMN
     tranif1 contact(row_wires[rr],column_wires[cc],keys[rr*16+cc]);
   end
 end endgenerate
 always @(posedge backend_clk)if(safe && vram_owner && h<160)
   $fatal(1,"CPU owns VRAM during active video");
 always @(posedge acknowledge)if(safe)begin
   transactions=transactions+1;
   if(saved_write)writes=writes+1;
   if(select[1])vram_transactions=vram_transactions+1;
   committed_kind=select[0]?0:select[1]?1:select[2]?2:3;
   committed_address=select[0]?ram_address:select[1]?vram_address:select[2]?rom_address:saved_address;
   committed_write=saved_write;committed_data=saved_write?saved_data:0;
 end
endmodule
