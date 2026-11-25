`timescale 1ns/1ps
// NET-13 pin-derived memory/controller/decoder. Device models are not silicon/PCB proof; MMIO remains a model; raster/slot/capture are native pin netlists.
// Epoch-tagged byte arrays permit independent fixtures without copying 96 KiB.
module isa1_memory #(parameter TIMED=0,FIXTURE_DEFAULTS=1) (
 input wire clk,video_clk,reset_n,power_good,request,write_enable,
 input wire [15:0] address,input wire [7:0] write_data,
 output wire acknowledge,output wire [7:0] read_data,
 output reg boot,output reg [1:0] vb,row,output reg eb,
 output wire [7:0] pixel,output wire [7:0] h,output wire [9:0] v
);
 integer generation=0,writes=0,transactions=0,vram_transactions=0;
 wire [31:0] ram_writes=frontend.U1.normal_writes,vram_writes=frontend.U2.normal_writes;
 wire [31:0] ram_aborts=frontend.U1.aborted_writes,vram_aborts=frontend.U2.aborted_writes;
 integer committed_kind,committed_address;reg committed_write=0;reg [7:0] committed_data;
 reg patterned_default=0;reg [63:0] keys=0;
 wire safe=reset_n && power_good;
 wire [15:0] saved_address;wire [7:0] saved_data;wire saved_write;
 wire accept,armed,bus_active,vram_owner,data_drive,oe_n,we_n,io_commit,read_capture;
 wire [3:0] select,cs_n;wire [5:0] io_select;wire [7:0] phase;
 wire [14:0] ram_address,vram_address,rom_address;wire [7:0] bus_read;
 wire vram_slot;reg [7:0] io_value;reg [15:0] cols;
 wire [7:0] pixel_bus;wire [14:0] video_address={v[8:2],h};
 wire backend_clk,capture_clk,visible,hsync_n,vsync_n,raster_ready;
 integer i;

 memory_decode_netlist #(.TIMED(TIMED)) decode(saved_address,boot,eb,vb,1'b1,safe,select,io_select,ram_address,vram_address,rom_address);
 memory_access_netlist #(.TIMED(TIMED)) access_controller(
   .clk(backend_clk),.reset_n(reset_n),.power_good(power_good),.request(request),.write_request(write_enable),.vram_slot(vram_slot),
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
   .reset_n(reset_n),.power_good(power_good),.vram_owner(vram_owner),.data_drive(data_drive),.oe_n(oe_n),.we_n(we_n),
   .ram_address(ram_address),.vram_address(vram_address),.rom_address(rom_address),.video_address(video_address),.write_data(saved_data),
   .io_data(io_value),.cs_n(cs_n),.select(select),.read_data(bus_read),.video_data(pixel_bus));
 // Master input feeds the KiCad pin raster; backend and capture are its
 // registered divided clocks. MMIO is still the preserved logical peripheral.
 video_system_netlist #(.TIMED(TIMED),.EARLY_CAPTURE(1)) raster(
   video_clk,reset_n,power_good,pixel_bus,backend_clk,capture_clk,vram_slot,
   visible,hsync_n,vsync_n,raster_ready,h,v,pixel);
 function [7:0] ram_read(input integer p);ram_read=frontend.U1.peek(p);endfunction
 function [7:0] vram_read(input integer p);vram_read=frontend.U2.peek(p);endfunction
 function [7:0] rom_read(input integer p);rom_read=frontend.U3.peek(p);endfunction
 function [15:0] columns;
   reg [3:0] rs,next_rs;reg [15:0] cs,next_cs;
   integer pass,r,col;
   begin
     rs=4'b1<<row;cs=0;
     // Connected component of an undioded 4x16 matrix. Inactive rows are Hi-Z.
     for(pass=0;pass<20;pass=pass+1) begin
       next_rs=rs;next_cs=cs;
       for(r=0;r<4;r=r+1) for(col=0;col<16;col=col+1)
         if(keys[r*16+col]) begin
           if(rs[r])next_cs[col]=1;
           if(cs[col])next_rs[r]=1;
         end
       rs=next_rs;cs=next_cs;
     end
     columns=~cs;
   end
 endfunction

 always @(keys or row)cols=columns();
 always @* begin
   io_value=8'hff;
   case(io_select)
     6'b000001:io_value={6'b0,vb};6'b000010:io_value={7'b0,eb};6'b000100:io_value={7'b0,!boot};
     6'b010000:io_value=cols[7:0];6'b100000:io_value=cols[15:8];default:io_value=8'hff;
   endcase
 end
 always @(posedge backend_clk or negedge safe)begin
   if(!safe)begin boot<=1;vb<=0;eb<=0;row<=0;end
   else begin
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
endmodule
