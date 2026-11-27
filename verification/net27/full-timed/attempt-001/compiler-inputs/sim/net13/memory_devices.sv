`timescale 1ns/1ps
// Selected datasheet pin/timing models, not vendor transistor/IBIS models.
// Tags/defaults are verification fixtures. SRAM has no reset and is unknown
// before a write unless a bench explicitly seeds a fixture or loads an image.
module parallel_memory_32k #(parameter TIMED=0,READ_ONLY=0,SEED=49,EARLY_ON=0)(
 input wire [14:0] a,input wire ce_n,oe_n,we_n,inout wire [7:0] io,
 input wire checks_valid,output reg driving=0);
 localparam T_AA=TIMED?(READ_ONLY?150:20):0;
 localparam T_OH=TIMED?(READ_ONLY?0:3):0;
 localparam T_ON=TIMED?(EARLY_ON?0:3):0;
 localparam T_OFF=TIMED?(READ_ONLY?50:5):0;
 reg [7:0] mem[0:32767];integer tag[0:32767];
 integer generation=0,normal_writes=0,aborted_writes=0,update_seq=0;
 reg fixture_seeded=0,patterned_default=0;
 reg address_good=0,control_good=0;reg [7:0] read_value=8'hxx;
 integer address_serial=0,control_serial=0,i;
 realtime address_changed=0,data_changed=0,write_started=0,last_write_end=-1000;
 reg write_active=0,write_address_changed=0;reg [14:0] write_address;
 initial for(i=0;i<32768;i=i+1)tag[i]=-1;
 function [7:0] peek(input integer p);
   if(tag[p]==generation)peek=mem[p];
   else if(fixture_seeded)peek=patterned_default?((p*17+(p>>8)+SEED)&255):0;
   else peek=8'hxx;
 endfunction
 task automatic address_event(input [14:0] addr,input integer ticket);
 begin
   #T_OH;if(ticket==address_serial)address_good=0;
   #(T_AA-T_OH);
   if(ticket==address_serial)begin read_value=peek(addr);address_good=1;end
 end
 endtask
 always @(a)begin
   address_changed=$realtime;
   if(write_active)begin
     write_address_changed=1;
     if(checks_valid)$fatal(1,"SRAM address changed during active write");
   end
 end
 always @(a or generation or fixture_seeded or patterned_default or update_seq)begin
   address_serial=address_serial+1;
   fork address_event(a,address_serial);join_none
 end
 task automatic control_event(input bit enable,input integer ticket);
 begin
   if(enable)begin
     #T_ON;if(ticket==control_serial)driving=1;
     #(T_AA-T_ON);if(ticket==control_serial)control_good=1;
   end else begin
     control_good=0;
     #T_OFF;if(ticket==control_serial)driving=0;
   end
 end
 endtask
 always @(ce_n or oe_n or we_n)begin
   control_serial=control_serial+1;
   fork control_event(!ce_n && !oe_n && we_n,control_serial);join_none
 end
 assign io=driving?(address_good && control_good?read_value:8'hxx):8'hzz;
 always @(io)data_changed=$realtime;
 always @(ce_n or we_n)begin
   if(READ_ONLY && !we_n)$fatal(1,"EEPROM programming is not implemented; WE must stay HIGH");
   if(!READ_ONLY)begin
     if(!ce_n && !we_n && !write_active)begin
       write_active=1;write_started=$realtime;write_address=a;write_address_changed=0;
     end else if(write_active && (ce_n || we_n))begin
       write_active=0;
       if(!checks_valid || write_address_changed || $isunknown(io) ||
          (TIMED && ($realtime-write_started<12 || $realtime-address_changed<12 ||
                     $realtime-data_changed<10 || $realtime-last_write_end<20)))begin
         mem[write_address]=8'hxx;tag[write_address]=generation;aborted_writes=aborted_writes+1;
         if(checks_valid)$fatal(1,"SRAM write timing/data violation");
       end else begin
         mem[a]=io;tag[a]=generation;normal_writes=normal_writes+1;
       end
       last_write_end=$realtime;update_seq=update_seq+1;
     end
   end
 end
endmodule
