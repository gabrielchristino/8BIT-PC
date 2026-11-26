// GENERATED: actual CPU clock and raster come from native sources; no external clock force.
`timescale 1ns/1ps
module tb_schmitt_cpu_fault;
 defparam memory.reset_domains.CPU_PERIOD_NS=9999.500024998750;
 defparam memory.reset_domains.MASTER_PERIOD_NS=39.723932196610;

 parameter POLICY=1;
 reg raw=1,run=0,monitoring=0,counting=0;
 wire clk=memory.cpu_source;
 wire req,wr,ack,boot,eb,z,c,halted,retired;
 wire [15:0] address,pc,sp,x;wire [7:0] wdata,rdata,a,b,pixel,h;
 wire [9:0] v;wire [1:0] vb,row,fault;wire [12:0] ca;wire [31:0] cw;
 isa1_cpu #(.TIMED(1)) cpu(memory.cpu_core_clk,memory.cpu_reset_n,1'b1,run,boot,
   req,wr,address,wdata,ack,rdata,pc,sp,x,a,b,z,c,halted,retired,fault,ca,cw);
 isa1_clocked_memory #(.TIMED(1),.FIXTURE_DEFAULTS(0),.RESET_POLICY(POLICY)) memory(
   raw,1'b1,1'b1,req,wr,address,wdata,ack,rdata,boot,vb,row,eb,pixel,h,v);
 reg [7:0] image[0:32767];reg [15:0] retained_address;reg [7:0] retained_data;
 integer i,attempt,retire_count=0,cuts=0;
 realtime began,max_we=0,observed;
 always @(posedge memory.cpu_core_clk)begin
   #1000;if(counting && retired)retire_count=retire_count+1;
 end
 always @(memory.frontend.U1.a)if(monitoring && memory.frontend.U1.we_n===0)
   $fatal(1,"CPU fault changed physical SRAM address while WE low");
 always @(memory.frontend.U2.a)if(monitoring && memory.frontend.U2.we_n===0)
   $fatal(1,"CPU fault changed physical VRAM address while WE low");
 initial begin
   $readmemh("scan_image.hex",image);
   #100;raw=0;
   for(attempt=0;attempt<2;attempt=attempt+1)begin
     run=0;counting=0;raw=0;#60000;
     memory.generation=attempt+1;
     for(i=0;i<32768;i=i+1)begin memory.frontend.U3.mem[i]=image[i];memory.frontend.U3.tag[i]=attempt+1;end
     raw=1;wait(memory.safe===1);@(negedge clk);run=1;monitoring=1;
     wait(memory.frontend.U1.we_n===0 && memory.frontend.U1.a==15'h6000);
     #(attempt*40);
     if(memory.frontend.U1.we_n!==0)$fatal(1,"CPU fault fixture missed actual write");
     retained_address=memory.saved_address;retained_data=memory.saved_data;
     began=$realtime;raw=0;
     fork
       begin
         wait(memory.frontend.U1.we_n===1);observed=$realtime-began;
         if(observed>max_we)max_we=observed;
       end
       begin
         #100;if(memory.frontend.U1.we_n!==1)$fatal(1,"CPU write WE inhibition exceeded100ns");
         #900;
         if(req!==0 || memory.cpu_reset_n!==0)$fatal(1,"actual CPU request survived fast reset");
         if({memory.saved_address,memory.saved_data}!=={retained_address,retained_data})
           $fatal(1,"actual CPU clear lost held SRAM payload");
       end
     join
     #50000;
     if(ack!==0 || memory.bank_memory_n!==0)$fatal(1,"bank did not cancel interrupted CPU write");
     // Keep the same memory epoch: interrupted writes are not rolled back or
     // erased. Restart firmware must produce its own correct final bytes.
     raw=1;wait(memory.safe===1);retire_count=0;counting=1;
     wait(halted===1);@(negedge clk);#1000;counting=0;
     if(retire_count!=26 || fault!==0)$fatal(1,"CPU restart did not retire complete scan");
     for(i=0;i<8;i=i+1)if(memory.ram_read(16'h6000+i)!==8'hff)
       $fatal(1,"restarted CPU did not replace scan result");
     run=0;cuts=cuts+1;
   end
   $display("RESULT policy=%0d actual_cpu_write_cuts=%0d restarted_scans=2 max_we_inhibit_ns=%0.3f fixture_defaults=0 failures=0",POLICY,cuts,max_we);
   $finish;
 end
 initial begin #100000000;$fatal(1,"CPU write reset watchdog");end
endmodule
