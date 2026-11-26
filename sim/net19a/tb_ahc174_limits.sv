`timescale 1ns/1ps
module tb_ahc174_limits;
 parameter MODE=0,EARLY=0;
 reg clk=0,clr_n=1;reg [5:0] d=0;wire [5:0] q;
 net19_ahc174 #(.TIMED(1),.EARLY(EARLY)) dut(clk,clr_n,d,q);
 initial begin
   #10;clr_n=0;
   if(MODE==4)begin #4.9;clr_n=1;end
   else if(MODE==3)begin
     #40;d=6'h2a;#17.6;clr_n=1;#2.4;clk=1;
   end else begin
     #20;
     if(q!==0)$fatal(1,"AHC174 async clear did not work with stopped clock");
     clr_n=1;#20;d=6'h2a;
     if(MODE==1)begin #15.6;d=6'h15;#4.4;clk=1;end
     else begin
       #20;clk=1;
       if(MODE==2)begin #0.4;d=6'h15;end
       else if(MODE==5)begin #4.9;clk=0;end
       else begin
         #0.9;if(q!==0)$fatal(1,"AHC174 changed before selected CQ");
         #(EARLY ? 0.2 : 9.7);
         if(q!==6'h2a)$fatal(1,"AHC174 selected CQ transfer missing");
         #20;clk=0;#20;clr_n=0;
         #10.9;if(q!==6'h2a)$fatal(1,"AHC174 changed before selected async clear");
         #0.2;if(q!==0)$fatal(1,"AHC174 selected async clear missing");
         $display("RESULT early=%0d async_clear_clock_stopped=1 selected_cq_checked=1 failures=0",EARLY);
         $finish;
       end
     end
   end
   #100;$fatal(1,"Invalid timing stimulus was not rejected");
 end
endmodule
