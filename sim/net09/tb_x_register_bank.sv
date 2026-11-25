`timescale 1ns/1ps
module tb_x_register_bank;
 parameter integer TIMED=0;
 localparam DELAY=TIMED?1000:1;
 reg clk=0,reset_n=1,power_good=1,exec_enable=0;
 reg [3:0] x_n=4'he;reg [15:0] ea=0;wire [15:0] x;
 x_register_bank_netlist #(.TIMED(TIMED)) dut(clk,reset_n,power_good,exec_enable,x_n,ea,x);
 integer q,op,en,n=0;reg [15:0] expected;
 initial begin
  #DELAY;reset_n=0;#DELAY;if(x!==0)$fatal(1,"X reset failed");reset_n=1;#DELAY;
  for(q=0;q<65536;q=q+1)for(op=0;op<4;op=op+1)for(en=0;en<2;en=en+1)begin
   clk=0;dut.U1.q=q[7:0];dut.U2.q=q[15:8];ea=q^16'ha596;x_n=~(4'b1<<op);exec_enable=en;expected=q;
   if(en)case(op)1:expected=ea;2:expected=q+1;3:expected=q-1;endcase
   #DELAY;clk=1;#DELAY;
   if(x!==expected)$fatal(1,"X mismatch q=%04x op=%0d en=%0d got=%04x expected=%04x",q,op,en,x,expected);
   n=n+1;
  end
  reset_n=0;#DELAY;clk=0;#DELAY;clk=1;#DELAY;if(x!==0)$fatal(1,"Unsafe X reset write");
  power_good=0;reset_n=1;#DELAY;clk=0;#DELAY;clk=1;#DELAY;if(x!==0)$fatal(1,"Unsafe X power write");
  $display("RESULT timed=%0d x_cases=%0d failures=0",TIMED,n);$finish;
 end
endmodule
