`timescale 1ns/1ps
module tb_rtl_alu;
 reg clk=0,reset_n=0;
 wire req,wr,z,c,halted,retired;wire [15:0] address,pc,sp,x;
 wire [7:0] data,a,b;wire [1:0] fault;wire [12:0] ca;wire [31:0] cw;
 isa1_cpu dut(clk,reset_n,1'b1,1'b0,1'b0,req,wr,address,data,1'b0,8'b0,
              pc,sp,x,a,b,z,c,halted,retired,fault,ca,cw);
 integer op,aa,bb,oldc,n=0;reg [7:0] expected;reg expected_c;
 initial begin
   #1;clk=1;#1;clk=0;reset_n=1;
   for(op=1;op<=8;op=op+1)begin
     dut.rom[4096]=op<<18;
     for(aa=0;aa<256;aa=aa+1)for(bb=0;bb<256;bb=bb+1)for(oldc=0;oldc<2;oldc=oldc+1)begin
       dut.a=aa;dut.b=bb;dut.c=oldc;expected_c=oldc;
       case(op)
         1:begin expected=aa+bb;expected_c=aa+bb>255;end
         2,8:begin expected=aa-bb;expected_c=aa>=bb;end
         3:expected=aa&bb;4:expected=aa|bb;5:expected=aa^bb;
         6:begin expected=aa<<1;expected_c=aa>=128;end
         7:begin expected=aa>>1;expected_c=aa%2;end
       endcase
       #1;
       if(dut.result!==expected || dut.carry!==expected_c)
         $fatal(1,"ALU mismatch op=%0d A=%0d B=%0d oldC=%0d",op,aa,bb,oldc);
       n=n+1;
     end
   end
   $display("RESULT alu_cases=%0d failures=0",n);$finish;
 end
endmodule
