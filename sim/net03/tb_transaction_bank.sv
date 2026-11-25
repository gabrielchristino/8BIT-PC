`timescale 1ns/1ps
module tb_transaction_bank;
 parameter integer TIMED=0,CASES=65536;
 localparam HALF=TIMED?500:5;
 reg clk=0,reset_n=0,power_good=1,start=0,issue_write=0,ack_raw=0;
 reg [15:0] issue_address=0;reg [7:0] issue_data=0,bus_rdata=0;
 wire ready,done,request,write_enable;wire [15:0] address;
 wire [7:0] write_data,read_data;wire [5:0] phase;
 transaction_bank_netlist #(.TIMED(TIMED)) dut(clk,reset_n,power_good,start,issue_write,ack_raw,
   issue_address,issue_data,bus_rdata,ready,done,request,write_enable,address,write_data,read_data,phase);
 integer n,waits,cycles,reset_kind,cut,op,hold_checks=0,one_shot_checks=0,reset_checks=0;
 reg [15:0] expected_address;reg [7:0] expected_data,expected_read;reg expected_write;
 task tick;begin #(HALF);clk=1;#(HALF);clk=0;end endtask
 task check_payload;
   begin
     if(address!==expected_address || write_data!==expected_data || write_enable!==expected_write)
       $fatal(1,"retained payload mismatch address=%h expected=%h",address,expected_address);
     hold_checks=hold_checks+1;
   end
 endtask
 initial begin
   repeat(4)tick();reset_n=1;repeat(4)tick();
   for(n=0;n<CASES;n=n+1)begin
     if(!ready)$fatal(1,"not idle before transaction %0d",n);
     expected_address=n;expected_data=n^(n>>8);expected_read=expected_data^8'hb7;expected_write=n%2;
     issue_address=expected_address;issue_data=expected_data;issue_write=expected_write;start=1;
     tick(); // Accepted; capture phase asserted.
     if(phase!==6'b000001 || request)$fatal(1,"capture phase missing");
     tick(); // Capture registers, then settle for a full clock interval.
     if(phase!==6'b000010 || request)$fatal(1,"payload settling phase missing");
     issue_address=~expected_address;issue_data=~expected_data;issue_write=~expected_write;
     tick();
     if(!request)$fatal(1,"request not issued after settling");
     check_payload();
     for(waits=0;waits<n%8;waits=waits+1)begin
       tick();if(!request || done)$fatal(1,"request abandoned without ACK");check_payload();
     end
     bus_rdata=expected_read;ack_raw=1;
     cycles=0;
     while(request && cycles<8)begin tick();cycles=cycles+1;end
     if(request)$fatal(1,"synchronized ACK not consumed");
     repeat(n%4)tick();
     ack_raw=0;cycles=0;
     while(!done && cycles<10)begin tick();cycles=cycles+1;end
     if(!done || request || write_enable || read_data!==expected_read)$fatal(1,"completion/read capture failure");
     // A held START must not retrigger; the result must remain retained.
     bus_rdata=~expected_read;
     repeat(3)begin
       tick();
       if(done || request || ready || read_data!==expected_read)$fatal(1,"held START repeated or result changed");
       one_shot_checks=one_shot_checks+1;
     end
     start=0;tick();
     if(!ready || request)$fatal(1,"controller did not rearm");
   end
   for(reset_kind=0;reset_kind<2;reset_kind=reset_kind+1)
     for(op=0;op<2;op=op+1)for(cut=0;cut<21;cut=cut+1)begin
       start=0;reset_n=0;power_good=1;ack_raw=0;repeat(3)tick();reset_n=1;repeat(3)tick();
       issue_write=op;issue_address=16'h5aa5;issue_data=8'hc3;start=1;
       for(cycles=0;cycles<cut;cycles=cycles+1)begin
         if(cycles==7)ack_raw=1;
         if(cycles==12)ack_raw=0;
         tick();
       end
       if(reset_kind)power_good=0;else reset_n=0;
       start=0;ack_raw=1;repeat(3)tick();
       if(request || write_enable || done || phase!==0)$fatal(1,"reset did not cancel transaction");
       power_good=1;reset_n=1;repeat(4)tick();
       if(ready || request || done)$fatal(1,"stale ACK accepted after reset");
       ack_raw=0;repeat(5)tick();
       if(!ready || request || done)$fatal(1,"restart failed after stale ACK drained");
       reset_checks=reset_checks+1;
     end
   $display("RESULT timed=%0d transactions=%0d payload_hold_checks=%0d held_start_checks=%0d reset_stale_ack_cases=%0d failures=0",
      TIMED,CASES,hold_checks,one_shot_checks,reset_checks);$finish;
 end
endmodule
