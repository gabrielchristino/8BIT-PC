`timescale 1ns/1ps
module tb_register_bank;
 parameter integer TIMED=0;
 localparam SETTLE=TIMED?1000:1;
 reg clk=0,reset_n=1,power_good=1,exec_enable=0;
 reg [2:0] src=0;reg [7:0] dst_n=8'hff;reg [3:0] flags_n=4'hf;
 reg [15:0] pc=0;reg [7:0] mdr=0,alu_result=0;reg alu_carry=0;
 wire [7:0] a,b,value;wire [15:0] ea;wire z,c;
 register_bank_netlist #(.TIMED(TIMED)) dut(clk,reset_n,power_good,exec_enable,src,dst_n,flags_n,pc,mdr,alu_result,alu_carry,a,b,value,ea,z,c);
 reg [7:0] ra=0,rb=0;reg [15:0] rea=0;reg rz=0,rc=0;
 reg [7:0] selected;integer s,v,d,f,cin,en,n=0,cuts=0;
 function [7:0] reference_value;
  input [2:0] select;
  begin case(select)
   1:reference_value=ra;2:reference_value=pc[15:8];3:reference_value=pc[7:0];
   4:reference_value=mdr;5:reference_value=alu_result;default:reference_value=0;
  endcase end
 endfunction
 task check_state;
  begin
   if(a!==ra || b!==rb || ea!==rea || z!==rz || c!==rc)
    $fatal(1,"Register mismatch n=%0d src=%0d dst=%0d flags=%0d en=%0d actual=%02x/%02x/%04x/%b/%b expected=%02x/%02x/%04x/%b/%b",n,s,d,f,en,a,b,ea,z,c,ra,rb,rea,rz,rc);
  end
 endtask
 task step;
  input integer source,destination,flag_mode,enabled,payload,carry_value;
  begin
   clk=0;src=source;dst_n=~(8'b1<<destination);flags_n=~(4'b1<<flag_mode);
   exec_enable=enabled;pc={8'(payload^8'ha5),8'(payload+1)};mdr=payload;alu_result=payload^8'h3c;alu_carry=carry_value;
   #SETTLE;selected=reference_value(src);
   if(value!==selected)$fatal(1,"Source mux mismatch src=%0d payload=%0d actual=%02x expected=%02x",source,payload,value,selected);
   check_state();
   if(reset_n && power_good && enabled)begin
    case(destination)1:ra=selected;2:rb=selected;3:rea[7:0]=selected;4:rea[15:8]=selected;endcase
    if(flag_mode!=0)rz=selected==0;
    if(flag_mode==2)rc=carry_value;
   end
   clk=1;#SETTLE;check_state();n=n+1;
  end
 endtask
 initial begin
  #SETTLE;reset_n=0;#SETTLE;check_state();reset_n=1;#SETTLE;
  step(5,1,2,1,8'h55,1);step(5,2,0,1,8'haa,0);
  for(s=0;s<8;s=s+1)for(v=0;v<256;v=v+1)for(d=0;d<8;d=d+1)
   for(f=0;f<4;f=f+1)for(cin=0;cin<2;cin=cin+1)for(en=0;en<2;en=en+1)
    step(s,d,f,en,v,cin);
  // Asynchronous clear during changing input, clock high/low, and unsafe power.
  for(cuts=0;cuts<4;cuts=cuts+1)begin
   step(5,1,2,1,8'h9a,1);step(5,3,0,1,8'hbc,0);
   clk=cuts%2;exec_enable=1;src=5;alu_result=8'hff;dst_n=8'hfd;
   if(cuts<2)reset_n=0;else power_good=0;
   ra=0;rb=0;rea=0;rz=0;rc=0;#SETTLE;check_state();
   step(5,1,2,1,8'hff,1);step(5,4,2,1,8'h42,1);
   exec_enable=0;reset_n=1;power_good=1;#SETTLE;check_state();
  end
  $display("RESULT timed=%0d register_cycles=%0d matrix_cases=262144 reset_cuts=4 failures=0",TIMED,n);$finish;
 end
endmodule
