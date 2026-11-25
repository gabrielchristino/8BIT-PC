`timescale 1ns/1ps
// NET-12 pin-derived access controller/decoder. Storage, bus data, MMIO and raster are simulation models.
// Epoch-tagged byte arrays permit independent fixtures without copying 96 KiB.
module isa1_memory #(parameter TIMED=0) (
 input wire clk,video_clk,reset_n,power_good,request,write_enable,
 input wire [15:0] address,input wire [7:0] write_data,
 output wire acknowledge,output wire [7:0] read_data,
 output reg boot,output reg [1:0] vb,row,output reg eb,
 output reg [7:0] pixel,output reg [7:0] h,output reg [9:0] v
);
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
 function [7:0] ram_read(input integer p);
   ram_read=ram_tag[p]==generation?ram[p]:(patterned_default?((p*17+(p>>8)+49)&255):0);
 endfunction
 function [7:0] vram_read(input integer p);
   vram_read=vram_tag[p]==generation?vram[p]:(patterned_default?((p*17+(p>>8)+93)&255):0);
 endfunction
 function [7:0] rom_read(input integer p);
   rom_read=rom_tag[p]==generation?eeprom[p]:(patterned_default?((p*17+(p>>8)+167)&255):0);
 endfunction
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
