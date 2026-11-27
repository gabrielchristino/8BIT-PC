`timescale 1ns/1ps
module compiled_smoke;
 reg [7:0] uninitialized;
 reg e0=0,e1=0,contact=0,src=0;
 tri [7:0] bus;
 tri line_a,line_b;
 assign bus=e0?8'haa:8'bz;
 assign bus=e1?8'h55:8'bz;
 assign line_a=e0?1'b0:1'bz;
 pullup(line_a);pullup(line_b);
 tranif1 sw(line_a,line_b,contact);
 wire delayed;
 assign #(8.5,1) delayed=src;
 realtime rose=-1,fell=-1;
 always @(posedge delayed)rose=$realtime;
 always @(negedge delayed)fell=$realtime;
 initial begin
   #2;
   if(uninitialized!==8'bx || bus!==8'bz || line_a!==1'b1 || line_b!==1'b1)$fatal(1,"four-state startup/pullup semantics lost");
   e0=1;#1;if(bus!==8'haa || line_a!==0 || line_b!==1)$fatal(1,"isolated switch semantics lost");
   contact=1;#1;if(line_b!==0)$fatal(1,"bidirectional switch semantics lost");
   e1=1;#1;if(bus!==8'bx)$fatal(1,"bus contention X semantics lost");
   e0=0;e1=0;#1;if(bus!==8'bz || line_b!==1)$fatal(1,"tristate release semantics lost");
   #14;src=1;#20;src=0;#2;
   if(rose!=28.5 || fell!=41 || delayed!==0)$fatal(1,"independent rise/fall delays lost rise=%0.3f fall=%0.3f",rose,fell);
   $display("RESULT four_state=1 bidirectional_switch=1 contention_x=1 delayed_edges=%0.3f/%0.3f failures=0",rose,fell);$finish;
 end
endmodule
