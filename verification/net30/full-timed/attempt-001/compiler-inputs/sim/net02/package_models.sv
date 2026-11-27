`timescale 1ns/1ps
// Pin functions only. Not vendor timing/transistor models.
module hc273_functional #(parameter T_CQ=0,T_CLR=0,CHECKS=0)
 (input wire clk,clr_n,input wire [7:0] d,output reg [7:0] q);
 always @(posedge clk or negedge clr_n)if(!clr_n)q<=#T_CLR 0;else q<=#T_CQ d;
 generate if(CHECKS)begin:timing
   realtime data_changed=0,clear_rise=0,clear_fall=0,clock_changed=0;
   reg saw_clear=0,saw_clock=0;
   always @(d)data_changed=$realtime;
   always @(negedge clr_n)begin clear_fall=$realtime;saw_clear=1;end
   always @(posedge clr_n)begin
     if($realtime>1000 && saw_clear && $realtime-clear_fall<20)$fatal(1,"HC273 clear pulse violation");
     clear_rise=$realtime;
   end
   always @(clk)begin
     if($realtime>1000 && saw_clock && $realtime-clock_changed<20)$fatal(1,"HC273 clock pulse violation");
     clock_changed=$realtime;saw_clock=1;
   end
   always @(posedge clk)if(clr_n && $realtime>1000)begin
     if($realtime-data_changed<25)$fatal(1,"HC273 data setup violation");
     if($realtime-clear_rise<25)$fatal(1,"HC273 clear recovery violation");
   end
   // TI SN74HC273 table 6.10 specifies data hold=0 at 4.5 V.
 end endgenerate
endmodule
module hc283_functional #(parameter T_SUM=0,T_CARRY=0)
 (input wire [3:0] a,b,input wire cin,output wire [3:0] s,output wire cout);
 wire [4:0] result={1'b0,a}+{1'b0,b}+cin;
 assign #T_SUM s=result[3:0];assign #T_CARRY cout=result[4];
endmodule
