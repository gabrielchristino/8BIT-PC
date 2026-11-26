`timescale 1ns/1ps
module tb_ahc164_limits;
 parameter MODE=0;
 reg clk=0,clr_n=1,a=0,b=1;
 wire [7:0] q;
 net22_ahc164 #(.TIMED(1),.EARLY_ALL(MODE==7),.EARLY_CAPTURE(MODE==8)) dut(clk,clr_n,a,b,q,1'b1);
 initial begin
   #100;clr_n=0;
   if(MODE==5)begin #3;clr_n=1;#20;$fatal(1,"missing clear pulse rejection");end
   #5;if(MODE!=1 && MODE!=8)a=1;
   if(MODE==4)begin #14;clr_n=1;#1;clk=1;#20;$fatal(1,"missing recovery rejection");end
   #5;clr_n=1;
   if(MODE==8)begin dut.state=8'h04;dut.q=8'h04;end
   if(MODE==1)begin #9;a=1;#1;clk=1;#20;$fatal(1,"missing setup rejection");end
   #10;clk=1;
   if(MODE==2)begin #0.1;a=0;#20;$fatal(1,"missing hold rejection");end
   if(MODE==3)begin #2;clk=0;#20;$fatal(1,"missing clock pulse rejection");end
   if(MODE==6)begin #5;clk=0;#5;clk=1;#20;$fatal(1,"missing frequency envelope rejection");end
   if(MODE==7 || MODE==8)begin
     #0.9;if((MODE==7 ? q[0] : q[3])!==0)$fatal(1,"early Q changed before1ns");
     #0.2;if((MODE==7 ? q[0] : q[3])!==1)$fatal(1,"early Q did not change at1ns");
   end else begin
     #12.4;if(q[0]===1)$fatal(1,"Q changed before12.5ns");
     #0.2;if(q[0]!==1)$fatal(1,"Q did not change at12.5ns");
   end
   #10;clk=0;a=0;
   #10;clk=1;
   #13;
   if(MODE!=8 && q[1:0]!==2'b10)$fatal(1,"serial shift differs from prior internal state");
   $display("RESULT mode=%0d ahc164_shift_and_delay=1 failures=0",MODE);
   $finish;
 end
endmodule
