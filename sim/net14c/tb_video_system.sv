`timescale 1ns/1ps
module tb_video_system;
 parameter integer TIMED=1,EARLY_CAPTURE=0;
 localparam realtime HALF=1000000000.0/25175000.0/2;
 reg master=0,running=0,reset_n=1,request=0;
 always #HALF if(running)master=~master;
 wire backend,capture,slot,visible,hsync_n,vsync_n,ready;
 wire [7:0] h,pixel;wire [9:0] v;wire [14:0] video_address={v[8:2],h};
 wire ack,accept,armed,held_write,bus_active,owner,drive,oe_n,we_n,io_commit,read_capture;
 wire [15:0] held_address;wire [7:0] held_data,read_data,read_bus,video_data,phase;
 wire [3:0] select,cs_n;wire [5:0] io_select;wire [14:0] ra,va,ea;
 video_system_netlist #(.TIMED(TIMED),.EARLY_CAPTURE(EARLY_CAPTURE)) raster(
   master,reset_n,1'b1,video_data,backend,capture,slot,visible,hsync_n,vsync_n,ready,h,v,pixel);
 memory_decode_netlist #(.TIMED(TIMED)) decode(held_address,1'b0,1'b0,2'b11,1'b1,reset_n,select,io_select,ra,va,ea);
 memory_access_netlist #(.TIMED(TIMED)) controller(.clk(backend),.reset_n(reset_n),.power_good(1'b1),
   .request(request),.write_request(1'b1),.vram_slot(slot),.address(16'h9ffe),.write_data(8'h39),
   .read_bus(read_bus),.select(select),.ack(ack),.accept(accept),.armed(armed),.held_write(held_write),
   .bus_active(bus_active),.vram_owner(owner),.data_drive(drive),.oe_n(oe_n),.we_n(we_n),.io_commit(io_commit),
   .read_capture(read_capture),.held_address(held_address),.held_data(held_data),.read_data(read_data),.cs_n(cs_n),.phase(phase));
 memory_bus_netlist #(.TIMED(TIMED),.EARLY_ON(1)) frontend(.reset_n(reset_n),.power_good(1'b1),
   .vram_owner(owner),.data_drive(drive),.oe_n(oe_n),.we_n(we_n),.ram_address(ra),.vram_address(va),.rom_address(ea),
   .video_address(video_address),.write_data(held_data),.io_data(8'hff),.cs_n(cs_n),.select(select),
   .read_data(read_bus),.video_data(video_data));
 integer samples=0,active=0,hs=0,vs=0,writes=0,frames=0,i,ex_h=0,ex_v=0;
 reg [31:0] starts=0;
 function [7:0] pattern(input integer a);pattern=(a*17+(a>>8)+93)&255;endfunction
 always @(posedge backend)if(reset_n && phase[2] && slot && select[1] && h>=161 && h<=192)starts[h-161]=1;
 always @(posedge capture)if(reset_n && running)begin
   if(h!==ex_h || v!==ex_v)$fatal(1,"raster coordinates mismatch h=%0d v=%0d expected=%0d,%0d",h,v,ex_h,ex_v);
   // Observe registered data after selected CLK->Q and output gates. Do not
   // model analog RGB/DAC settling as this digital delay.
   #60;
   if(!ready)$fatal(1,"capture never initialized");
   if(visible!==(ex_h<160 && ex_v<480))$fatal(1,"visible mismatch");
   if(hsync_n!==!(ex_h>=164 && ex_h<188) || vsync_n!==!(ex_v>=490 && ex_v<492))$fatal(1,"sync mismatch");
   if(visible)begin
     if(owner)$fatal(1,"visible VRAM owner");
     if(pixel!==pattern((ex_v/4)*256+ex_h))$fatal(1,"pixel mismatch h=%0d v=%0d got=%h expected=%h",ex_h,ex_v,pixel,pattern((ex_v/4)*256+ex_h));
     active=active+1;
   end else if(pixel!==0)$fatal(1,"blanking not black");
   samples=samples+1;if(!hsync_n)hs=hs+1;if(!vsync_n)vs=vs+1;
   if(ex_h==199)begin ex_h=0;if(ex_v==524)begin ex_v=0;frames=frames+1;end else ex_v=ex_v+1;end else ex_h=ex_h+1;
   if(frames==2)begin
     if(active!=153600 || hs!=25200 || vs!=800 || writes<100 || starts!==32'hffffffff)$fatal(1,"coverage incomplete writes=%0d starts=%h",writes,starts);
     if(frontend.U2.aborted_writes!=0)$fatal(1,"write abort");
     $display("RESULT frames=2 samples=%0d visible=%0d hsync=%0d vsync=%0d writes=%0d grant_starts=32 timed=%0d early_capture=%0d failures=0",samples,active,hs,vs,writes,TIMED,EARLY_CAPTURE);$finish;
   end
 end
 initial begin
   for(i=0;i<32768;i=i+1)begin frontend.U2.mem[i]=pattern(i);frontend.U2.tag[i]=0;end
   frontend.U2.generation=0;frontend.U2.fixture_seeded=0;
   // This first bench requires a stopped master during release. Reset with
   // a free-running clock must be tested separately before system acceptance.
   #100;reset_n=0;#1000;reset_n=1;#500;running=1;wait(armed);
   for(i=0;i<200;i=i+1)begin
     while(h!=i)@(negedge master);
     request=1;wait(ack);writes=writes+1;
     @(negedge master);request=0;wait(armed);
   end
   forever begin
     @(negedge master);if(armed)request=1;
     wait(ack);writes=writes+1;
     repeat(writes%47)@(negedge master);
     request=0;wait(armed);
   end
 end
 initial begin #40000000;$fatal(1,"watchdog");end
endmodule
