`timescale 1ns/1ps
module tb_stack_bank;
 parameter integer TIMED=0;
 localparam HALF=TIMED?500:1,SETTLE=TIMED?400:1;
 reg clk=0,reset_n=0,update=0,down=0;
 wire [15:0] sp,sum;
 stack_bank_netlist #(.TIMED(TIMED)) dut(clk,reset_n,update,down,sp,sum);
 integer value,direction,n=0,holds=0,resets=0;
 reg [15:0] expected;
 initial begin
   #(HALF);clk=1;#(HALF);clk=0;reset_n=1;
   for(direction=0;direction<2;direction=direction+1)begin
     down=direction;
     for(value=0;value<65536;value=value+1)begin
       // Fixture seeding is not a physical load port.
       dut.U1.q=value&255;dut.U2.q=(value>>8)^128;
       update=0;#(SETTLE);
       expected=direction?value-1:value+1;
       if(sp!==value[15:0] || sum!==expected)$fatal(1,"stack arithmetic mismatch SP=%h DOWN=%d SUM=%h",sp,direction,sum);
       clk=1;#(HALF);clk=0;
       if(sp!==value[15:0])$fatal(1,"stack changed without UPDATE");
       holds=holds+1;
       update=1;#(HALF);clk=1;#(HALF);clk=0;update=0;#(SETTLE);
       if(sp!==expected)$fatal(1,"stack update mismatch SP=%h expected=%h",sp,expected);
       n=n+1;
       if(value%256==0)begin
         reset_n=0;update=1;#(SETTLE);
         if(sp!==16'h8000)$fatal(1,"asynchronous stack reset mismatch");
         clk=1;#(HALF);clk=0;
         if(sp!==16'h8000)$fatal(1,"UPDATE bypassed clear");
         update=0;reset_n=1;#(SETTLE);resets=resets+1;
       end
     end
   end
   $display("RESULT timed=%0d arithmetic_updates=%0d hold_checks=%0d reset_checks=%0d failures=0",TIMED,n,holds,resets);$finish;
 end
endmodule
