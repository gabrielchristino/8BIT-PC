`timescale 1ns/1ps
module tb_sync_states;
 parameter SLOW=1,NEGATIVE=0;
 reg [1:0] supply=0;
 reg pg=0,ready=0,h=0,v=0;
 wire hb,vb,oe;
 integer bits,tested=0;
 net34_sync #(.SLOW(SLOW)) dut(supply,pg,NEGATIVE==1?1'b1:ready,h,v,hb,vb,oe);
 task expect_z;begin #30;if(hb!==1'bz || vb!==1'bz)$fatal(1,"sync drive while inhibited");tested=tested+1;end endtask
 initial begin
   #30;expect_z;
   supply=1;pg=0;ready=1;expect_z;
   ready=1'bx;expect_z; // local supervisor low must mask unknown source
   ready=0;pg=1;expect_z;
   ready=1;
   for(bits=0;bits<4;bits=bits+1)begin
     h=bits[0];v=bits[1];#30;
     if(hb!==h || vb!==v || oe!==0)$fatal(1,"sync buffer truth mismatch");tested=tested+1;
   end
   ready=1'bz;expect_z; // real input pulldown defines disconnected source
   ready=1;pg=0;expect_z;
   pg=1;#30;supply=0;expect_z; // exact VCC0 only, not whole falling ramp
   supply=2;#30;
   if(hb!==1'bx || vb!==1'bx)$fatal(1,"ramp falsely treated as qualified");tested=tested+1;
   supply=1;pg=0;ready=0;expect_z;
   pg=1;ready=1;h=1;v=0;#30;
   if(hb!==1 || vb!==0)$fatal(1,"sync re-enable mismatch");tested=tested+1;
   $display("RESULT sync_state_checks=%0d off_is_ioff_projection=1 ramp_unqualified=1 slow=%0d failures=0",tested,SLOW);$finish;
 end
 initial begin #10000;$fatal(1,"sync states watchdog");end
endmodule
