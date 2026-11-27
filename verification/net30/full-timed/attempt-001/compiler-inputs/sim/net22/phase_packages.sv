`timescale 1ns/1ps
// TI SCAS970: 5V+/-0.5, -40..85C, CL50pF. Selected bounds, not vendor silicon.
module net22_ahc164 #(parameter TIMED=0,EARLY_CAPTURE=0,EARLY_ALL=0)(
 input wire clk,clr_n,a,b,output reg [7:0] q,input wire checks);
 reg [7:0] state;
 localparam realtime CQ=TIMED?(EARLY_ALL?1:12.5):0,CLR_T=TIMED?11:0;
 realtime changed=-10000,edge_at=-10000,last_clk=-10000,released=-10000;
 realtime last_rise=-10000,last_clear=-10000;
 integer i;
 always @(a or b)begin
   if(TIMED && checks && clr_n && $realtime-edge_at<0.5)$fatal(1,"AHC164 data hold violation %m");
   changed=$realtime;
 end
 always @(clk)begin
   if(TIMED && checks && clr_n && $realtime-last_clk<5)$fatal(1,"AHC164 clock pulse violation %m");
   last_clk=$realtime;
 end
 always @(negedge clr_n)last_clear=$realtime;
 always @(posedge clr_n)begin
   if(TIMED && checks && $realtime-last_clear<5)$fatal(1,"AHC164 clear pulse violation %m");
   released=$realtime;
 end
 always @(posedge clk or negedge clr_n)begin
   if(!clr_n)begin state<=0;q<=#CLR_T 0;end
   else begin
     if(TIMED && checks && $realtime-released<2.5)$fatal(1,"AHC164 reset recovery violation %m");
     if(TIMED && checks && $realtime-changed<4.5)$fatal(1,"AHC164 data setup violation %m");
     if(TIMED && checks && $realtime-last_rise<10.526315)$fatal(1,"AHC164 clock outside95MHz qualification envelope %m");
     last_rise=$realtime;
     edge_at=$realtime;
     // The vendor shift register transfers between internal FFs. Output-load
     // delay belongs to the pins, not a second external shift-stage chain.
     state<={state[6:0],a&b};
     for(i=0;i<8;i=i+1)
       q[i]<=#((TIMED && EARLY_CAPTURE && i==3)?1:CQ) (i==0 ? (a&b) : state[i-1]);
   end
 end
endmodule
