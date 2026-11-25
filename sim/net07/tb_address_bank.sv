`timescale 1ns/1ps
module tb_address_bank;
 parameter integer TIMED=0;
 localparam DELAY=TIMED?1000:1;
 reg clk=0,reset_n=1,power_good=1,exec_enable=0,z=0;
 reg [2:0] addr_sel=0;reg [7:0] pc_n=8'hfe;
 reg [15:0] ea=0,x=0,sp=0,stack_sum=0;
 wire [15:0] pc,address;
 address_bank_netlist #(.TIMED(TIMED)) dut(clk,reset_n,power_good,exec_enable,addr_sel,pc_n,z,ea,x,sp,stack_sum,pc,address);
 integer p,op,flag,en,s,n=0,m=0;reg [15:0] expected,expected_address;
 task seed;
  input [15:0] value;
  begin dut.U1.q=value[7:0];dut.U2.q=value[15:8];end
 endtask
 initial begin
  #DELAY;reset_n=0;#DELAY;
  if(pc!==0)$fatal(1,"PC reset failed");
  reset_n=1;#DELAY;
  for(p=0;p<65536;p=p+1)for(op=0;op<8;op=op+1)for(flag=0;flag<2;flag=flag+1)for(en=0;en<2;en=en+1)begin
   clk=0;seed(p);ea=p^16'ha55a;pc_n=~(8'b1<<op);z=flag;exec_enable=en;expected=p;
   if(en)case(op)1:expected=p+1;2:expected=ea;3:if(flag)expected=ea;4:if(!flag)expected=ea;endcase
   #DELAY;clk=1;#DELAY;
   if(pc!==expected)$fatal(1,"PC mismatch p=%04x op=%0d z=%0d en=%0d actual=%04x expected=%04x",p,op,flag,en,pc,expected);
   n=n+1;
  end
  exec_enable=0;clk=0;
  for(p=0;p<65536;p=p+1)for(s=0;s<8;s=s+1)begin
   seed(p);ea=p^16'h96a5;x={8'(p),8'(p>>8)};sp=p+16'h1357;stack_sum=p-1;addr_sel=s;
   case(s)1:expected_address=p;2:expected_address=ea;3:expected_address=x;4:expected_address=sp;5:expected_address=stack_sum;default:expected_address=0;endcase
   #DELAY;
   if(address!==expected_address)$fatal(1,"Address mux mismatch p=%04x select=%0d got=%04x expected=%04x",p,s,address,expected_address);
   m=m+1;
  end
  // Both reset inputs clear independently, regardless of requested increment.
  exec_enable=1;pc_n=8'hfd;reset_n=0;#DELAY;clk=1;#DELAY;
  if(pc!==0)$fatal(1,"PC changed during reset");
  clk=0;power_good=0;reset_n=1;#DELAY;clk=1;#DELAY;
  if(pc!==0)$fatal(1,"PC changed with unsafe power");
  $display("RESULT timed=%0d pc_cases=%0d address_cases=%0d failures=0",TIMED,n,m);$finish;
 end
endmodule
