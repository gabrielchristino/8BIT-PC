`timescale 1ns/1ps
module tb_memory_access;
 parameter integer TIMED=0,SMOKE=0;
 parameter realtime HALF=500;
 reg clk=0,reset_n=0,power_good=1,request=1,write_request=0;
 reg [15:0] address=0;reg [7:0] write_data=0;
 reg boot=0,eb=0;reg [1:0] vb=0;
 wire ack,accept,armed,held_write,bus_active,vram_owner,data_drive,oe_n,we_n,io_commit,read_capture;
 wire [15:0] held_address;wire [7:0] held_data,read_data;wire [3:0] cs_n,select;wire [5:0] ios;
 wire [14:0] ra,va,ea;wire [7:0] phase;
 reg [7:0] h=0;
 always #HALF clk=~clk;
 // Synchronous grant stimulus is prepared half a cycle before controller CLK.
 // This is not the final physical raster or its timing proof.
 always @(negedge clk)h<=h==199?0:h+1;
 wire slot=h>=161 && h<=192;
 wire safe=reset_n && power_good;
 wire [7:0] read_bus;
 function [7:0] value(input [15:0] addr);value=addr[7:0]^addr[15:8]^8'ha6;endfunction
 // Simulation data source, delayed from actual chip/OE enables; not a device model.
 assign #(TIMED?220:0) read_bus=(!oe_n || !cs_n[3])?value(held_address):8'hff;
 memory_decode_netlist #(.TIMED(TIMED)) decode(held_address,boot,eb,vb,1'b1,safe,select,ios,ra,va,ea);
 keyboard_access_netlist #(.TIMED(TIMED)) dut(.*,.vram_slot(slot),.key_ready(1'b1),.io_col_lo(1'b0),.io_col_hi(1'b0));
 integer accepted=0,write_pulses=0,io_writes=0,reads=0,completed=0,tests=0,cuts=0;
 integer op,r,k,delay_phase,limit,n,prior,aw,iw,rc,ac;
 reg [15:0] saved_address;reg [7:0] saved_data;reg saved_write;
 reg watch=0;reg was_ack=0;realtime we_started=0;realtime min_we=1e9;
 reg [31:0] slot_starts=0;
 reg [23:0] reset_payload;
 genvar g;
 generate for(g=0;g<4;g=g+1)begin:chip_enable_checks
   always @(posedge cs_n[g])if(safe && bus_active && select[g])$fatal(1,"chip enable glitch during owned access");
 end endgenerate
 always @(posedge oe_n)if(safe && bus_active && !held_write && |select[2:0])$fatal(1,"read enable glitch during owned access");
 always @(posedge clk)if(safe)begin
   if(phase[2] && slot && select[1])slot_starts[h-161]=1;
   if(accept)begin
     accepted=accepted+1;saved_address=address;saved_data=write_data;saved_write=write_request;watch=1;
   end
   if(io_commit)io_writes=io_writes+1;
   if(read_capture)reads=reads+1;
 end
 always @(negedge we_n)if(safe)begin write_pulses=write_pulses+1;we_started=$realtime;end
 always @(posedge we_n)if(safe && we_started>0)begin
   if($realtime-we_started<min_we)min_we=$realtime-we_started;
   if(TIMED && $realtime-we_started<20)$fatal(1,"write pulse below selected 20ns fixture bound");
   we_started=0;
 end
 always @(negedge clk)begin
   #25;
   if(safe)begin
     if(phase!==0 && (phase & (phase-1))!==0)$fatal(1,"one-hot phase violation");
     if(watch && ({held_address,held_data,held_write}!=={saved_address,saved_data,saved_write}))$fatal(1,"held payload changed");
     if(vram_owner && h<160)$fatal(1,"VRAM owner reached visible pixels h=%0d",h);
     if(data_drive && (!oe_n || !cs_n[2]))$fatal(1,"read/write or EEPROM drive conflict");
     if(!we_n && (!data_drive || !oe_n || cs_n[0]&&cs_n[1]))$fatal(1,"invalid write enable");
     if(ack && (bus_active || vram_owner || !we_n || !oe_n || cs_n!=15))$fatal(1,"ACK retained bus ownership");
     if(ack && !was_ack)completed=completed+1;
     was_ack=ack;
   end else begin watch=0;was_ack=0;end
 end
 task ready;
 begin
   limit=0;
   while(!armed)begin @(negedge clk);limit=limit+1;if(limit>50)$fatal(1,"arm timeout");end
 end
 endtask
 task transact(input [15:0] addr,input bit wr,input [7:0] data,input integer hold_cycles);
 begin
   request=0;ready();@(negedge clk);#(HALF/3);
   address=addr;write_request=wr;write_data=data;ac=accepted;aw=write_pulses;iw=io_writes;rc=reads;request=1;
   limit=0;while(accepted==ac)begin @(negedge clk);limit=limit+1;if(limit>50)$fatal(1,"accept timeout");end
   #30;
   // Stronger than the CPU protocol: disturb all source payload pins after capture.
   address=~addr;write_data=~data;write_request=~wr;
   limit=0;while(!ack)begin @(negedge clk);limit=limit+1;if(limit>240)$fatal(1,"ACK timeout");end
   #25;
   if(!wr && read_data!==value(addr))$fatal(1,"read capture mismatch got=%h expected=%h",read_data,value(addr));
   if(accepted!=ac+1 || write_pulses!=aw+(wr && addr<16'ha000 && !(boot && addr<16'h4000)) || io_writes!=iw+(wr && addr>=16'ha000 && addr<16'hc000) || reads!=rc+!wr)
     $fatal(1,"single-effect mismatch addr=%h wr=%b accept=%0d write=%0d IO=%0d reads=%0d",addr,wr,accepted-ac,write_pulses-aw,io_writes-iw,reads-rc);
   repeat(hold_cycles)@(negedge clk);
   #25;
   if(accepted!=ac+1 || !ack || bus_active || vram_owner)$fatal(1,"held ACK/request repeated or occupied bus");
   request=0;watch=0;ready();tests=tests+1;
 end
 endtask
 task cut_at(input integer p,input integer power_cut,input integer wr,input [15:0] addr);
 begin
   request=0;watch=0;ready();@(negedge clk);address=addr;write_data=8'h59;write_request=wr;request=1;
   limit=0;while(!phase[p])begin @(negedge clk);limit=limit+1;if(limit>240)$fatal(1,"cut phase timeout %0d",p);end
   #35;watch=0;reset_payload={held_address,held_data};
   if(power_cut)power_good=0;else reset_n=0;
   // Keep the accepted payload and source request high across reset. Any
   // in-flight physical write may be truncated: no rollback/atomicity claim.
   #1000;
   if(ack || bus_active || vram_owner || !oe_n || !we_n || cs_n!=15 || io_commit || read_capture)$fatal(1,"unsafe access after response budget");
   if({held_address,held_data}!==reset_payload)$fatal(1,"reset changed retained write payload");
   repeat(8)@(negedge clk);
   #25;prior=accepted;
   reset_n=1;power_good=1;
   repeat(15)@(negedge clk);
   #25;if(accepted!=prior || ack || bus_active)$fatal(1,"stale request replayed after reset");
   request=0;watch=0;ready();cuts=cuts+1;
 end
 endtask
 initial begin
   // A request already high when reset is released must not be accepted.
   repeat(12)@(negedge clk);reset_n=1;
   repeat(15)@(negedge clk);#25;
   if(accepted || ack || armed)$fatal(1,"startup stale request accepted");
   request=0;ready();
   transact(16'hc123,0,8'h31,2);
   if(SMOKE)begin $display("RESULT smoke failures=0");$finish;end
   for(op=0;op<2;op=op+1)for(r=0;r<4;r=r+1)for(k=0;k<64;k=k+1)begin
     boot=k[0];eb=k[1];vb=k[3:2];
     transact((r==0?16'h0100:r==1?16'h8100:r==2?16'hc100:16'ha000)+k,op,k,1+(k%9));
   end
   // Every payload pin must independently retain both logic levels.
   boot=0;
   for(k=0;k<16;k=k+1)begin
     transact(16'b1<<k,k[0],8'h96,1);
     transact(~(16'b1<<k),!k[0],8'h69,1);
   end
   for(k=0;k<8;k=k+1)begin
     transact(16'h4567,1,8'b1<<k,1);
     transact(16'h4567,1,~(8'b1<<k),1);
   end
   // Hold completion for more than a video frame. VRAM must remain released.
   boot=0;transact(16'h8123,1,8'h7c,105100);
   for(k=0;k<200;k=k+1)begin
     while(h!=k)@(negedge clk);
     transact(16'h8345,k[0],k,1);
   end
   if(slot_starts!==32'hffffffff)$fatal(1,"grant boundary coverage missing %h",slot_starts);
   for(op=0;op<2;op=op+1)for(r=0;r<8;r=r+1)for(k=0;k<8;k=k+1)begin
     boot=0;cut_at(k,op,r[0],r<2?16'h4234:r<4?16'h8234:r<6?16'hc234:16'ha000);
     transact(16'hc124,0,0,1);
   end
   $display("RESULT timed=%0d half=%0f transactions=%0d reset_cuts=%0d accepted=%0d completed=%0d write_pulses=%0d io_writes=%0d reads=%0d min_write_ns=%0f failures=0",TIMED,HALF,tests,cuts,accepted,completed,write_pulses,io_writes,reads,min_we);$finish;
 end
endmodule
