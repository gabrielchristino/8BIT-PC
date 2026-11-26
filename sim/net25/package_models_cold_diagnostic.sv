// INVESTIGATION ONLY: CLR-low short clocks remain OPEN constraints, not physical approvals.
// GENERATED selected pulse investigation; original predicates/guards retained.
`timescale 1ns/1ps
// Functional/selected-delay models, not transistor models. No metastability.
module hc174_model #(parameter integer TIMED=0)(input wire clk,clr_n,input wire [5:0] d,output reg [5:0] q);
 always @(posedge clk or negedge clr_n)if(!clr_n)q<=#(TIMED?40:0) 0;else q<=#(TIMED?40:0) d;
 if(TIMED)dff_timing #(.WIDTH(6)) check_state(clk,clr_n,d);
endmodule
module dff_timing #(parameter integer WIDTH=1,RECOVERY=25,CLEAR_PULSE=20)
 (input wire clk,clr_n,input wire [WIDTH-1:0] d);
 realtime data_changed=0,clear_rise=0,clear_fall=0,clock_changed=0;
 reg saw_clear=0,saw_clock=0;
 integer reset_clock_events=0;
 always @(d)data_changed=$realtime;
 always @(negedge clr_n)begin clear_fall=$realtime;saw_clear=1;end
 always @(posedge clr_n)begin
   if($realtime>5000 && saw_clear && $realtime-clear_fall<CLEAR_PULSE)$fatal(1,"DFF clear pulse violation");
   clear_rise=$realtime;
 end
 always @(clk)begin
   if($realtime>5000 && saw_clock && $realtime-clock_changed<20)begin
     if(clr_n===1'b0)begin
       reset_clock_events=reset_clock_events+1;
       $display("OPEN_RESET_CLOCK scope=%m measured_ns=%0.3f required_ns=20 clr_n=%b",$realtime-clock_changed,clr_n);
     end else $fatal(1,"DFF clock pulse violation measured_ns=%0.3f required_ns=20 clr_n=%b",$realtime-clock_changed,clr_n);
   end
   clock_changed=$realtime;saw_clock=1;
 end
 always @(posedge clk)if(clr_n && $realtime>5000)begin
   if($realtime-data_changed<25)$fatal(1,"DFF data setup violation");
   if($realtime-clear_rise<RECOVERY)$fatal(1,"DFF clear recovery violation");
 end
endmodule
module hc377_timing(input wire clk,en_n,input wire [7:0] d,input wire valid);
 realtime data_changed=0,enable_changed=0,sampled=0;
 reg have_sample=0;
 always @(d)begin
   if(valid && have_sample && $realtime-sampled<5)$fatal(1,"HC377 data hold violation");
   data_changed=$realtime;
 end
 always @(en_n)begin
   if(valid && have_sample && $realtime-sampled<5)$fatal(1,"HC377 enable hold violation");
   enable_changed=$realtime;
 end
 always @(posedge clk)if(valid && !en_n && $realtime>5000)begin
   if($realtime-data_changed<25)$fatal(1,"HC377 data setup violation");
   if($realtime-enable_changed<25)$fatal(1,"HC377 enable setup violation");
   sampled=$realtime;have_sample=1;
 end
endmodule
module hc74_model #(parameter integer TIMED=0)(input wire clk,clr_n,pre_n,d,output reg q,output wire qn);
 always @(posedge clk or negedge clr_n or negedge pre_n)
   if(!clr_n && !pre_n)q<=1'bx;
   else if(!clr_n)q<=#(TIMED?58:0) 0;
   else if(!pre_n)q<=#(TIMED?58:0) 1;
   else q<=#(TIMED?44:0) d;
 assign qn=~q; // QN outputs unused in this design; no QN timing claim.
endmodule
