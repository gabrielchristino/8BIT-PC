`timescale 1ns/1ps
module tb_execution_bank;
 parameter integer TIMED=0;
 localparam DELAY=TIMED?1000:1;
 reg clk=0,reset_n=1,power_good=1,run=1,ready=1,x_ready=1,x_done=0,use_x=0,boot=0,bus_ready=1,bus_done=0,dispatch=0,cw_end=0,cw_halt=0;
 reg [7:0] ir=0,addr_n=8'hff;reg [3:0] mem_n=4'he,x_n=4'he;reg [15:0] sp=16'h8000;
 wire ep,advance,start,x_request,x_count,checked,halted,retired;wire [1:0] fault,state;
 execution_bank_netlist #(.TIMED(TIMED)) dut(clk,reset_n,power_good,run,ready,x_ready,x_done,use_x,boot,bus_ready,bus_done,dispatch,cw_end,cw_halt,ir,addr_n,mem_n,x_n,sp,ep,advance,start,x_request,x_count,checked,halted,retired,fault,state);
 integer mode,which,s,seen,bytes_needed,lower,n=0,k;reg pop,allowed;
 task tick;begin clk=0;#DELAY;clk=1;#DELAY;end endtask
 task clear_fixture;
  begin clk=0;dut.U1.q=0;dut.U2.q=0;end
 endtask
 initial begin
  #DELAY;reset_n=0;#DELAY;reset_n=1;#DELAY;
  // Both first-byte preflight and the already-checked second byte.
  for(mode=0;mode<2;mode=mode+1)for(which=0;which<4;which=which+1)for(seen=0;seen<2;seen=seen+1)
   for(s=0;s<65536;s=s+1)begin
    clear_fixture();dut.U1.q[4]=seen;boot=mode;sp=s;ir=8'h50+which;
    pop=which==1 || which==3;addr_n=~(8'b1<<(pop?4:5));mem_n=4'hd;
    bytes_needed=which<2 && !seen?2:1;lower=mode?16384:0;
    allowed=pop?(s>=lower && s+bytes_needed<=32768):(s-bytes_needed>=lower && s<=32768);
    tick();
    if(start!==allowed || halted!==!allowed || retired!==!allowed || fault!==(allowed?2'b00:pop?2'b10:2'b01))
     $fatal(1,"Guard mismatch SP=%04x IR=%02x boot=%0d checked=%0d allowed=%b state=%b fault=%b",s,ir,mode,seen,allowed,state,fault);
    n=n+1;
   end
  mem_n=4'he;addr_n=8'hff;cw_halt=1;
  for(k=0;k<256;k=k+1)begin
   clear_fixture();ir=k;tick();
   if(!halted || !retired || fault!==(k==255?2'b00:2'b11) || advance!==0)$fatal(1,"HALT/invalid decode mismatch IR=%02x",ir);
  end
  clear_fixture();cw_halt=0;ir=8'h52;sp=16'h8000;boot=0;addr_n=8'hdf;mem_n=4'hd;tick();
  if(!start || state!=1)$fatal(1,"Response entry failed");
  for(k=0;k<5;k=k+1)begin sp=k;ir=k;tick();if(!start || state!=1 || halted || fault || retired)$fatal(1,"Held response changed");end
  bus_done=1;tick();if(start || state!=2)$fatal(1,"Drop entry failed");
  bus_done=0;bus_ready=0;repeat(3)begin tick();if(state!=2)$fatal(1,"Drop did not wait");end
  bus_ready=1;ready=0;tick();if(state!=2)$fatal(1,"Drop ignored word readiness");
  ready=1;run=0;cw_end=1;tick();if(state!=0 || !retired)$fatal(1,"Drop completion/retire failed");
  clear_fixture();run=1;cw_end=0;mem_n=4'he;use_x=1;x_n=4'hd;tick();
  if(state!=3 || !x_request)$fatal(1,"X load request missing");
  run=0;x_done=1;tick();x_done=0;repeat(3)begin tick();if(!x_request)$fatal(1,"X completion not held during pause");end
  run=1;tick();if(state!=0 || x_request)$fatal(1,"X load resume failed");
  power_good=0;#DELAY;if(halted || fault || start || retired || x_request)$fatal(1,"Unsafe-power clear failed");
  $display("RESULT timed=%0d guard_cases=%0d halt_cases=256 handshake_checks=18 failures=0",TIMED,n);$finish;
 end
endmodule
