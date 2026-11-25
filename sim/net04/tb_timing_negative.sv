`timescale 1ns/1ps
module tb_timing_negative;
 parameter integer CASE=0;
 reg clk=0,clr_n=0,enp=0,en_n=1;reg [7:0] data=0;wire [3:0] q;wire rco;
 hc161_model #(.TIMED(1)) counter(clk,clr_n,1'b1,enp,1'b1,4'b0,q,rco);
 hct377_timing monitor_word(clk,en_n,data,1'b1);
 initial begin
   #100;clk=1;#100;clk=0;clr_n=1;#6000;
   case(CASE)
     0:begin #100;enp=1;#10;clk=1;end
     1:begin #100;clr_n=0;#100;clr_n=1;#10;clk=1;end
     2:begin en_n=0;#100;data=1;#10;clk=1;end
     3:begin #100;en_n=0;#10;clk=1;end
     4:begin en_n=0;#100;clk=1;#1;data=1;end
     5:begin en_n=0;#100;clk=1;#2;en_n=1;end
   endcase
   #100;$fatal(1,"Expected timing rejection absent");
 end
endmodule
