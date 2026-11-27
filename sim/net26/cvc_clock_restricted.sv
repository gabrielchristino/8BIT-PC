`timescale 1ns/1ps
// Separate tool-evaluation projection. Equivalent only for constant qualified
// oscillator power/enable after start. Original cancelable fork model intact.
// Explicit rejection on later invalid power prevents false brownout approval.
module net23_ach #(parameter realtime PERIOD_NS=39.721946,DUTY=0.5,STARTUP_NS=10000000)(
 input wire power_valid,enable,output wire q);
 reg phase=0,running=0;
 assign q=(power_valid===1'b1 && enable===1'b1 && running)?phase:1'bx;
 initial begin
   if(PERIOD_NS<=0 || DUTY<=0 || DUTY>=1 || STARTUP_NS<0)$fatal(1,"invalid oscillator configuration");
   phase=0;running=0;
   wait(power_valid===1'b1 && enable===1'b1);
   #STARTUP_NS;
   if(power_valid!==1'b1 || enable!==1'b1)$fatal(1,"restricted source invalid before startup");
   running=1;
   forever begin
     phase=1;#(PERIOD_NS*DUTY);
     phase=0;#(PERIOD_NS*(1-DUTY));
   end
 end
 always @(power_valid or enable)
   if(running && (power_valid!==1'b1 || enable!==1'b1))$fatal(1,"restricted source invalid after startup");
endmodule
