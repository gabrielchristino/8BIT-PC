// GENERATED from 3651b6f7534de18a7e78df660649a7ffdcfae29f0729721ff84e91e13182840d; CWR supplies held direction.
`timescale 1ns/1ps
// Rev 9.8.4.2: candidate component bank plus a REFERENCE control sequencer.
// The sequencer/gate equations are not yet mapped to physical control ICs.
module counter_word_candidate #(
    parameter [15:0] INITIAL_VALUE=16'h0000,
    parameter integer TIMED=0
)(input wire clk,reset_n,wait_in,bus_idle,commit,down,load_request,
  input wire [15:0] load_data,
  output wire [15:0] q,
  output wire ready,load_done,load_n,count_permission);
    localparam INIT=0, INIT_RELEASE=1, READY=2, CAPTURE=3,
               APPLY=4, RELEASE=5, HOLD=6;
    reg [2:0] state;
    reg request_seen;
    wire direction=down; // Direction already held by the opposite-phase control register.
    wire accept_load = state==READY && load_request && !request_seen
                       && !wait_in && bus_idle;
    // Opposite clock phase is part of the reference contract, not a gated clock.
    always @(negedge clk or negedge reset_n) begin
        if (!reset_n) begin state<=INIT;request_seen<=0;end
        else begin

            if (!load_request) request_seen<=0;
            if (accept_load) request_seen<=1;
            case(state)
                INIT: state<=INIT_RELEASE;
                INIT_RELEASE: state<=READY;
                READY: if(accept_load) state<=CAPTURE;
                CAPTURE: state<=APPLY;
                APPLY: state<=RELEASE;
                RELEASE: state<=HOLD;
                HOLD: state<=READY;
                default: state<=INIT;
            endcase
        end
    end
    assign ready = reset_n && state==READY;
    assign load_done = reset_n && state==HOLD;
    assign load_n = reset_n && state!=INIT && state!=APPLY;
    assign count_permission = ready && commit && !wait_in && bus_idle && !load_request;
    wire capture_n = !(reset_n && state==CAPTURE);
    wire select_data = reset_n && state!=INIT && state!=INIT_RELEASE;
    wire [15:0] saved_data,preset_data;
    sn74hc377_model #(.T_CQ(TIMED?40:0)) U5
        (clk,capture_n,load_data[7:0],saved_data[7:0]);
    sn74hc377_model #(.T_CQ(TIMED?40:0)) U6
        (clk,capture_n,load_data[15:8],saved_data[15:8]);
    wire [3:0] terminal,enable;
    assign enable[0]=count_permission;
    assign enable[1]=count_permission && terminal[0];
    assign enable[2]=count_permission && terminal[0] && terminal[1];
    assign enable[3]=count_permission && terminal[0] && terminal[1] && terminal[2];
    genvar i;
    generate for(i=0;i<4;i=i+1) begin: nibble
        sn74hc157_model #(.T_PD(TIMED?38:0)) mux
            (INITIAL_VALUE[4*i+:4],saved_data[4*i+:4],select_data,1'b0,
             preset_data[4*i+:4]);
        sn74hc191_model #(.T_CLK_Q(TIMED?48:0),.T_LOAD_Q(TIMED?66:0),
                         .T_DATA_Q(TIMED?60:0),.T_TERMINAL(TIMED?63:0)) counter
            (clk,load_n,!enable[i],direction,preset_data[4*i+:4],q[4*i+:4],terminal[i]);
        if(TIMED) hc191_timing_monitor monitor
            (clk,load_n,!enable[i],direction,preset_data[4*i+:4]);
    end endgenerate
endmodule
