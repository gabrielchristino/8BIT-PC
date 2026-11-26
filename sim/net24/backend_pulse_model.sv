// GENERATED selected pulse investigation; original predicates/guards retained.
`timescale 1ns/1ps
module net24_backend_ff #(parameter TIMED=0,EARLY=0,RESET_BOUNDARY=0,FIRST_STAGE=0,RESOLVE_LATE=1,parameter realtime RISE_T=10.5,FALL_T=10.5)(
 input wire clk,clr_n,pre_n,d,output reg q,output wire qb,input wire checks);
 integer recovery_events=0;
 localparam realtime CQ=TIMED?(EARLY?1:10.5):0;
 localparam realtime ASYNC_T=TIMED?11:0;
 realtime changed=-10000,edge_at=-10000,last_clk=-10000,released=-10000;
 assign qb=~q;
 always @(d)begin
   if(TIMED && checks && clr_n && pre_n && $realtime-edge_at<0.5)$fatal(1,"AHC74 hold violation %m");
   changed=$realtime;
 end
 always @(clk)begin
   if(TIMED && checks && clr_n && pre_n && $realtime-last_clk<5)$fatal(1,"AHC74 pulse violation %m");
   last_clk=$realtime;
 end
 always @(posedge clr_n or posedge pre_n)released=$realtime;
 always @(posedge clk or negedge clr_n or negedge pre_n)begin
   if(!clr_n && !pre_n)q<=#ASYNC_T 1'bx;
   else if(!clr_n)q<=#ASYNC_T 0;
   else if(!pre_n)q<=#ASYNC_T 1;
   else begin
     if(TIMED && checks && $realtime-released<3 && !RESET_BOUNDARY)
       $fatal(1,"AHC74 reset recovery violation %m");
     if(TIMED && checks && $realtime-changed<5)$fatal(1,"AHC74 setup violation %m");
     edge_at=$realtime;
     if(TIMED && checks && $realtime-released<3 && RESET_BOUNDARY)begin
       recovery_events=recovery_events+1;
       // Deliberate abstraction at the external asynchronous boundary only.
       // Never claim that real metastability is bounded by one cycle.
       if(FIRST_STAGE && RESOLVE_LATE)q<=#CQ 0;else q<=#(TIMED?(d?RISE_T:FALL_T):0) d;
     end else q<=#(TIMED?(d?RISE_T:FALL_T):0) d;
   end
 end
endmodule
