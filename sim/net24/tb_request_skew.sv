`timescale 1ns/1ps
module tb_request_skew;
 parameter realtime FIRST_CLOCK=8.5,SECOND_CLOCK=8.5,FIRST_CQ=44;
 reg clk=0,reset_n=0,request=0;
 always #79.443892 clk=~clk;
 wire ack;wire [7:0] read_data;
 system_access_netlist #(.TIMED(1),.FIRST_CLOCK(FIRST_CLOCK),.SECOND_CLOCK(SECOND_CLOCK),.FIRST_CQ(FIRST_CQ)) dut(
   .clk(clk),.reset_n(reset_n),.power_good(1'b1),.request(request),.write_request(1'b0),
   .vram_slot(1'b1),.key_ready(1'b1),.io_col_lo(1'b0),.io_col_hi(1'b0),
   .address(16'h5123),.write_data(8'h00),.read_bus(8'ha5),.select(4'b0001),.ack(ack),.read_data(read_data));
 initial begin
   #1000;reset_n=1;
   #8000;@(negedge clk);#20;request=1;
   // REQ is stable about59ns before the first clock pin. The selected
   // counterexample is the second stage, not an asynchronous first-stage hit.
   wait(ack===1);#100;
   if(read_data!==8'ha5)$fatal(1,"request clock probe MDR readback mismatch");
   $display("RESULT first_clock_ns=%0.3f second_clock_ns=%0.3f first_cq_ns=%0.3f acknowledged_read=1 failures=0",FIRST_CLOCK,SECOND_CLOCK,FIRST_CQ);$finish;
 end
 initial begin #20000;$fatal(1,"request skew watchdog");end
endmodule
