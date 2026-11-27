`timescale 1ns/1ps
// TI SCAS970 selected digital bounds. Native strict model remains net22_ahc164.
// BOUNDARY=1 is a deliberately bounded binary projection at ASYNC SAFE / CLR
// only, NOT metastability simulation, a duration guarantee or MTBF approval.
module net25_warm164 #(parameter TIMED=0,BOUNDARY=0,RESOLVE_LATE=1)(
 input wire clk,clr_n,a,b,output reg [7:0] q,input wire checks);
 reg [7:0] state;
 reg previous_data=0,last_data=0,sampled;
 integer setup_events=0,hold_events=0,recovery_events=0,i;
 localparam realtime CQ=TIMED?12.5:0,CLR_T=TIMED?11:0;
 realtime changed=-10000,edge_at=-10000,last_clk=-10000,released=-10000;
 realtime last_rise=-10000,last_clear=-10000;
 always @(a or b)begin
   if(TIMED && checks && clr_n && $realtime-edge_at<0.5)begin
     if(!BOUNDARY)$fatal(1,"AHC164 data hold violation %m");
     hold_events=hold_events+1;
   end
   changed=$realtime;
   // Previous stable binary input at the aperture; sampled below by policy.
   previous_data<=last_data;
   last_data<=a&b;
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
     sampled=a&b;
     if(TIMED && checks && $realtime-released<2.5)begin
       if(!BOUNDARY)$fatal(1,"AHC164 reset recovery violation %m");
       recovery_events=recovery_events+1;
       if(RESOLVE_LATE)sampled=0;
     end
     if(TIMED && checks && $realtime-changed<4.5)begin
       if(!BOUNDARY)$fatal(1,"AHC164 data setup violation %m");
       setup_events=setup_events+1;
       if(RESOLVE_LATE)sampled=previous_data;
     end
     if(TIMED && checks && $realtime-last_rise<10.526315)$fatal(1,"AHC164 clock outside95MHz qualification envelope %m");
     last_rise=$realtime;edge_at=$realtime;
     state<={state[6:0],sampled};
     for(i=0;i<8;i=i+1)q[i]<=#CQ (i==0?sampled:state[i-1]);
   end
 end
endmodule
