`timescale 1ns/1ps
module tb_hc273_negative;
 parameter integer CASE=0;
 reg clk=0,clr_n=0;reg [7:0] d=0;wire [7:0] q;
 hc273_functional #(.CHECKS(1)) dut(clk,clr_n,d,q);
 initial begin
   #10;clk=1;#50;clk=0;#100;clr_n=1;#1000;
   case(CASE)
     0:begin #100;d=55;#10;clk=1;end
     1:begin #100;clr_n=0;#100;clr_n=1;#10;clk=1;end
     2:begin #100;clr_n=0;#10;clr_n=1;end
     3:begin #100;clk=1;#10;clk=0;end
   endcase
   #100;$fatal(1,"Expected timing rejection absent");
 end
endmodule
