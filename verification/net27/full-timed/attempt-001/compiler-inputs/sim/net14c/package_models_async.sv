// GENERATED bounded external reset model; strict predecessor preserved.
`timescale 1ns/1ps
// Selected 4.5..5.5 V, -40..85 C timing scenarios at the documented CL.
// Functional HDL with aperture monitors, not vendor transistor/IBIS models.
module net14b_ahc74 #(parameter TIMED=0,EARLY=0,RESET_BOUNDARY=0,FIRST_STAGE=0,RESOLVE_LATE=1)(
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
       if(FIRST_STAGE && RESOLVE_LATE)q<=#CQ 0;else q<=#CQ d;
     end else q<=#CQ d;
   end
 end
endmodule

module net14b_lv161 #(parameter TIMED=0)(input wire clk,clr_n,load_n,enp,ent,
 input wire [3:0] d,output reg [3:0] q,output wire rco,input wire checks);
 localparam realtime CQ=TIMED?11.5:0;
 realtime changed=-10000,edge_at=-10000,last_clk=-10000,released=-10000;
 assign #(TIMED?14:0) rco=ent && (&q);
 always @(d or load_n or enp or ent)begin
   if(TIMED && checks && clr_n && $realtime-edge_at<1)$fatal(1,"LV161 hold violation %m");
   changed=$realtime;
 end
 always @(clk)begin
   if(TIMED && checks && clr_n && $realtime-last_clk<5)$fatal(1,"LV161 pulse violation %m");
   last_clk=$realtime;
 end
 always @(posedge clr_n)released=$realtime;
 always @(posedge clk or negedge clr_n)begin
   if(!clr_n)q<=#(TIMED?12.5:0) 0;
   else begin
     if(TIMED && checks && $realtime-released<1.5)$fatal(1,"LV161 reset recovery violation %m");
     if(TIMED && checks && $realtime-changed<6)$fatal(1,"LV161 setup violation %m");
     edge_at=$realtime;
     if(!load_n)q<=#CQ d;
     else if(enp && ent)q<=#CQ q+1;
   end
 end
endmodule

module net14b_ahc574 #(parameter TIMED=0)(input wire clk,oe_n,input wire [7:0] d,
 output wire [7:0] q,input wire checks);
 reg [7:0] state;
 realtime changed=-10000,edge_at=-10000,last_clk=-10000;
 assign #(TIMED?12:0) q=oe_n?8'bz:state;
 always @(d)begin
   if(TIMED && checks && $realtime-edge_at<1.5)$fatal(1,"AHC574 hold violation %m");
   changed=$realtime;
 end
 always @(clk)begin
   if(TIMED && checks && $realtime-last_clk<5)$fatal(1,"AHC574 pulse violation %m");
   last_clk=$realtime;
 end
 always @(posedge clk)begin
   if(TIMED && checks && $realtime-changed<3)$fatal(1,"AHC574 setup violation %m");
   edge_at=$realtime;state<=d;
 end
endmodule
