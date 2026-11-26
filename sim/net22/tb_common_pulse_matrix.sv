`timescale 1ns/1ps
module tb_common_phase_matrix;
 parameter POLICY=1,EARLY_CAPTURE=0,EARLY_ALL=0;
 parameter realtime MASTER_T=8.5,H_T=8.5,V_T=8.5,CAP_T=8.5,NOR_T=3.6,DUTY=0.5,SHIFT_RISE=1,SHIFT_FALL=12.5;
 reg master=0,raw=1;
 always begin #(39.721946*(1-DUTY));master=1;#(39.721946*DUTY);master=0;end
 wire backend,capture,slot,visible,hs,vs,ready;
 wire [7:0] h,pixel;wire [9:0] v;
 video_common_clock_netlist #(.TIMED(1),.EARLY_CAPTURE(EARLY_CAPTURE),.RESOLVE_LATE(POLICY),
   .SHIFT_RISE(SHIFT_RISE),.SHIFT_FALL(SHIFT_FALL),.EARLY_ALL(EARLY_ALL),.MASTER_T(MASTER_T),.H_T(H_T),.V_T(V_T),.CAP_T(CAP_T),.NOR_T(NOR_T)) dut(
   master,raw,1'b1,8'h00,backend,capture,slot,visible,hs,vs,ready,h,v,pixel);
 integer warm=0,samples=0,phase0=0,phase1=0,phase2=0,phase3=0,raster_steps=0;
 reg seen_capture=0;integer previous_h,previous_v;
 always @(posedge capture)begin
   #25;
   if(raw && ready)begin
     if(seen_capture)begin
       if(h!==(previous_h==199 ? 0:previous_h+1) ||
          v!==(previous_h==199 ? (previous_v==524 ? 0:previous_v+1):previous_v))
         $fatal(1,"common-clock raster cadence mismatch");
       raster_steps=raster_steps+1;
     end
     previous_h=h;previous_v=v;seen_capture=1;
   end else seen_capture=0;
 end
 always @(posedge backend)if(raw && ready && slot && (h<161 || h>192))
   $fatal(1,"common-clock SLOT outside safe H window");
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
         default:$fatal(1,"common-clock phase token lost or duplicated");
       endcase
       samples=samples+1;
     end
   end else warm=0;
 end
 initial begin
   #100;raw=0;#30000;raw=1;
   wait(samples==2000);
   if(phase0!=500 || phase1!=500 || phase2!=500 || phase3!=500 || raster_steps<490)
     $fatal(1,"common-clock matrix coverage incomplete");
   $display("RESULT policy=%0d phase_samples=2000 each_phase=500 raster_steps=%0d failures=0",POLICY,raster_steps);
   $finish;
 end
 initial begin #1000000;$fatal(1,"common-clock matrix watchdog");end
endmodule
