`timescale 1ns/1ps
module tb_keyboard_resume;
 parameter TIMED=1,RESOLVE_LATE=1;
 reg clk=0,bank_reset_n=1,access_safe=0;
 always #79.445 clk=~clk;
 tri [3:0] row_wires;tri [15:0] column_wires;
 wire boot,eb,ready;wire [1:0] vb,row;wire [7:0] data;
 tran contact(row_wires[0],column_wires[0]);
 keyboard_500_netlist #(.TIMED(TIMED),.RESOLVE_LATE(RESOLVE_LATE)) dut(clk,bank_reset_n,access_safe,1'b0,6'b010000,8'b0,row_wires,column_wires,boot,eb,vb,row,data,ready);
 integer i,cycles;realtime enabled_at,min_quiet=1e12;
 initial begin
   #100;bank_reset_n=0;#1000;bank_reset_n=1;
   repeat(20000)@(negedge clk);
   for(i=0;i<2;i=i+1)begin
     if(ready!==0)$fatal(1,"quiet timer advanced while row drivers disabled");
     if(row_wires!==4'b1111)$fatal(1,"disabled rows not biased high");
     // New FF clock is an existing AHC125 branch: +10ns in delayed model.
     // Release one ns before that edge to exercise the explicit boundary.
     @(negedge clk);#88.445;access_safe=1;enabled_at=$realtime;cycles=0;
     while(!ready)begin @(negedge clk);cycles=cycles+1;if(cycles>17000)$fatal(1,"resume quiet timeout");end
     if($realtime-enabled_at<2600000)$fatal(1,"resume did not restart full quiet interval");
     if($realtime-enabled_at<min_quiet)min_quiet=$realtime-enabled_at;
     #120;if(data!==8'hfe)$fatal(1,"resume key read mismatch");
     access_safe=0;#100;
     if(ready!==0)$fatal(1,"unsafe quiet flag not cleared");
     if(i==0)repeat(20000)@(negedge clk);
   end
   if(TIMED && (dut.U41_0.recovery_events<2 || dut.U41_1.recovery_events<2))$fatal(1,"missing safe-release aperture coverage");
   $display("RESULT timed=%0d policy=%0d late_enables=2 min_quiet_ns=%0.3f recovery=%0d/%0d failures=0",TIMED,RESOLVE_LATE,min_quiet,dut.U41_0.recovery_events,dut.U41_1.recovery_events);$finish;
 end
 initial begin #20000000;$fatal(1,"resume watchdog");end
endmodule
