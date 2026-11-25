`timescale 1ns/1ps
module tb_alu_bank;
 parameter integer TIMED=0;
 reg [7:0] a=0,b=0;reg [3:0] op=0;reg carry_in=0;
 wire [7:0] result;wire carry_out,zero;
 alu_bank_netlist #(.TIMED(TIMED)) dut(a,b,op,carry_in,result,carry_out,zero);
 integer operation,aa,bb,oldc,n=0;reg [7:0] expected;reg expected_c;
 initial begin
   for(operation=0;operation<16;operation=operation+1)
   for(aa=0;aa<256;aa=aa+1)for(bb=0;bb<256;bb=bb+1)for(oldc=0;oldc<2;oldc=oldc+1)begin
     a=aa;b=bb;op=operation;carry_in=oldc;expected=0;expected_c=oldc;
     case(operation)
       1:begin expected=aa+bb;expected_c=aa+bb>255;end
       2,8:begin expected=aa-bb;expected_c=aa>=bb;end
       3:expected=aa&bb;4:expected=aa|bb;5:expected=aa^bb;
       6:begin expected=aa<<1;expected_c=aa>=128;end
       7:begin expected=aa>>1;expected_c=aa%2;end
     endcase
     if(TIMED)#1000;else #1;
     if(result!==expected || carry_out!==expected_c || zero!==(expected==0))
       $fatal(1,"ALU mismatch op=%0d A=%0d B=%0d oldC=%0d got=%02x/%b/%b expected=%02x/%b",operation,aa,bb,oldc,result,carry_out,zero,expected,expected_c);
     n=n+1;
   end
   $display("RESULT timed=%0d alu_cases=%0d failures=0",TIMED,n);$finish;
 end
endmodule
