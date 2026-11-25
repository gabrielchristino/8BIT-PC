`timescale 1ns/1ps
// Executable phase contract only. No KiCad-derived counter/clock circuit.
// The ideal 25.175 MHz stimulus is supplied by the bench, not an oscillator BOM.
module video_contract #(parameter realtime COUNTER_Q=11.5, parameter integer CAPTURE_PHASE=3)(
 input wire master,reset_n,
 output reg backend_clk=0,
 output reg [7:0] h=199,output reg [9:0] v=524,
 output wire [14:0] address,output wire slot,
 input wire [7:0] video_data,
 output reg valid=0,output reg [7:0] pixel=0,
 output reg visible=0,hsync_n=1,vsync_n=1,
 output reg [7:0] pixel_h=0,output reg [9:0] pixel_v=0
);
 integer phase=0;reg started=0;
 assign address={v[8:2],h};
 assign slot=h>=161 && h<=192;
 always @(posedge master)begin
   if(!reset_n)begin
     phase=0;backend_clk<=0;h<=199;v<=524;started=0;
     valid<=0;pixel<=0;visible<=0;hsync_n<=1;vsync_n<=1;
   end else begin
     // Backend rises halfway through an issued pixel and falls at the next
     // issue. Grant logic is ideal here; hardware setup/hold is not closed.
     if(phase==0)begin
       backend_clk<=0;
       if(h==199)begin h<=#COUNTER_Q 0;v<=#COUNTER_Q (v==524?0:v+1);end
       else h<=#COUNTER_Q h+1;
       started=1;
     end
     if(phase==2)backend_clk<=1;
     if(phase==CAPTURE_PHASE && started)begin
       valid<=1;pixel_h<=h;pixel_v<=v;
       visible<=h<160 && v<480;
       pixel<=h<160 && v<480?video_data:0;
       hsync_n<=!(h>=164 && h<188);vsync_n<=!(v>=490 && v<492);
     end else valid<=0;
     phase=(phase+1)%4;
   end
 end
endmodule
