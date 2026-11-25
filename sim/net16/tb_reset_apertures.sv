`timescale 1ns/1ps
module tb_reset_apertures;
 parameter RESOLVE_LATE=1;
 reg raw_safe_n,backend=0,cpu=0;
 wire bank_n,cpu_n,safe;
 reset_domains_netlist #(.TIMED(1),.RESOLVE_LATE(RESOLVE_LATE)) dut(raw_safe_n,backend,cpu,bank_n,cpu_n,safe);
 always #79.445 backend=~backend;
 always #5000 cpu=~cpu;
 wire [5:0] bank_q,cpu_q;
 hc174_model #(.TIMED(1)) bank(backend,bank_n,6'b111111,bank_q);
 hc174_model #(.TIMED(1)) core(cpu,cpu_n,6'b111111,cpu_q);
 integer domain,i;
 real period,half,target,delta,delay_to_release;
 initial begin
   #100;raw_safe_n=0;
   for(domain=0;domain<2;domain=domain+1)for(i=0;i<5;i=i+1)begin
     raw_safe_n=0;#30000;
     period=domain ? 10000 : 158.89;half=period/2;
     case(i)0:delta=0.25;1:delta=1.25;2:delta=2.75;3:delta=3.25;4:delta=5;endcase
     // AHC125 10ns + two AHC14 24ns + bounded charge delay 42000ns.
     target=($floor(($realtime+42034-half)/period)+2)*period+half;
     delay_to_release=target-($realtime+42034)-delta;
     #(delay_to_release);raw_safe_n=1;
     wait(safe===1);#20000;
     if(bank_q!==6'b111111 || cpu_q!==6'b111111)$fatal(1,"aperture domain did not resume");
   end
   if(dut.U3_0.recovery_events<3 || dut.U3_1.recovery_events<3 || dut.U5_0.recovery_events<3 || dut.U5_1.recovery_events<3)$fatal(1,"insufficient recovery aperture coverage");
   $display("RESULT policy=%0d aperture_cuts=10 recovery_backend=%0d/%0d recovery_cpu=%0d/%0d failures=0",RESOLVE_LATE,dut.U3_0.recovery_events,dut.U3_1.recovery_events,dut.U5_0.recovery_events,dut.U5_1.recovery_events);
   $finish;
 end
 initial begin #10000000;$fatal(1,"aperture watchdog");end
endmodule
