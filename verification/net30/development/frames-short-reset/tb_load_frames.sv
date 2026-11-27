`timescale 1ns/1ps
// Separate native-system raster test. VRAM and VB are explicit fixture seeds;
// this bench never claims unseeded CPU boot or analog/PVT/DAC qualification.
module tb_load_frames;
 parameter POLICY=1,EARLY_CAPTURE=1;
 defparam memory.raster.EARLY_CAPTURE=EARLY_CAPTURE;
 reg raw=1,request=0;
 wire ack,boot,eb;wire [1:0] vb,row;
 wire [7:0] read_data,pixel,h;wire [9:0] v;
 isa1_clocked_memory #(.TIMED(1),.FIXTURE_DEFAULTS(0),.RESET_POLICY(POLICY)) memory(
   raw,1'b1,1'b1,request,1'b1,16'h9ffe,8'h39,ack,read_data,boot,vb,row,eb,pixel,h,v);
 wire master=memory.master_source,backend=memory.backend_clk,capture=memory.capture_clk;
 wire owner=memory.vram_owner,visible=memory.visible,hsync_n=memory.hsync_n,vsync_n=memory.vsync_n;
 integer samples=0,active=0,hs=0,vs=0,writes=0,frames=0,i,ex_h=0,ex_v=0;
 reg monitoring=0;reg [31:0] starts=0;
 function [7:0] pattern(input integer address);pattern=(address*17+(address>>8)+93)&255;endfunction
 always @(posedge backend)if(monitoring && memory.phase[2] && memory.vram_slot && memory.select[1] && h>=161 && h<=192)starts[h-161]=1;
 always @(posedge capture)if(monitoring)begin
   if(h!==ex_h || v!==ex_v)$fatal(1,"native frame raster mismatch %0d,%0d expected%0d,%0d",h,v,ex_h,ex_v);
   #60;
   if(!memory.raster_ready)$fatal(1,"native capture not initialized");
   if(visible!==(ex_h<160 && ex_v<480))$fatal(1,"native visible mismatch");
   if(hsync_n!==!(ex_h>=164 && ex_h<188) || vsync_n!==!(ex_v>=490 && ex_v<492))$fatal(1,"native sync mismatch");
   if(visible)begin
     if(owner)$fatal(1,"native visible VRAM owner");
     if(pixel!==pattern((ex_v/4)*256+ex_h))$fatal(1,"native frame pixel mismatch %0d,%0d got%h",ex_h,ex_v,pixel);
     active=active+1;
   end else if(pixel!==0)$fatal(1,"native blanking not black");
   samples=samples+1;if(!hsync_n)hs=hs+1;if(!vsync_n)vs=vs+1;
   if(ex_h==199)begin ex_h=0;if(ex_v==524)begin ex_v=0;frames=frames+1;end else ex_v=ex_v+1;end else ex_h=ex_h+1;
   if(frames==2)begin
     if(active!=153600 || hs!=25200 || vs!=800 || writes<100 || starts!==32'hffffffff)$fatal(1,"native frame coverage incomplete writes%0d starts%h",writes,starts);
     if(memory.frontend.U2.aborted_writes!=0)$fatal(1,"native frame write abort");
     $display("RESULT native_frames=2 samples=%0d visible=%0d hsync=%0d vsync=%0d writes=%0d grant_starts=32 policy=%0d early_capture=%0d seeded_vram=1 seeded_vb=1 failures=0",samples,active,hs,vs,writes,POLICY,EARLY_CAPTURE);
     $finish;
   end
 end
 initial begin
   for(i=0;i<32768;i=i+1)begin memory.frontend.U2.mem[i]=pattern(i);memory.frontend.U2.tag[i]=0;end
   #100;raw=0;#1000;raw=1;wait(memory.safe===1);
   // Fixture-only bank seed, off the physical backend edge, before monitoring.
   @(negedge backend);#0.01;memory.peripheral.U1.q[1:0]=2'b11;
   repeat(2)@(negedge backend);
   while(h!=0 || v!=0)@(negedge master);
   monitoring=1;
   for(i=0;i<200;i=i+1)begin
     while(h!=i)@(negedge master);
     request=1;wait(ack);writes=writes+1;
     @(negedge master);request=0;wait(memory.armed);
   end
   forever begin
     @(negedge master);if(memory.armed)request=1;
     wait(ack);writes=writes+1;
     repeat(writes%47)@(negedge master);
     request=0;wait(memory.armed);
   end
 end
 initial begin #90000000;$fatal(1,"native frame watchdog");end
endmodule
