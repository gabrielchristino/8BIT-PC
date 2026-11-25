`timescale 1ns/1ps
module tb_register_timing_negative;
 parameter integer CASE=0;
 reg clk=0,clear_n=0;reg [7:0] data=0;
 wire [7:0] q;wire flag;
 generate if(CASE<4)begin
  hc273_functional #(.CHECKS(1)) reg8(clk,clear_n,data,q);
 end else begin
  hc74_model flag_ff(clk,clear_n,1'b1,data[0],flag, );
  dff_timing #(.WIDTH(1),.RECOVERY(6),.CLEAR_PULSE(25)) check_flag(clk,clear_n,data[0]);
 end endgenerate
 initial begin
  #6000;clear_n=1;#100;
  case(CASE)
   0,4:begin data=1;#1;clk=1;end
   1,5:begin clear_n=0;#100;clear_n=1;#1;clk=1;end
   2,6:begin clk=1;#10;clk=0;end
   3,7:begin clear_n=0;#10;clear_n=1;end
  endcase
  #100;$display("ERROR expected timing rejection absent");$finish;
 end
endmodule
