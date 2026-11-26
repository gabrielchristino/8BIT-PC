`timescale 1ns/1ps
// CQ6ns is an admitted illustrative value below the44ns maximum; datasheet gives no minimum. Not measured silicon.
module net24_hc74_probe #(parameter integer TIMED=0,parameter realtime CQ_NS=44)(input wire clk,clr_n,pre_n,d,output reg q,output wire qn);
 always @(posedge clk or negedge clr_n or negedge pre_n)
   if(!clr_n && !pre_n)q<=1'bx;
   else if(!clr_n)q<=#(TIMED?58:0) 0;
   else if(!pre_n)q<=#(TIMED?58:0) 1;
   else q<=#(TIMED?CQ_NS:0) d;
 assign qn=~q; // QN outputs unused in this design; no QN timing claim.
endmodule
