`timescale 1ns/1ps
module tb_timing_negative;
 parameter integer CASE=0;
 reg clk=0,clr_n=0,en_n=1;reg [7:0] data=0;wire [5:0] q;
 hc174_model #(.TIMED(1)) storage(clk,clr_n,data[5:0],q);
 hc377_timing latch_check(clk,en_n,data,1'b1);
 initial begin
   #100;clk=1;#100;clk=0;clr_n=1;#6000;
   case(CASE)
     0:begin #100;data=55;#10;clk=1;end
     1:begin en_n=0;#100;clk=1;#2;data=255;end
     2:begin #100;en_n=0;#10;clk=1;end
     3:begin en_n=0;#100;clk=1;#2;en_n=1;end
   endcase
   #100;$fatal(1,"Expected timing rejection absent");
 end
endmodule
