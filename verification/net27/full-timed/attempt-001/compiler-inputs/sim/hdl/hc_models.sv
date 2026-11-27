`timescale 1ns/1ps
// Simulation models, not vendor transistor models or synthesizable chip replacements.
module sn74hc191_model #(
    parameter integer T_CLK_Q=0, T_LOAD_Q=0, T_DATA_Q=0, T_TERMINAL=0
)(input wire clk, load_n, cten_n, down, input wire [3:0] d,
  output reg [3:0] q, output wire terminal);
    reg previous_clk;
    initial previous_clk = 1'b0;
    // LOAD is level-sensitive: data changes while LOAD is low must propagate.
    always @(clk or load_n or d) begin
        if (!load_n) begin
            q <= #(T_LOAD_Q > T_DATA_Q ? T_LOAD_Q : T_DATA_Q) d;
        end else if (clk === 1'b1 && previous_clk === 1'b0 && !cten_n)
            q <= #T_CLK_Q (down ? q-4'd1 : q+4'd1);
        previous_clk = clk;
    end
    assign #T_TERMINAL terminal = down ? (q==4'h0) : (q==4'hf);
    // RCO is deliberately not modeled or connected: all counters share CLK.
endmodule

module sn74hc157_model #(parameter integer T_PD=0)
 (input wire [3:0] a,b, input wire select_b,g_n, output wire [3:0] y);
    assign #T_PD y = g_n ? 4'b0 : select_b ? b : a;
endmodule

module sn74hc377_model #(parameter integer T_CQ=0)
 (input wire clk,en_n, input wire [7:0] d, output reg [7:0] q);
    // This component has no reset pin.
    always @(posedge clk) if (!en_n) q <= #T_CQ d;
endmodule

module hc191_timing_monitor(input wire clk,load_n,cten_n,down,
                          input wire [3:0] d);
    // TI SCLS121D, SN74HC191, 4.5 V, -40..85 C. Only these checks are covered.
    realtime data_change=0, enable_change=0, direction_change=0;
    realtime load_rise=0, load_fall=0, clock_rise=0;
    reg have_load_rise=0, have_clock_rise=0, have_load_fall=0;
    always @(d) begin
        if (have_load_rise && $realtime-load_rise < 5)
            $fatal(1,"HC191 data hold after LOAD violation");
        data_change=$realtime;
    end
    always @(cten_n) begin
        if (have_clock_rise && $realtime-clock_rise < 5)
            $fatal(1,"HC191 CTEN hold violation");
        enable_change=$realtime;
    end
    always @(down) begin
        if (have_clock_rise && $realtime-clock_rise < 5)
            $fatal(1,"HC191 direction hold violation");
        direction_change=$realtime;
    end
    always @(negedge load_n) begin load_fall=$realtime;have_load_fall=1;end
    always @(posedge load_n) if ($realtime>200) begin
        if (have_load_fall && $realtime-load_fall < 30)
            $fatal(1,"HC191 LOAD pulse violation");
        if ($realtime-data_change < 38)
            $fatal(1,"HC191 data setup before LOAD release violation");
        load_rise=$realtime;have_load_rise=1;
    end
    always @(posedge clk) if (load_n && $realtime>200) begin
        if (have_load_rise && $realtime-load_rise < 38)
            $fatal(1,"HC191 LOAD recovery violation");
        if (!cten_n) begin
            if ($realtime-enable_change < 51 || $realtime-direction_change < 51)
                $fatal(1,"HC191 count setup violation");
            clock_rise=$realtime;have_clock_rise=1;
        end else have_clock_rise=0;
    end
endmodule
