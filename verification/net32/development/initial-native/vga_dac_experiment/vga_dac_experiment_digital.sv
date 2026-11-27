`timescale 1ns/1ps
// XML-derived digital latch projection only; all analog elements excluded.
module net32_dac_leaf(input wire clk,input wire [9:0] r,g,b,output wire [9:0] red,green,blue);
net31_dac_latch U1(clk,{r[9],r[8],r[7],r[6],r[5],r[4],r[3],r[2],r[1],r[0]},red);
net31_dac_latch U2(clk,{g[9],g[8],g[7],g[6],g[5],g[4],g[3],g[2],g[1],g[0]},green);
net31_dac_latch U3(clk,{b[9],b[8],b[7],b[6],b[5],b[4],b[3],b[2],b[1],b[0]},blue);
endmodule
