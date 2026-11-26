`timescale 1ns/1ps
// TI SCLS425H: 4.5..5.5V, -40..85C, <=50pF. Selected bounds,
// not a vendor transistor model or full min/max/skew/PVT qualification.
module net19_ahc174 #(parameter TIMED=0,EARLY=0)(
 input wire clk,clr_n,input wire [5:0] d,output reg [5:0] q);
 localparam realtime CQ=TIMED?(EARLY?1:10.5):0,ASYNC_T=TIMED?11:0;
 realtime data_changed=-10000,sampled=-10000,clear_release=-10000;
 realtime clear_assert=-10000,last_clock=-10000,min_setup=1e30;
 reg saw_clear=0,saw_clock=0;
 always @(posedge clk or negedge clr_n)
   if(!clr_n)q<=#ASYNC_T 0;else q<=#CQ d;
 always @(d)begin
   if(TIMED && saw_clear && clr_n && $realtime-sampled<0.5)
     $fatal(1,"AHC174 hold violation %m");
   data_changed=$realtime;
 end
 always @(negedge clr_n)begin clear_assert=$realtime;saw_clear=1;end
 always @(posedge clr_n)begin
   if(TIMED && saw_clear && $realtime-clear_assert<5)
     $fatal(1,"AHC174 clear pulse violation %m");
   clear_release=$realtime;
 end
 always @(clk)begin
   if(TIMED && saw_clear && saw_clock && clr_n && $realtime-last_clock<5)
     $fatal(1,"AHC174 clock pulse violation %m");
   last_clock=$realtime;saw_clock=1;
 end
 always @(posedge clk)if(saw_clear && clr_n)begin
   if($realtime-data_changed<min_setup)min_setup=$realtime-data_changed;
   if(TIMED && $realtime-data_changed<4.5)
     $fatal(1,"AHC174 setup violation %m");
   if(TIMED && $realtime-clear_release<2.5)
     $fatal(1,"AHC174 recovery violation %m");
   sampled=$realtime;
 end
endmodule
