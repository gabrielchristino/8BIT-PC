`timescale 1ns/1ps
// Native XML-derived digital projection, no analog or NET30 integration.
module tb_dac_leaf;
 reg clk=0;
 reg [9:0] r=0,g=0,b=0;
 wire [9:0] red,green,blue;
 integer i;
 real period=1000000000.0/25175000.0;
 net32_dac_leaf dut(clk,r,g,b,red,green,blue);
 initial begin
   #20;
   for(i=0;i<1024;i=i+1)begin
     r=i;g=(i*73+11)&1023;b=1023-i;
     #(2*period);clk=1;#2;
     if(red!==r || green!==g || blue!==b)$fatal(1,"native DAC pin/code mismatch");
     #(period-2);clk=0;#(period);
   end
   $display("RESULT native_dac_only=1 samples=1024 distinct_codes_each_channel=1024 analog_model=0 failures=0");
   $finish;
 end
 initial begin #1000000;$fatal(1,"DAC leaf watchdog");end
endmodule
