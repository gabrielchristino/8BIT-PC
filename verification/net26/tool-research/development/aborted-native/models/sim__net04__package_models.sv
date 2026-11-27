// Syntax-only explicit generate regions for CVC; guards and instances unchanged.
`timescale 1ns/1ps
// Functional / selected-delay pin models. Not transistor models or full PVT proof.
module hc161_model #(parameter integer TIMED=0)(input wire clk,clr_n,load_n,enp,ent,input wire [3:0] d,output reg [3:0] q,output wire rco);
 always @(posedge clk or negedge clr_n)
   if(!clr_n)q<=#(TIMED?53:0) 0;
   else if(!load_n)q<=#(TIMED?51:0)d;
   else if(enp && ent)q<=#(TIMED?51:0)(q+4'd1);
 assign rco=ent && q==15; // RCO is unconnected; no RCO timing claim.
generate
 if(TIMED)begin:timing
   realtime changed=0,cleared=0;
   always @(d or enp or ent or load_n)changed=$realtime;
   always @(posedge clr_n)cleared=$realtime;
   always @(posedge clk)if(clr_n && $realtime>5000)begin
     if($realtime-changed<43)$fatal(1,"HC161 setup envelope violation");
     if($realtime-cleared<31)$fatal(1,"HC161 clear recovery violation");
   end
 end
endgenerate
endmodule
module at28hc64_read #(parameter FILE="control_lane0.hex",parameter integer T_ACC=0)
 (input wire [12:0] a,output wire [7:0] data);
 reg [7:0] rom[0:8191];
 initial $readmemh(FILE,rom);
 // CE/OE fixed low, WE high by converter; programming/power ramps not modeled.
 assign #T_ACC data=rom[a];
endmodule
module hc138_model #(parameter integer T_PD=0)(input wire [2:0] a,input wire g1,g2a_n,g2b_n,output wire [7:0] y);
 assign #T_PD y=g1 && !g2a_n && !g2b_n ? ~(8'b1<<a) : 8'hff;
endmodule
module hc139_model #(parameter integer T_PD=0)(input wire [1:0] a,input wire g_n,output wire [3:0] y);
 assign #T_PD y=g_n ? 4'hf : ~(4'b1<<a);
endmodule
module hct377_timing(input wire clk,en_n,input wire [7:0] d,input wire valid);
 realtime data_changed=0,enable_changed=0,sampled=0;reg have_sample=0;
 always @(d)begin
   if(valid && have_sample && $realtime-sampled<3)$fatal(1,"HCT377 data hold violation");
   data_changed=$realtime;
 end
 always @(en_n)begin
   if(valid && have_sample && $realtime-sampled<5)$fatal(1,"HCT377 enable hold violation");
   enable_changed=$realtime;
 end
 always @(posedge clk)if(valid && !en_n && $realtime>5000)begin
   if($realtime-data_changed<15)$fatal(1,"HCT377 data setup violation");
   if($realtime-enable_changed<15)$fatal(1,"HCT377 enable setup violation");
   sampled=$realtime;have_sample=1;
 end
endmodule
