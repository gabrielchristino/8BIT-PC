`timescale 1ns/1ps
module tb_video_contract;
 parameter integer CAPTURE_PHASE=3;
 parameter integer INJECT_HOLD=0;
 parameter realtime COUNTER_Q=11.5;
 localparam realtime MASTER_HALF=1000000000.0/25175000.0/2;
 reg master=0,reset_n=0,request=0;
 always #MASTER_HALF master=~master;
 wire backend,slot;wire [7:0] h,pixel,pixel_h;wire [9:0] v,pixel_v;
 wire [14:0] video_address;wire valid,visible,hsync_n,vsync_n;
 wire ack,accept,armed,held_write,bus_active,owner,drive,oe_n,we_n,io_commit,read_capture;
 wire [15:0] held_address;wire [7:0] held_data,read_data,read_bus,video_data,phase;
 wire [3:0] select,cs_n;wire [5:0] io_select;wire [14:0] ra,va,ea;
 video_contract #(.COUNTER_Q(COUNTER_Q),.CAPTURE_PHASE(CAPTURE_PHASE)) raster(
   master,reset_n,backend,h,v,video_address,slot,video_data,
   valid,pixel,visible,hsync_n,vsync_n,pixel_h,pixel_v);
 memory_decode_netlist #(.TIMED(1)) decode(held_address,1'b0,1'b0,2'b11,1'b1,reset_n,select,io_select,ra,va,ea);
 memory_access_netlist #(.TIMED(1)) controller(.clk(backend),.reset_n(reset_n),.power_good(1'b1),
   .request(request),.write_request(1'b1),.vram_slot(slot),.address(16'h9ffe),.write_data(8'h39),
   .read_bus(read_bus),.select(select),.ack(ack),.accept(accept),.armed(armed),.held_write(held_write),
   .bus_active(bus_active),.vram_owner(owner),.data_drive(drive),.oe_n(oe_n),.we_n(we_n),.io_commit(io_commit),
   .read_capture(read_capture),.held_address(held_address),.held_data(held_data),.read_data(read_data),.cs_n(cs_n),.phase(phase));
 memory_bus_netlist #(.TIMED(1),.EARLY_ON(1)) frontend(.reset_n(reset_n),.power_good(1'b1),
   .vram_owner(owner),.data_drive(drive),.oe_n(oe_n),.we_n(we_n),.ram_address(ra),.vram_address(va),.rom_address(ea),
   .video_address(video_address),.write_data(held_data),.io_data(8'hff),.cs_n(cs_n),.select(select),
   .read_data(read_bus),.video_data(video_data));
 integer samples=0,active=0,hs=0,vs=0,writes=0,limit=0;
 integer ex_h=0,ex_v=0,frames=0,i;reg [31:0] starts=0;
 realtime data_changed=-10000,captured=-10000;
 function [7:0] pattern(input integer a);pattern=(a*17+(a>>8)+93)&255;endfunction
 always @(video_data)begin
   if(reset_n && captured>=0 && $realtime-captured<5)
     $fatal(1,"pixel hold violation");
   data_changed=$realtime;
 end
 always @(posedge backend)if(reset_n && phase[2] && slot && select[1])starts[h-161]=1;
 // Calibrate the aperture monitor by perturbing its observed input 1 ns
 // after capture. This is an injected bench fault, not a pad/clock model.
 always @(posedge valid)if(INJECT_HOLD && visible)begin
   #1;force video_data=8'hxx;#1;release video_data;
 end
 always @(posedge valid)begin
   // Check the data aperture at capture, not after Q propagation.
   if(visible && $realtime-data_changed<25)$fatal(1,"pixel setup violation");
   captured=visible?$realtime:-10000;
   if(pixel_h!==ex_h || pixel_v!==ex_v)$fatal(1,"raster sequence mismatch");
   if(visible!==(ex_h<160 && ex_v<480))$fatal(1,"visible mismatch");
   if(hsync_n!==!(ex_h>=164 && ex_h<188) || vsync_n!==!(ex_v>=490 && ex_v<492))$fatal(1,"sync mismatch");
   if(visible)begin
     if(owner)$fatal(1,"CPU owns visible VRAM");
     if(pixel!==pattern((ex_v/4)*256+ex_h))$fatal(1,"pixel data/address mismatch");
     active=active+1;
   end else if(pixel!==0)$fatal(1,"blanking is not black");
   if(!hsync_n)hs=hs+1;if(!vsync_n)vs=vs+1;
   samples=samples+1;
   if(ex_h==199)begin ex_h=0;if(ex_v==524)begin ex_v=0;frames=frames+1;end else ex_v=ex_v+1;end else ex_h=ex_h+1;
   if(frames==2)begin
     if(active!=153600 || hs!=25200 || vs!=800 || writes<100 || starts!==32'hffffffff)
       $fatal(1,"coverage incomplete active=%0d hs=%0d vs=%0d writes=%0d starts=%h",active,hs,vs,writes,starts);
     if(frontend.U2.aborted_writes!=0)$fatal(1,"unexpected write abort");
     $display("RESULT frames=2 samples=%0d visible=%0d hsync=%0d vsync=%0d writes=%0d grant_starts=32 failures=0",samples,active,hs,vs,writes);
     $finish;
   end
 end
 initial begin
   // Explicit video fixture, not SRAM power-up contents. No CPU boot is run.
   for(i=0;i<32768;i=i+1)begin frontend.U2.mem[i]=pattern(i);frontend.U2.tag[i]=0;end
   frontend.U2.generation=0;frontend.U2.fixture_seeded=0;
   repeat(12)@(negedge master);reset_n=1;
   wait(armed);
   // Sweep the request arrival position through an entire line. Saturating
   // traffic alone can lock into a subset of grant starts.
   for(i=0;i<200;i=i+1)begin
     while(h!=i)@(negedge master);
     request=1;wait(ack);writes=writes+1;
     @(negedge master);request=0;wait(armed);
   end
   forever begin
     @(negedge master);if(armed)request=1;
     wait(ack);writes=writes+1;
     // Vary the next acceptance phase to cover the entire grant window.
     repeat(writes%47)@(negedge master);
     request=0;wait(armed);
   end
 end
 initial begin #40000000;$fatal(1,"frame watchdog timeout");end
endmodule
