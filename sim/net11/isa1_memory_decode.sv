`timescale 1ns/1ps
// NET-11: physical pin-derived address decode; storage/MMIO/CDC/arbitration remain simulation models.
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
 integer generation=0, latency=0, writes=0, transactions=0, vram_transactions=0;
 integer ram_writes=0,vram_writes=0;
 reg patterned_default=0;
 integer ack_hold=0,release_countdown=0;
 integer committed_kind,committed_address;
 reg committed_write=0;reg [7:0] committed_data;
 reg [63:0] keys=0;
 reg ack_cpu=0;reg [7:0] data_cpu;
 assign acknowledge=reset_n && power_good && ack_cpu;
 assign read_data=data_cpu;
 wire safe=reset_n && power_good;
 wire [3:0] region_select;wire [5:0] decoded_io;
 wire [14:0] ram_address,vram_address,rom_address;
 memory_decode_netlist #(.TIMED(TIMED)) address_decoder(address,boot,eb,vb,request,safe,
    region_select,decoded_io,ram_address,vram_address,rom_address);
 reg [15:0] saved_address; reg [7:0] saved_data;reg saved_write;
 integer physical,kind,countdown;
 localparam IDLE=0,DELAY=1,VIDEO=2,HOLD=3;
 reg [1:0] cpu_state;
 reg video_request,video_ack,req1,req2,ack1,ack2;
 reg [7:0] video_data;
 integer video_stage;
 integer i;
 initial begin
   for(i=0;i<32768;i=i+1) begin ram_tag[i]=-1;vram_tag[i]=-1;rom_tag[i]=-1;end
 end
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
 task io_read;
   reg [15:0] cols;
   begin
     cols=columns();
     case(saved_address)
       16'ha000:data_cpu<={6'b0,vb};16'ha001:data_cpu<={7'b0,eb};
       16'ha002:data_cpu<={7'b0,!boot};
       16'ha011:data_cpu<=cols[7:0];16'ha012:data_cpu<=cols[15:8];
       default:data_cpu<=255;
     endcase
   end
 endtask
 always @(posedge clk or negedge safe) begin
   if(!safe) begin
     boot<=1;vb<=0;eb<=0;row<=0;ack_cpu<=0;data_cpu<=0;
     cpu_state<=IDLE;video_request<=0;ack1<=0;ack2<=0;
     saved_address<=0;saved_data<=0;saved_write<=0;physical<=0;kind<=0;countdown<=0;release_countdown<=0;
   end else begin
     ack1<=video_ack;ack2<=ack1;
     case(cpu_state)
       IDLE: if(request && !video_ack && !ack1 && !ack2) begin
         saved_address<=address;saved_data<=write_data;saved_write<=write_enable;
         case(region_select)
           4'b0001:begin kind<=0;physical<=ram_address;end
           4'b0010:begin kind<=1;physical<=vram_address;end
           4'b0100:begin kind<=2;physical<=rom_address;end
           4'b1000:begin kind<=3;physical<=address;end
           default:$fatal(1,"NET11 address decode not settled at capture");
         endcase
         countdown<=latency;cpu_state<=DELAY;
       end
       DELAY: if(countdown>0)countdown<=countdown-1;
       else if(kind==1)begin video_request<=1;cpu_state<=VIDEO;end
       else begin
         if(saved_write)begin
           if(kind==0)begin ram[physical]<=saved_data;ram_tag[physical]<=generation;ram_writes=ram_writes+1;end
           if(kind==3)case(saved_address)
             16'ha000:vb<=saved_data[1:0];16'ha001:eb<=saved_data[0];
             16'ha002:if(saved_data[0])boot<=0;
             16'ha010:row<=saved_data[1:0];
           endcase
           writes=writes+1;
         end else case(kind)
           0:data_cpu<=ram_read(physical);2:data_cpu<=rom_read(physical);3:io_read();
         endcase
         transactions=transactions+1;committed_kind=kind;committed_address=physical;
         committed_write=saved_write;committed_data=saved_write?saved_data:0;
         ack_cpu<=1;cpu_state<=HOLD;release_countdown<=ack_hold;
       end
       VIDEO: if(ack2)begin
         data_cpu<=video_data;video_request<=0;ack_cpu<=1;cpu_state<=HOLD;release_countdown<=ack_hold;
         transactions=transactions+1;
         if(saved_write)writes=writes+1;
       end
       HOLD: if(!request)begin
         if(release_countdown>0)release_countdown<=release_countdown-1;
         else begin ack_cpu<=0;cpu_state<=IDLE;end
       end
     endcase
   end
 end
 always @(posedge video_clk or negedge safe) begin
   if(!safe)begin h<=0;v<=0;pixel<=0;req1<=0;req2<=0;video_ack<=0;video_stage<=-1;video_data<=0;end
   else begin
     req1<=video_request;req2<=req1;
     pixel<=h<160 && v<480?vram_read((v/4)*256+h):0;
     if(h==199)begin h<=0;v<=v==524?0:v+1'b1;end else h<=h+1'b1;
     if(video_stage==-1 && req2 && h>=161 && h<=192)video_stage<=0;
     else if(video_stage>=0 && video_stage<4)begin
       if(h<161 || h>196)$fatal(1,"VRAM outside blanking window");
       video_stage<=video_stage+1;
       if(video_stage==1)begin
         if(saved_write)begin vram[physical]<=saved_data;vram_tag[physical]<=generation;vram_writes=vram_writes+1;end
         else video_data<=vram_read(physical);
         vram_transactions=vram_transactions+1;
       end
       if(video_stage==3)video_ack<=1;
     end else if(video_stage==4 && !req2)begin video_ack<=0;video_stage<=-1;end
   end
 end
endmodule
