`timescale 1ns/1ps
// Native raster + native DAC digital pin projection; synthetic VRAM data.
// Qualified external master/reset forcepoints. No CPU/memory/source/POR model.
module tb_video_dac;
 parameter EARLY=0,POLICY=1,NEGATIVE=0;
 reg master=0,reset_n=0,phase_init_n=0,monitoring=0,expected_valid=0,epoch_done=0;
 wire backend,capture,slot,visible,hs,vs,ready,arm,dclock,blue0,blue1,dhs,dvs;
 wire [7:0] h,pixel;
 wire [9:0] v,red,green,blue;
 wire [7:0] data=(h*17+v*13)&255;
 wire observed_hs=NEGATIVE==1?hs:dhs;
 wire observed_vs=NEGATIVE==1?vs:dvs;
 integer cap_h,cap_v,samples=0,active=0,hs_count=0,vs_count=0,frames=0,epoch;
 integer er,eg,eb;
 reg [7:0] expected_pixel;
 reg expected_hs=1,expected_vs=1,last_hs=1,last_vs=1;
 reg [255:0] seen=0;
 dac_packet_video_netlist #(.TIMED(1),.EARLY_CAPTURE(EARLY),.RESOLVE_LATE(POLICY)) raster(
   master,reset_n,1'b1,phase_init_n,1'b1,data,backend,capture,slot,visible,hs,vs,ready,arm,h,v,pixel,
   dclock,blue0,blue1,dhs,dvs);
 net33_dac converter(dclock,pixel,NEGATIVE==2?blue1:blue0,NEGATIVE==2?blue0:blue1,red,green,blue);
 always #19.8609731877 master=~master;
 always @(posedge capture)if(monitoring)begin
   cap_h=h;cap_v=v;
   #60;
   if(samples && (observed_hs!==last_hs || observed_vs!==last_vs))
     $fatal(1,"sync changed before DAC capture");
   expected_pixel=(cap_h<160 && cap_v<480)?((cap_h*17+cap_v*13)&255):0;
   expected_hs=!(cap_h>=164 && cap_h<188);
   expected_vs=!(cap_v>=490 && cap_v<492);
   if(pixel!==expected_pixel || hs!==expected_hs || vs!==expected_vs)
     $fatal(1,"native raster reference mismatch h%0d v%0d",cap_h,cap_v);
   expected_valid=1;
 end
 always @(posedge dclock)if(monitoring && expected_valid)begin
   #35;
   er=(((expected_pixel>>5)&7)*1023+3)/7;
   eg=(((expected_pixel>>2)&7)*1023+3)/7;
   eb=((expected_pixel&3)*1023+1)/3;
   if(red!==er[9:0] || green!==eg[9:0] || blue!==eb[9:0])
     $fatal(1,"native RGB332 DAC mapping mismatch");
   if(observed_hs!==expected_hs || observed_vs!==expected_vs)
     $fatal(1,"native DAC sync mismatch");
   last_hs=expected_hs;last_vs=expected_vs;seen[expected_pixel]=1;
   samples=samples+1;if(cap_h<160 && cap_v<480)active=active+1;
   if(!expected_hs)hs_count=hs_count+1;if(!expected_vs)vs_count=vs_count+1;
   if(cap_h==199 && cap_v==524)begin
     frames=frames+1;monitoring=0;expected_valid=0;epoch_done=1;
   end
 end
 initial begin
   for(epoch=0;epoch<2;epoch=epoch+1)begin
     reset_n=0;phase_init_n=0;
     #50000;
     if(dhs!==1 || dvs!==1 || pixel!==0)$fatal(1,"native reset blank/sync mismatch");
     phase_init_n=1;reset_n=1;
     wait(ready===1);
     while(h!=0 || v!=0)@(negedge master);
     epoch_done=0;last_hs=1;last_vs=1;monitoring=1;
     wait(epoch_done);
     @(negedge master);#1;
   end
   if(samples!=210000 || active!=153600 || hs_count!=25200 || vs_count!=800 || seen!=={256{1'b1}})
     $fatal(1,"native DAC coverage mismatch frames%0d samples%0d colors%h",frames,samples,seen);
   $display("RESULT native_raster_dac=1 reset_epochs=2 samples=%0d visible=%0d hsync=%0d vsync=%0d colors=256 cpu=0 analog=0 early=%0d policy=%0d failures=0",samples,active,hs_count,vs_count,EARLY,POLICY);
   $finish;
 end
 initial begin #150000000;$fatal(1,"native DAC raster watchdog");end
endmodule
