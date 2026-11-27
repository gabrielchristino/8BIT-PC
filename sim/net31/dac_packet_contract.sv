`timescale 1ns/1ps
// Functional proposal only. No native packages, vendor analog model or PVT claim.
// 1 ns output delay is a selected typical value, not a guaranteed maximum.
module net31_dac_latch(input wire clk, input wire [9:0] data, output reg [9:0] code);
 realtime last_data=-1000, last_clock=-1000;
 reg seen_clock=0;
 always @(data) begin
   if(seen_clock && $realtime-last_clock<1.5)$fatal(1,"DAC hold violation");
   last_data=$realtime;
 end
 always @(posedge clk) begin
   if($isunknown(data))$fatal(1,"DAC unknown data");
   if($realtime-last_data<2.0)$fatal(1,"DAC setup violation");
   last_clock=$realtime;seen_clock=1;
   code<=#1 data;
 end
 always @(negedge clk) if(seen_clock && $realtime-last_clock<3.5)
   $fatal(1,"DAC high pulse violation");
endmodule

module net31_packet_proposal #(parameter SYNC_LATE=0)(
 input wire p3,p1,input wire [7:0] pixel,input wire hs,vs,
 output wire [9:0] red,green,blue,output reg hs_out=1,vs_out=1);
 reg [7:0] held_pixel;
 reg held_hs=1,held_vs=1,previous_hs=1,previous_vs=1;
 wire [2:0] r=held_pixel[7:5],g=held_pixel[4:2];
 wire [1:0] b=held_pixel[1:0];
 wire [9:0] r10={r,r,r,r[2]},g10={g,g,g,g[2]},b10={b,b,b,b,b};
 always @(posedge p3) begin
   held_pixel<=pixel;held_hs<=hs;held_vs<=vs;
 end
 net31_dac_latch R(p1,r10,red),G(p1,g10,green),B(p1,b10,blue);
 // Common selected delay deliberately does not stand in for physical H/V drivers.
 always @(posedge p1) begin
   hs_out<=#1 (SYNC_LATE?previous_hs:held_hs);
   vs_out<=#1 (SYNC_LATE?previous_vs:held_vs);
   previous_hs<=held_hs;previous_vs<=held_vs;
 end
endmodule
