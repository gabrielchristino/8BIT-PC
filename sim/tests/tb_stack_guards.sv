`timescale 1ns/1ps
// Exhaustive SP bounds at the first stack microinstruction; ROM words are real.
module tb_stack_guards;
 reg clk=0,reset_n=0,boot=0;
 wire req,wr,z,c,halted,retired;wire [15:0] address,pc,sp,x;
 wire [7:0] data,a,b;wire [1:0] fault;wire [12:0] ca;wire [31:0] cw;
 isa1_cpu dut(clk,reset_n,1'b1,1'b1,boot,req,wr,address,data,1'b0,8'b0,
              pc,sp,x,a,b,z,c,halted,retired,fault,ca,cw);
 integer mode,which,s,lower,bytes_needed,n=0,rejections=0;
 reg pop,allowed;reg [7:0] opcode;
 initial begin
   // Establish reset with a real clock edge before the first seeded fixture.
   #1;clk=1;#1;clk=0;
   for(mode=0;mode<2;mode=mode+1)for(which=0;which<4;which=which+1)begin
     case(which)0:opcode=8'h50;1:opcode=8'h51;2:opcode=8'h52;3:opcode=8'h53;endcase
     pop=which==1 || which==3;bytes_needed=which<2?2:1;lower=mode?16384:0;
     for(s=0;s<65536;s=s+1)begin
       reset_n=0;clk=0;boot=mode;#1;reset_n=1;#1;
       dut.fetch_bank=0;dut.ir=opcode;dut.microstep=which==0?4:0;
       dut.sp=s;dut.stack_checked=0;
       allowed=pop?(s>=lower && s+bytes_needed<=32768):(s-bytes_needed>=lower && s<=32768);
       #1;clk=1;#1;
       if(sp!==s[15:0])$fatal(1,"preflight changed SP");
       if(req!==allowed || halted!==!allowed ||
          fault!==(allowed?2'b00:(pop?2'b10:2'b01)))
         $fatal(1,"stack guard mismatch opcode=%h SP=%h boot=%0d allowed=%0d req=%b halt=%b fault=%b state=%h addr=%h word=%h",
           opcode,s,mode,allowed,req,halted,fault,dut.state,ca,cw);
       if(!allowed)rejections=rejections+1;
       n=n+1;
     end
   end
   $display("RESULT stack_bound_cases=%0d rejected_cases=%0d failures=0",n,rejections);$finish;
 end
endmodule
