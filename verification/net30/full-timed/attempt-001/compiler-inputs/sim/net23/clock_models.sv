`timescale 1ns/1ps
// Configured ACH behavior, NOT an analog oscillator model or jitter guarantee.
// Qualified power is separate from RAW reset. Invalid/startup output is X.
module net23_ach #(parameter realtime PERIOD_NS=39.721946,DUTY=0.5,STARTUP_NS=10000000)(
 input wire power_valid,enable,output wire q);
 reg phase=0,running=0;
 assign q=(power_valid===1'b1 && enable===1'b1 && running) ? phase:1'bx;
 initial begin
   if(PERIOD_NS<=0 || DUTY<=0 || DUTY>=1 || STARTUP_NS<0)$fatal(1,"invalid oscillator configuration");
   forever begin
     phase=0;running=0;
     wait(power_valid===1'b1 && enable===1'b1);
     fork : operating_interval
       begin
         #STARTUP_NS;running=1;
         forever begin
           phase=1;#(PERIOD_NS*DUTY);
           phase=0;#(PERIOD_NS*(1-DUTY));
         end
       end
       begin
         wait(power_valid!==1'b1 || enable!==1'b1);
       end
     join_any
     disable operating_interval;
   end
 end
endmodule
