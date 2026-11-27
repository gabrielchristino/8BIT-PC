`timescale 1ns/1ps
// Qualified-state functional projection, NOT regulator/supervisor/transistor POR model.
// supply=0: fully off/Ioff; supply=1: qualified 3.0..3.6V; supply=2: ramp unspecified.
module net35_sync #(parameter SLOW=1)(input wire [1:0] supply,input wire supervisor_released,
 input wire ready_source,h_internal,v_internal,output tri h_buffer,v_buffer,output wire oe_n);
 localparam realtime GATE_T=SLOW?6.5:2,DATA_T=SLOW?5.3:1.4,ENABLE_T=SLOW?5.7:1.2,DISABLE_T=SLOW?5.6:1.4;
 localparam realtime ACTIVE_T=DATA_T>ENABLE_T?DATA_T:ENABLE_T;
 tri pg,ready,h,v,oe;
 assign (weak1,weak0) ready=1'b0;
 assign (weak1,weak0) h=1'b0;
 assign (weak1,weak0) v=1'b0;
 assign ready=ready_source;assign h=h_internal;assign v=v_internal;
 assign (weak1,weak0) pg=supply==0?1'b0:supply==1?1'b1:1'bx;
 assign pg=(supply==1 && !supervisor_released)?1'b0:1'bz;
 assign (weak1,weak0) oe=supply==0?1'b0:supply==1?1'b1:1'bx;
 assign #GATE_T oe=supply==0?1'bz:supply==1?~(pg & ready):1'bx;
 assign oe_n=oe;
 assign #(ACTIVE_T,ACTIVE_T,DISABLE_T) h_buffer=supply==0?1'bz:supply!=1?1'bx:oe?1'bz:h;
 assign #(ACTIVE_T,ACTIVE_T,DISABLE_T) v_buffer=supply==0?1'bz:supply!=1?1'bx:oe?1'bz:v;
 // One selected active delay covers data and enable; it is not an exact cell arc.
endmodule
