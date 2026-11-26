`timescale 1ns/1ps
module tb_drain_pulse;
 parameter integer PROFILE=0,POLICY=1,INITIAL_PHASE=-1;
 parameter realtime OFFSET_NS=39,RAW_LOW_NS=100000,RAW_RELEASE_NS=12000000;
 reg raw=0;
 wire backend,master,cpu,bank,cpu_reset,safe,bmem,bkey,bdecode,smem,skey,core,access_clock,key_clock;
 wire capture,slot,visible,hs,vs,ready,phase_init,bank_sync,bank_arm;wire [7:0] h,pixel;wire [9:0] v;
 integer falls=0;
 phase_drain_reset_netlist #(.TIMED(1),.PROFILE(PROFILE),.RESOLVE_LATE(POLICY)) clocks(
   .raw_safe_n(raw),.backend_source(backend),.osc_power_valid(1'b1),.bank_arm(bank_arm),
   .bank_reset_n(bank),.cpu_reset_n(cpu_reset),.access_safe(safe),
   .bank_memory_n(bmem),.bank_keyboard_n(bkey),.bank_decode_n(bdecode),
   .safe_memory(smem),.safe_keyboard(skey),.cpu_core_clk(core),.access_clk(access_clock),
   .keyboard_clk(key_clock),.cpu_source(cpu),.master_source(master),.phase_init_n(phase_init),.bank_sync1(bank_sync));
 phase_drain_video_netlist #(.TIMED(1),.EARLY_CAPTURE(1),.PROFILE(PROFILE),.RESOLVE_LATE(POLICY)) video(
   .master(master),.reset_n(raw),.power_good(1'b1),.phase_init_n(phase_init),.bank_sync1(bank_sync),
   .video_data(8'h00),.backend_clk(backend),.capture_clk(capture),.slot(slot),.visible(visible),
   .hsync_n(hs),.vsync_n(vs),.ready(ready),.bank_arm(bank_arm),.h(h),.v(v),.pixel(pixel));
 net25_control_pulse_netlist #(.TIMED(1),.PROFILE(PROFILE)) control(
   .clk(access_clock),.reset_n(bmem),.power_good(1'b1),.request(1'b0),.write_request(1'b0),
   .vram_slot(slot),.key_ready(1'b1),.io_col_lo(1'b0),.io_col_hi(1'b0),
   .address(16'h5123),.write_data(8'h00),.read_bus(8'h00),.select(4'b0001));
 initial begin
   if(INITIAL_PHASE>=0)begin
     #0.001;video.U9.state=INITIAL_PHASE;video.U9.q=INITIAL_PHASE;
   end
 end
 always @(posedge bank)begin
   if(ready!==1'b1)$fatal(1,"banks released before valid capture ready");
 end
 always @(negedge backend)if(raw===0 && phase_init===0)falls=falls+1;
 initial begin
   #RAW_RELEASE_NS;raw=1;wait(safe===1);
   repeat(8)@(negedge backend);
   if(OFFSET_NS>=0)begin
     #OFFSET_NS;raw=0;
     $display("CUT profile=%0d offset_ns=%0.3f raw_assert_ns=%0.3f bank_memory_n=%b",PROFILE,OFFSET_NS,$realtime,bmem);
     #RAW_LOW_NS;raw=1;wait(safe===1);
   end else #100000;
   #2000;
   $display("RESULT profile=%0d offset_ns=%0.3f policy=%0d initial_phase=%0d ready=%b safe=%b failures=0",PROFILE,OFFSET_NS,POLICY,INITIAL_PHASE,ready,safe);$finish;
 end
 initial begin #16000000;$fatal(1,"drain pulse watchdog");end
endmodule
