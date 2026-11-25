`timescale 1ns/1ps
// Pin-derived logic. RC delay and external recovery resolution are conditional abstractions.
module reset_domains_netlist #(parameter TIMED=0,RESOLVE_LATE=1,parameter realtime ASSERT_DELAY=1000,RELEASE_DELAY=42000)(input wire raw_safe_n,backend_clk,cpu_clk,output wire bank_reset_n,cpu_reset_n,access_safe);
wire n_ACCESS_SAFE;
wire n_ALL_READY;
wire n_BACKEND;
wire n_BANK_RESET_N;
wire n_CPU_CLK;
wire n_CPU_RESET_N;
wire n_CPU_SYNC1;
wire n_DELAY_CLEAR_N;
wire n_DELAY_INV;
wire n_DELAY_RC;
wire n_RAW_BUFFERED;
wire n_RAW_SAFE_N;
wire n_RESET_SYNC1;
wire U3_unused_qb0,U3_unused_qb1,U5_unused_qb0,U5_unused_qb1;
assign n_RAW_SAFE_N=raw_safe_n;
assign n_BACKEND=backend_clk;
assign n_CPU_CLK=cpu_clk;
assign #(RELEASE_DELAY,ASSERT_DELAY) n_DELAY_RC=n_RAW_BUFFERED;
assign #(TIMED?10:0) n_RAW_BUFFERED=1'b0 ? 1'bz : n_RAW_SAFE_N;
assign #(TIMED?12:0) n_DELAY_INV=~n_DELAY_RC;
assign #(TIMED?12:0) n_DELAY_CLEAR_N=~n_DELAY_INV;
net14b_ahc74 #(.TIMED(TIMED),.RESET_BOUNDARY(1),.FIRST_STAGE(1),.RESOLVE_LATE(RESOLVE_LATE)) U3_0(n_BACKEND,n_DELAY_CLEAR_N,1'b1,1'b1,n_RESET_SYNC1,U3_unused_qb0,1'b1);
net14b_ahc74 #(.TIMED(TIMED),.RESET_BOUNDARY(1),.FIRST_STAGE(0),.RESOLVE_LATE(RESOLVE_LATE)) U3_1(n_BACKEND,n_DELAY_CLEAR_N,1'b1,n_RESET_SYNC1,n_BANK_RESET_N,U3_unused_qb1,1'b1);
assign #(TIMED?10:0) n_ALL_READY=n_BANK_RESET_N & n_CPU_RESET_N;
assign #(TIMED?10:0) n_ACCESS_SAFE=n_RAW_SAFE_N & n_ALL_READY;
net14b_ahc74 #(.TIMED(TIMED),.RESET_BOUNDARY(1),.FIRST_STAGE(1),.RESOLVE_LATE(RESOLVE_LATE)) U5_0(n_CPU_CLK,n_DELAY_CLEAR_N,1'b1,1'b1,n_CPU_SYNC1,U5_unused_qb0,1'b1);
net14b_ahc74 #(.TIMED(TIMED),.RESET_BOUNDARY(1),.FIRST_STAGE(0),.RESOLVE_LATE(RESOLVE_LATE)) U5_1(n_CPU_CLK,n_DELAY_CLEAR_N,1'b1,n_CPU_SYNC1,n_CPU_RESET_N,U5_unused_qb1,1'b1);
assign bank_reset_n=n_BANK_RESET_N;
assign cpu_reset_n=n_CPU_RESET_N;
assign access_safe=n_ACCESS_SAFE;
endmodule
