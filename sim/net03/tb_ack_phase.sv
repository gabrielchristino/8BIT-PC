`timescale 1ns/1ps
// Digital phase sweep only: first FF intentionally has no synchronous setup check.
module tb_ack_phase;
 parameter integer TIMED=0;
 localparam HALF=TIMED?500:5;
 reg clk=0,reset_n=0,power_good=1,start=0,issue_write=0,ack_raw=0;
 reg [15:0] issue_address=0;reg [7:0] issue_data=0,bus_rdata=0;
 wire ready,done,request,write_enable;wire [15:0] address;wire [7:0] wdata,rdata;wire [5:0] phase;
 always #HALF clk=~clk;
 transaction_bank_netlist #(.TIMED(TIMED)) dut(clk,reset_n,power_good,start,issue_write,ack_raw,
    issue_address,issue_data,bus_rdata,ready,done,request,write_enable,address,wdata,rdata,phase);
 integer offsets[0:5];integer index,op,cases=0,count;
 initial begin
   offsets[0]=0;offsets[1]=1;offsets[2]=HALF-1;offsets[3]=HALF;offsets[4]=HALF+1;offsets[5]=2*HALF-1;
   repeat(4)@(negedge clk);reset_n=1;repeat(4)@(negedge clk);
   for(op=0;op<2;op=op+1)for(index=0;index<6;index=index+1)begin
     if(!ready)$fatal(1,"phase test not idle");
     issue_address=16'h4200+index;issue_data=8'ha0+index;bus_rdata=8'hb0+index;
     issue_write=op;start=1;count=0;
     while(!request && count<8)begin @(negedge clk);count=count+1;end
     if(!request)$fatal(1,"phase test request timeout");
     #(offsets[index]);ack_raw=1;
     count=0;
     while(request && count<8)begin @(negedge clk);count=count+1;end
     if(request || address!==16'h4200+index || wdata!==8'ha0+index)$fatal(1,"ACK phase lost payload");
     repeat(2)@(negedge clk);
     #(offsets[index]);ack_raw=0;
     count=0;
     while(!done && count<8)begin @(negedge clk);count=count+1;end
     if(!done || rdata!==8'hb0+index)$fatal(1,"ACK phase completion/read failure");
     repeat(2)begin @(negedge clk);if(request || done)$fatal(1,"ACK phase repeated completion");end
     start=0;repeat(3)@(negedge clk);
     if(!ready)$fatal(1,"ACK phase rearm failed");cases=cases+1;
   end
   $display("RESULT timed=%0d ack_phase_cases=%0d failures=0",TIMED,cases);$finish;
 end
 initial begin #(HALF*1000);$fatal(1,"ACK phase watchdog");end
endmodule
