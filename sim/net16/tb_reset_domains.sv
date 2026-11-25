`timescale 1ns/1ps
module tb_reset_domains;
 parameter TIMED=0,RESOLVE_LATE=1,FAULT_EARLY=0,FAULT_CPU=0;
 parameter realtime ASSERT_DELAY=1000,RELEASE_DELAY=42000;
 reg raw_safe_n,backend=0,cpu=0,run_backend=1,run_cpu=1;
 wire bank_n,cpu_n,access_safe;
 reset_domains_netlist #(.TIMED(TIMED),.RESOLVE_LATE(RESOLVE_LATE),.ASSERT_DELAY(ASSERT_DELAY),.RELEASE_DELAY(RELEASE_DELAY)) dut(raw_safe_n,backend,cpu,bank_n,cpu_n,access_safe);
 always #79.445 if(run_backend)backend=~backend;
 always #5000 if(run_cpu)cpu=~cpu;
 wire bank_reset=FAULT_EARLY ? raw_safe_n : bank_n;
 wire cpu_reset=FAULT_EARLY ? raw_safe_n : cpu_n;
 wire safe=FAULT_CPU ? raw_safe_n & bank_n : access_safe;
 wire we_n;
 // Worst selected existing WE path, downstream of the new fast qualifier.
 assign #40 we_n=~safe;
 wire [5:0] bank_q,cpu_q;
 hc174_model #(.TIMED(TIMED)) bank(backend,bank_reset,6'b111111,bank_q);
 hc174_model #(.TIMED(TIMED)) core(cpu,cpu_reset,6'b111111,cpu_q);
 integer i,cpu_pauses=0,backend_pauses=0;
 realtime began,min_order=1e30,order_delay;
 reg monitoring=0;
 always @(negedge bank_reset or negedge cpu_reset)if(monitoring)begin
   if(we_n!==1'b1)$fatal(1,"state reset before WE inhibition");
   order_delay=$realtime-began;
   if(order_delay<min_order)min_order=order_delay;
 end
 initial begin
   #100;raw_safe_n=0;#60000;raw_safe_n=1;
   wait(access_safe===1);#20000;
   for(i=0;i<32;i=i+1)begin
     @(negedge backend);#(i*0.37+1);
     began=$realtime;monitoring=1;raw_safe_n=0;
     #200;
     if(safe!==0 || we_n!==1)$fatal(1,"fast inhibit failed");
     if(bank_reset!==1 || cpu_reset!==1)$fatal(1,"bank reset did not preserve inhibit ordering delay");
     #(ASSERT_DELAY+100);
     if(bank_reset!==0 || cpu_reset!==0)$fatal(1,"delayed reset missing");
     #40000;
     if(bank_q!==0 || cpu_q!==0)$fatal(1,"state not cleared");
     if(i%3==0)begin @(negedge cpu);run_cpu=0;cpu_pauses=cpu_pauses+1;end
     if(i%3==1)begin @(negedge backend);run_backend=0;backend_pauses=backend_pauses+1;end
     raw_safe_n=1;
     #(RELEASE_DELAY+20000);
     if(i%3==0 && (cpu_n!==0 || safe!==0))$fatal(1,"access released while CPU clock stopped");
     if(i%3==1 && (bank_n!==0 || safe!==0))$fatal(1,"access released while backend clock stopped");
     run_cpu=1;run_backend=1;
     wait(access_safe===1);#20000;
     if(bank_q!==6'b111111 || cpu_q!==6'b111111)$fatal(1,"domain did not resume");
     monitoring=0;
   end
   $display("RESULT timed=%0d policy=%0d reset_cuts=32 cpu_pauses=%0d backend_pauses=%0d min_order_ns=%0.3f recovery_backend=%0d/%0d recovery_cpu=%0d/%0d failures=0",TIMED,RESOLVE_LATE,cpu_pauses,backend_pauses,min_order,dut.U3_0.recovery_events,dut.U3_1.recovery_events,dut.U5_0.recovery_events,dut.U5_1.recovery_events);
   $finish;
 end
 initial begin #20000000;$fatal(1,"reset domain watchdog");end
endmodule
