`timescale 1ns/1ps
module tb_reset_memory;
 parameter POLICY=1,FAULT_BANK=0,FAULT_ADDRESS=0;
 reg clk=0,master=0,run_cpu=1,run_master=1,raw=1;
 always #5000 if(run_cpu)clk=~clk;
 always #19.860973 if(run_master)master=~master;
 reg request=0,wr=0;reg [15:0] address=0;reg [7:0] data=0;
 wire ack,boot,eb;wire [7:0] read_data,pixel,h;wire [9:0] v;wire [1:0] vb,row;
 isa1_memory #(.TIMED(1),.FIXTURE_DEFAULTS(0),.RESET_POLICY(POLICY)) memory(
   clk,master,raw,1'b1,request,wr,address,data,ack,read_data,boot,vb,row,eb,pixel,h,v);
 // Real SRAM pins are monitored even after logical SAFE drops: hold-up keeps
 // their supply valid. The predecessor model gates timing checks with SAFE.
 reg monitoring=0;
 always @(memory.frontend.U1.a)if(monitoring && memory.frontend.U1.we_n===0)
   $fatal(1,"independent RAM pin address changed while WE low");
 always @(memory.frontend.U2.a)if(monitoring && memory.frontend.U2.we_n===0)
   $fatal(1,"independent VRAM pin address changed while WE low");
 always @(negedge memory.bank_memory_n or negedge memory.bank_keyboard_n or negedge memory.bank_decode_n)
   if(monitoring && (memory.frontend.U1.we_n!==1 || memory.frontend.U2.we_n!==1))
     $fatal(1,"memory bank reset before physical WE inhibition");
 generate if(FAULT_BANK)begin:BAD_BANK
   initial force memory.bank_memory_n=raw;
 end endgenerate
 integer kind,offset_index,cuts=0,pauses=0;
 integer offsets[0:5];reg [15:0] saved_address;reg [7:0] saved_data;
 realtime began,observed_we,maximum_we=0;
 task release_reset;
 begin
   raw=1;wait(memory.safe===1);#1000;
   if(memory.cpu_reset_n!==1 || memory.bank_memory_n!==1)
     $fatal(1,"release lacks both domains");
 end
 endtask
 initial begin
   offsets[0]=0;offsets[1]=1;offsets[2]=7;offsets[3]=20;offsets[4]=40;offsets[5]=100;
   #100;raw=0;#60000;release_reset();
   monitoring=1;
   for(kind=0;kind<2;kind=kind+1)for(offset_index=0;offset_index<6;offset_index=offset_index+1)begin
     @(negedge clk);address=kind ? 16'h8123 : 16'h5123;data=8'hc5;wr=1;request=1;
     if(kind)wait(memory.frontend.U2.we_n===0);else wait(memory.frontend.U1.we_n===0);
     saved_address=memory.saved_address;saved_data=memory.saved_data;
     #(offsets[offset_index]);
     if((kind ? memory.frontend.U2.we_n : memory.frontend.U1.we_n)!==0)
       $fatal(1,"fault fixture missed active write");
     began=$realtime;raw=0;
     if(FAULT_ADDRESS && kind==0)begin
       #1;force memory.frontend.U1.a=15'h5000;
     end
     fork
       begin
         wait(memory.frontend.U1.we_n===1 && memory.frontend.U2.we_n===1);
         observed_we=$realtime-began;
         if(observed_we>maximum_we)maximum_we=observed_we;
       end
       begin
         #100;
         if(memory.frontend.U1.we_n!==1 || memory.frontend.U2.we_n!==1)
           $fatal(1,"physical SRAM WE exceeded 100ns inhibition budget");
         if(memory.cpu_reset_n!==0)$fatal(1,"CPU fast reset missing");
         if(memory.bank_memory_n!==1)$fatal(1,"memory bank cleared before RC interval");
         // Emulate only the request deassertion caused by the separate CPU
         // reset; SRAM addresses/data must already be retained by the HC377s.
         request=0;address=0;data=0;wr=0;
         #900;
         if({memory.saved_address,memory.saved_data}!=={saved_address,saved_data})
           $fatal(1,"payload lost across CPU fast reset");
       end
     join
     #21000;
     if(memory.bank_memory_n!==0 || memory.bank_keyboard_n!==0 || memory.bank_decode_n!==0)
       $fatal(1,"memory bank reset exceeded settling budget");
     #40000;
     if(ack!==0)$fatal(1,"aborted handshake survived bank reset");
     release_reset();#1000;
     if(ack!==0)$fatal(1,"old write replayed after restart");
     cuts=cuts+1;
   end
   // CPU stopped: bank release alone must not enable accesses.
   raw=0;#60000;@(negedge clk);run_cpu=0;raw=1;#100000;
   if(memory.bank_memory_n!==1 || memory.cpu_reset_n!==0 || memory.safe!==0)
     $fatal(1,"access released while CPU clock stopped");
   run_cpu=1;wait(memory.safe===1);#1000;pauses=pauses+1;
   // Master stopped: backend FF has no reset, and the bank synchronizer
   // cannot release until valid backend edges resume.
   raw=0;#60000;@(negedge master);run_master=0;raw=1;#100000;
   if(memory.bank_memory_n!==0 || memory.cpu_reset_n!==0 || memory.safe!==0)
     $fatal(1,"access released while backend clock stopped");
   run_master=1;wait(memory.safe===1);#1000;pauses=pauses+1;
   $display("RESULT policy=%0d active_write_cuts=%0d stopped_clocks=%0d max_we_inhibit_ns=%0.3f failures=0",POLICY,cuts,pauses,maximum_we);
   $finish;
 end
 initial begin #10000000;$fatal(1,"reset memory watchdog");end
endmodule
