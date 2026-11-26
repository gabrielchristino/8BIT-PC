`timescale 1ns/1ps
module tb_phase_skew;
 parameter FIX_GROUP=0,POLICY=1;
 parameter realtime CLOCK_A_NS=10,CLOCK_B_NS=10;
 reg master=0,raw=1;
 always #19.860973 master=~master;
 wire backend,capture,slot,visible,hs,vs,ready;
 wire [7:0] h,pixel;wire [9:0] v;
 video_system_netlist #(.TIMED(1),.EARLY_CAPTURE(1),.RESOLVE_LATE(POLICY),
   .FIX_GROUP(FIX_GROUP),.CLOCK_A_NS(CLOCK_A_NS),.CLOCK_B_NS(CLOCK_B_NS)) dut(
   master,raw,1'b1,8'h00,backend,capture,slot,visible,hs,vs,ready,h,v,pixel);
 integer warm=0,samples=0,backend_edges=0,phase0=0,phase1=0,phase2=0,phase3=0;
 always @(posedge backend)if(raw && dut.n_LOCAL_RESET_N)backend_edges=backend_edges+1;
 always @(negedge master)begin
   #15;
   if(raw && dut.n_LOCAL_RESET_N===1)begin
     warm=warm+1;
     if(warm>8)begin
       case({dut.n_P3,dut.n_P2,dut.n_P1,dut.n_P0})
         4'b0001:phase0=phase0+1;
         4'b0010:phase1=phase1+1;
         4'b0100:phase2=phase2+1;
         4'b1000:phase3=phase3+1;
         default:$fatal(1,"video phase token lost or duplicated");
       endcase
       samples=samples+1;
     end
   end else warm=0;
 end
 initial begin
   #100;raw=0;#30000;raw=1;
   wait(samples==10000);
   if(phase0!=2500 || phase1!=2500 || phase2!=2500 || phase3!=2500 || backend_edges<2500)
     $fatal(1,"phase cadence differs from divide-by-four contract");
   $display("RESULT fix_group=%0d policy=%0d clock_a_ns=%0.3f clock_b_ns=%0.3f phase_samples=10000 each_phase=2500 failures=0",FIX_GROUP,POLICY,CLOCK_A_NS,CLOCK_B_NS);
   $finish;
 end
 initial begin #1000000;$fatal(1,"phase skew watchdog");end
endmodule
