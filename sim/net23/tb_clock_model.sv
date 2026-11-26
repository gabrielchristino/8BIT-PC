`timescale 1ns/1ps
module tb_clock_model;
 parameter integer MODE=0;
 parameter realtime DUTY=0.475;
 reg valid=0;wire q;
 net23_ach #(.PERIOD_NS(MODE==1 ? 0:40),.DUTY(MODE==2 ? 1:DUTY),
   .STARTUP_NS(MODE==3 ? -1:100)) dut(valid,1'b1,q);
 realtime previous=-1;integer edges=0;
 always @(q)begin
   if(valid && (q===0 || q===1))begin
     if(previous>=0 && $realtime-previous<18.999)$fatal(1,"model pulse below configured minimum");
     previous=$realtime;edges=edges+1;
   end else previous=-1;
 end
 initial begin
   #10;if(q!==1'bx)$fatal(1,"model power-invalid not unknown");
   valid=1;#40;valid=0;#1;valid=1;
   // A one-nanosecond power interruption during startup must restart timing.
   #99.999;if(q!==1'bx)$fatal(1,"startup interruption did not restart delay");
   #0.002;if(q!==1)$fatal(1,"model did not start at selected delay");
   repeat(12)@(negedge q);
   #1;valid=0;#0.001;if(q!==1'bx)$fatal(1,"model continued output after power invalid");
   #2;valid=1;#99.999;if(q!==1'bx)$fatal(1,"second start too early");
   #0.002;if(q!==1)$fatal(1,"second start missing");
   repeat(12)@(negedge q);
   #0.001; // Allow the edge monitor in the same active region to count it.
   if(edges<48)$fatal(1,"model calibration coverage");
   $display("RESULT power_glitch_restart=1 repeated_start=1 edges=%0d failures=0",edges);$finish;
 end
 initial begin #10000;$fatal(1,"clock model watchdog");end
endmodule
