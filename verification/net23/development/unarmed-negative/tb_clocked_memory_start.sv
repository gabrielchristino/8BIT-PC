`timescale 1ns/1ps
module tb_clocked_memory_start;
 parameter integer ABSENT=0,FAULT_SAFE=0;
 reg raw=0,power_valid=0,request=0,wr=1,monitoring=0;
 reg [15:0] address=16'h5123;reg [7:0] data=8'hc5;
 wire ack,boot,eb;wire [7:0] read_data,pixel,h;wire [9:0] v;wire [1:0] vb,row;
 isa1_clocked_memory #(.TIMED(1),.FIXTURE_DEFAULTS(0)) memory(
   raw,1'b1,power_valid,request,wr,address,data,ack,read_data,boot,vb,row,eb,pixel,h,v);
 defparam memory.reset_domains.CPU_STARTUP_NS=(ABSENT==1 ? 1e12:10000000);
 defparam memory.reset_domains.MASTER_STARTUP_NS=(ABSENT==2 ? 1e12:10000000);
 realtime began,observed;
 always @(memory.frontend.U1.we_n or memory.frontend.U2.we_n)begin
   if(monitoring && ABSENT!=0 &&
      (memory.frontend.U1.we_n!==1 || memory.frontend.U2.we_n!==1))
     $fatal(1,"clock absence allowed physical SRAM WE");
 end
 always @(memory.frontend.U1.a)if(monitoring && memory.frontend.U1.we_n===0)
   $fatal(1,"source memory address changed while WE low");
 initial begin
   if(FAULT_SAFE)force memory.safe_memory=1'b1;
   #60000;monitoring=1;power_valid=1;raw=1;
   if(ABSENT!=0)begin
     // Adversarial request master, not CPU execution. WE must stay inhibited
     // even after the other source starts and the request reaches controller.
     request=1;
     #12000000;
     if(memory.safe!==0 || memory.frontend.U1.we_n!==1 || memory.frontend.U2.we_n!==1)
       $fatal(1,"clock absence allowed physical SRAM WE");
     $display("RESULT absent=%0d physical_we_inhibited=1 adversarial_request=1 failures=0",ABSENT);$finish;
   end
   wait(memory.safe===1);@(negedge memory.cpu_source);request=1;
   wait(ack===1);request=0;wait(ack===0);#1000;
   if(memory.ram_read(16'h5123)!==8'hc5)$fatal(1,"source-driven SRAM write/readback mismatch");
   @(negedge memory.cpu_source);address=16'h5124;data=8'h3a;request=1;
   wait(memory.frontend.U1.we_n===0);began=$realtime;raw=0;
   wait(memory.frontend.U1.we_n===1);observed=$realtime-began;
   if(observed>100)$fatal(1,"source memory WE exceeded100ns");
   #60000;
   if(memory.bank_memory_n!==0)$fatal(1,"source memory bank failed reset");
   power_valid=0;#1000;
   if(memory.frontend.U1.we_n!==1 || memory.frontend.U2.we_n!==1)$fatal(1,"clock loss under reset changed WE");
   $display("RESULT normal_sram_write=1 active_write_cut=1 max_we_inhibit_ns=%0.3f clock_loss_after_bank_reset=1 failures=0",observed);$finish;
 end
 initial begin #30000000;$fatal(1,"source memory watchdog");end
endmodule
