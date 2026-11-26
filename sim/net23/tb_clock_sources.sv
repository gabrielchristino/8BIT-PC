`timescale 1ns/1ps
module tb_clock_sources;
 parameter integer POLICY=1,ABSENT=0;
 parameter realtime CPU_START=10000000,MASTER_START=10000000,RELEASE_AT=12000000;
 parameter realtime CPU_PERIOD=10000,MASTER_PERIOD=39.721946,DUTY=0.475;
 reg power_valid=0,raw=0;
 wire backend,master,cpu,bank,cpu_reset,safe,bmem,bkey,bdecode,smem,skey,core,access_clock,key_clock;
 wire capture,slot,visible,hs,vs,ready;wire [7:0] h,pixel;wire [9:0] v;
 clocked_reset_netlist #(.TIMED(1),.RESOLVE_LATE(POLICY),
   .ASSERT_DELAY(19000),.RELEASE_DELAY(42000),.CPU_PERIOD_NS(CPU_PERIOD),
   .MASTER_PERIOD_NS(MASTER_PERIOD),.CPU_DUTY(DUTY),.MASTER_DUTY(DUTY),
   .CPU_STARTUP_NS(ABSENT==1 ? 1e12:CPU_START),.MASTER_STARTUP_NS(ABSENT==2 ? 1e12:MASTER_START)) clocks(
   .raw_safe_n(raw),.backend_source(backend),.osc_power_valid(power_valid),
   .bank_reset_n(bank),.cpu_reset_n(cpu_reset),.access_safe(safe),
   .bank_memory_n(bmem),.bank_keyboard_n(bkey),.bank_decode_n(bdecode),
   .safe_memory(smem),.safe_keyboard(skey),.cpu_core_clk(core),.access_clk(access_clock),
   .keyboard_clk(key_clock),.cpu_source(cpu),.master_source(master));
 video_common_clock_netlist #(.TIMED(1),.RESOLVE_LATE(POLICY),.EARLY_CAPTURE(1)) video(
   master,raw,power_valid,8'ha5,backend,capture,slot,visible,hs,vs,ready,h,v,pixel);
 integer pixels=0,cuts=0,i;realtime cpu_edge=-1,master_edge=-1;
 always @(cpu)if(raw && power_valid && cpu!==1'bx)begin
   if(cpu_edge>=0 && $realtime-cpu_edge<CPU_PERIOD*0.47)$fatal(1,"CPU source pulse shortened");
   cpu_edge=$realtime;
 end else cpu_edge=-1;
 always @(master)if(raw && power_valid && master!==1'bx)begin
   if(master_edge>=0 && $realtime-master_edge<MASTER_PERIOD*0.47)$fatal(1,"MASTER source pulse shortened");
   master_edge=$realtime;
 end else master_edge=-1;
 task await_ready;
   begin
     wait(safe===1);#100;
     if(cpu_reset!==1 || bank!==1 || smem!==1 || skey!==1)$fatal(1,"clock/reset readiness mismatch");
     repeat(64)begin
       @(posedge capture);#60;
       if(ready && visible)begin
         if(pixel!==8'ha5)$fatal(1,"source raster data mismatch");
         pixels=pixels+1;
       end
     end
   end
 endtask
 initial begin
   #30000;
   if(master!==1'bx || cpu!==1'bx)$fatal(1,"unpowered oscillator silently initialized");
   power_valid=1;
   #RELEASE_AT;raw=1;
   if(ABSENT!=0)begin
     #2000000;
     if(safe!==0 || cpu_reset!==0 || smem!==0 || skey!==0)$fatal(1,"clock absent released access");
     $display("RESULT absent=%0d access_inhibited=1 failures=0",ABSENT);$finish;
   end
   // If release precedes both starts, access must remain inhibited.
   if(RELEASE_AT<CPU_START && RELEASE_AT<MASTER_START)begin
     #1000;if(safe!==0)$fatal(1,"access released before oscillator startup");
   end
   await_ready;
   for(i=0;i<3;i=i+1)begin
     @(negedge backend);#(i*7);raw=0;
     #100;if(safe!==0 || cpu_reset!==0 || visible!==0 || pixel!==0)$fatal(1,"reset did not inhibit source system");
     #50000;raw=1;await_ready;cuts=cuts+1;
   end
   raw=0;#100;power_valid=0;#1;
   if(master!==1'bx || cpu!==1'bx)$fatal(1,"power removal did not invalidate clock");
   #30000;power_valid=1;#12000000;raw=1;await_ready;
   if(pixels<64)$fatal(1,"insufficient source raster coverage");
   $display("RESULT policy=%0d starts=2 reset_cuts=%0d visible_captures=%0d oscillator_model=behavioral failures=0",POLICY,cuts,pixels);
   $finish;
 end
 initial begin #60000000;$fatal(1,"source clock watchdog");end
endmodule
