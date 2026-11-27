`timescale 1ns/1ps
// XML pin-derived latch projection; analog omitted.
module net33_dac(input wire clk,input wire [7:0] pixel,input wire blue0,blue1,output wire [9:0] red,green,blue);
net31_dac_latch U1(clk,{pixel[7],pixel[6],pixel[5],pixel[7],pixel[6],pixel[5],pixel[7],pixel[6],pixel[5],pixel[7]},red);
net31_dac_latch U2(clk,{pixel[4],pixel[3],pixel[2],pixel[4],pixel[3],pixel[2],pixel[4],pixel[3],pixel[2],pixel[4]},green);
net31_dac_latch U3(clk,{pixel[1],pixel[0],pixel[1],pixel[0],blue1,blue0,blue1,blue0,blue1,blue0},blue);
endmodule
