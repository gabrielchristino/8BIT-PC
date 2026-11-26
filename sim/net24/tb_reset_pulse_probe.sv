`timescale 1ns/1ps
module tb_reset_pulse_probe;
 parameter integer PROFILE=0;
 parameter realtime OFFSET_NS=39;
 reg raw=0;
 wire backend,master,cpu,bank,cpu_reset,safe,bmem,bkey,bdecode,smem,skey,core,access_clock,key_clock;
 wire capture,slot,visible,hs,vs,ready;wire [7:0] h,pixel;wire [9:0] v;
 net24_reset_pulse_netlist #(.TIMED(1),.PROFILE(PROFILE)) clocks(
   .raw_safe_n(raw),.backend_source(backend),.osc_power_valid(1'b1),
   .bank_reset_n(bank),.cpu_reset_n(cpu_reset),.access_safe(safe),
   .bank_memory_n(bmem),.bank_keyboard_n(bkey),.bank_decode_n(bdecode),
   .safe_memory(smem),.safe_keyboard(skey),.cpu_core_clk(core),.access_clk(access_clock),
   .keyboard_clk(key_clock),.cpu_source(cpu),.master_source(master));
 net24_video_pulse_netlist #(.TIMED(1),.EARLY_CAPTURE(1),.PROFILE(PROFILE)) video(
   master,raw,1'b1,8'h00,backend,capture,slot,visible,hs,vs,ready,h,v,pixel);
 net24_control_pulse_netlist #(.TIMED(1),.PROFILE(PROFILE)) control(
   .clk(access_clock),.reset_n(bmem),.power_good(1'b1),.request(1'b0),.write_request(1'b0),
   .vram_slot(slot),.key_ready(1'b1),.io_col_lo(1'b0),.io_col_hi(1'b0),
   .address(16'h5123),.write_data(8'h00),.read_bus(8'h00),.select(4'b0001));
 initial begin
   #12000000;raw=1;wait(safe===1);
   repeat(8)@(negedge backend);
   if(OFFSET_NS>=0)begin
     #OFFSET_NS;raw=0;
     $display("CUT profile=%0d offset_ns=%0.3f raw_assert_ns=%0.3f bank_memory_n=%b",PROFILE,OFFSET_NS,$realtime,bmem);
     #100000;raw=1;wait(safe===1);
   end else #100000;
   #2000;
   $display("RESULT profile=%0d offset_ns=%0.3f reset_cut=%0d failures=0",PROFILE,OFFSET_NS,OFFSET_NS>=0);$finish;
 end
 initial begin #16000000;$fatal(1,"reset pulse probe watchdog");end
endmodule
