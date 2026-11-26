`timescale 1ns/1ps
module tb_warm_packages;
 parameter CASE=0,BOUNDARY=0,POLICY=0;
 reg clk=0,clr=1,a=0;wire [7:0] q;
 net25_warm164 #(.TIMED(1),.BOUNDARY(BOUNDARY),.RESOLVE_LATE(POLICY)) dut(clk,clr,a,1'b1,q,1'b1);
 initial begin
   #1;clr=0;
   if(CASE==5)begin #3;clr=1;#30;$fatal(1,"missed clear negative");end
   else if(CASE==4)begin #10;clr=1;#20;clk=1;#2;clk=0;#30;$fatal(1,"missed pulse negative");end
   else if(CASE==6)begin #10;clr=1;#20;clk=1;#5;clk=0;#5;clk=1;#30;$fatal(1,"missed frequency negative");end
   else if(CASE==2)begin #20;a=1;#9;clr=1;#1;clk=1;#13;
     if(q[0] !== (POLICY?1'b0:1'b1))$fatal(1,"recovery binary policy incorrect");
     if(!BOUNDARY || dut.recovery_events!=1)$fatal(1,"missed recovery negative");
   end
   else if(CASE==1)begin #10;clr=1;#19;a=1;#1;clk=1;#13;
     if(q[0] !== (POLICY?1'b0:1'b1))$fatal(1,"setup binary policy incorrect");
     if(!BOUNDARY || dut.setup_events!=1)$fatal(1,"missed setup negative");
   end
   else if(CASE==3)begin #10;clr=1;#20;clk=1;#0.2;a=1;#13;
     if(!BOUNDARY || dut.hold_events!=1)$fatal(1,"missed hold negative");
   end
   else begin
     #10;clr=1;a=1;
     repeat(3)begin #20;clk=1;#13;if(q[3]!==0)$fatal(1,"warm output asserted before fourth edge");#7;clk=0;end
     #20;clk=1;#13;if(q[3]!==1)$fatal(1,"warm output missing on fourth edge");
   end
   $display("RESULT case=%0d boundary=%0d policy=%0d setup=%0d hold=%0d recovery=%0d failures=0",CASE,BOUNDARY,POLICY,dut.setup_events,dut.hold_events,dut.recovery_events);$finish;
 end
 initial begin #1000;$fatal(1,"warm calibration watchdog");end
endmodule
