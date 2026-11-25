`timescale 1ns/1ps
module tb_reset_resolution;
 parameter integer TIMED=1,RESOLVE_LATE=1;
 localparam realtime HALF=1000000000.0/25175000.0/2;
 reg master=0,reset_n=1,power_good=1;
 always #HALF master=~master;
 wire backend,capture,slot,visible,hs,vs,ready;wire [7:0] h,pixel;wire [9:0] v;
 video_system_netlist #(.TIMED(TIMED),.RESOLVE_LATE(RESOLVE_LATE),.EARLY_CAPTURE(1)) dut(master,reset_n,power_good,8'ha5,backend,capture,slot,visible,hs,vs,ready,h,v,pixel);
 integer cuts=0,pixels=0,expected=0,j,k;reg observe=0;
 always @(posedge capture)if(observe && reset_n && power_good)begin
   if(h!==expected || v!==0)$fatal(1,"reset raster sequence mismatch h=%0d v=%0d expected=%0d",h,v,expected);
   #60;
   if(!ready || !visible || pixel!==8'ha5 || !hs || !vs)$fatal(1,"reset output initialization mismatch");
   expected=expected+1;pixels=pixels+1;
 end
 initial begin
   // Include the recovery aperture at the two marked external reset FFs.
   // Bounded binary resolution here is an assumption, not analog validation.
   for(j=0;j<2;j=j+1)for(k=0;k<40;k=k+1)begin
     observe=0;@(negedge master);
     if(j==0)reset_n=0;else power_good=0;
     #1000;
     if(pixel!==0 || visible!==0 || hs!==1 || vs!==1 || ready!==0)$fatal(1,"unsafe output not blanked");
     @(negedge master);
     #k;
     expected=0;observe=1;
     if(j==0)reset_n=1;else power_good=1;
     wait(expected==32);observe=0;cuts=cuts+1;
   end
   $display("RESULT reset_cuts=%0d captured_pixels=%0d free_running_master=1 recovery_aperture_excluded=0 bounded_binary_resolution=1 failures=0",cuts,pixels);if(dut.U8_0.recovery_events==0 || dut.U8_1.recovery_events==0)$fatal(1,"recovery aperture was not exercised");
   $display("BOUNDARY_EVENTS resolution_late=%0d stage1=%0d stage2=%0d analog_metastability_approved=0",RESOLVE_LATE,dut.U8_0.recovery_events,dut.U8_1.recovery_events);$finish;
 end
 initial begin #2000000;$fatal(1,"reset watchdog");end
endmodule
