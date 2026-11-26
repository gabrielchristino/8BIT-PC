`timescale 1ns/1ps
module tb_rtl_cpu;
 parameter integer CASES=1;
 parameter integer USE_HC191=0;
 reg clk=0,video_clk=0,reset_n=0,power_good=1,run=0;
 always #5 clk=~clk;
 always #1.75 video_clk=~video_clk;
 wire req,wr,ack,boot,eb,z,c,halted,retired;
 wire [15:0] address,pc,sp,x;
 wire [7:0] wdata,rdata,a,b,pixel,h;
 wire [9:0] v;
 wire [1:0] vb,row,fault;
 wire [12:0] ca;wire [31:0] cw;
 isa1_cpu #(.USE_HC191(USE_HC191)) dut(clk,reset_n,power_good,run,boot,req,wr,address,wdata,ack,rdata,
              pc,sp,x,a,b,z,c,halted,retired,fault,ca,cw);
 isa1_memory memory(clk,video_clk,reset_n,power_good,req,wr,address,wdata,
                    ack,rdata,boot,vb,row,eb,pixel,h,v);
 reg [31:0] vectors[0:CASES*64-1];
 integer case_id,base,j,cycles,trace_index,trace_base,wait_checks=0,total_transactions=0;
 reg active=0;
 reg [15:0] held_address;reg [7:0] held_data;reg held_write;
 reg [74:0] held_state;
 always @(posedge req) if(active) begin
   #0.001;held_address=address;held_data=wdata;held_write=wr;
   held_state={pc,sp,x,a,b,z,c,halted,fault,6'b0};
 end
 always @(posedge clk) if(active) begin
   #0.002;
   if(req && !ack) begin
     if({address,wdata,wr} !== {held_address,held_data,held_write})
       $fatal(1,"payload changed during WAIT case=%0d",case_id);
     if({pc,sp,x,a,b,z,c,halted,fault,6'b0} !== held_state)
       $fatal(1,"architectural change during WAIT case=%0d",case_id);
     wait_checks=wait_checks+1;
   end
 end
 always @(posedge ack) if(active) begin
   #0.001;
   if(!req || trace_index>=vectors[base+30])$fatal(1,"duplicate/unexpected commit case=%0d",case_id);
   trace_base=base+32+3*trace_index;
   if(address!==vectors[trace_base][15:0] || wr!==vectors[trace_base+1][8] ||
      (wr && wdata!==vectors[trace_base+1][7:0]) || (!wr && rdata!==vectors[trace_base+2][7:0]))
     $fatal(1,"transaction mismatch case=%0d op=%h transaction=%0d address=%h wr=%b w=%h r=%h expected=%h/%h/%h",
       case_id,vectors[base+11],trace_index,address,wr,wdata,rdata,
       vectors[trace_base],vectors[trace_base+1],vectors[trace_base+2]);
   trace_index=trace_index+1;total_transactions=total_transactions+1;
 end
 initial begin
   #500;reset_n=1;#500;reset_n=0;
   $readmemh("vectors.hex",vectors);
   for(case_id=0;case_id<CASES;case_id=case_id+1)begin
     base=case_id*64;active=0;run=0;reset_n=0;
     repeat(2)@(negedge clk);
     reset_n=1;
     repeat(2)@(negedge clk);
     @(negedge clk);
     @(negedge memory.backend_clk);#0.01;
     memory.peripheral.U1.q[5]=~(vectors[base+7]);memory.peripheral.U1.q[1:0]=vectors[base+8];memory.peripheral.U1.q[2]=vectors[base+9];memory.peripheral.U1.q[4:3]=vectors[base+10];
     
     @(negedge clk);
     memory.generation=case_id+1;memory.patterned_default=1;
     {dut.U154.q,dut.U153.q}=vectors[base];dut.U1.q=(vectors[base+1]) & 8'hff;dut.U2.q=((vectors[base+1]) >> 8) ^ 8'h80;dut.U113.q=vectors[base+2];dut.U114.q=vectors[base+3];
     {dut.U250.q,dut.U249.q}=vectors[base+4];dut.U117_0.q=vectors[base+5];dut.U117_1.q=vectors[base+6];
     if(vectors[base+1]<32768)begin
       memory.frontend.U1.mem[vectors[base+1]]=vectors[base+15];memory.frontend.U1.tag[vectors[base+1]]=memory.generation;
       if(vectors[base+1]+1<32768)begin
         memory.frontend.U1.mem[vectors[base+1]+1]=vectors[base+16];memory.frontend.U1.tag[vectors[base+1]+1]=memory.generation;
       end
     end
     for(j=0;j<3;j=j+1)begin memory.frontend.U1.mem[16384+j]=vectors[base+11+j];memory.frontend.U1.tag[16384+j]=memory.generation;end
     trace_index=0;cycles=0;active=1;run=1;
     begin:execute_case
       repeat(100000)begin
         @(posedge clk);#1;cycles=cycles+1;
         if(retired)disable execute_case;
       end
       $fatal(1,"instruction timeout case=%0d control=%h",case_id,ca);
     end
     run=0;
     if(trace_index!=vectors[base+30])$fatal(1,"missing commit case=%0d",case_id);
     if(pc!==vectors[base+17][15:0] || sp!==vectors[base+18][15:0] ||
       a!==vectors[base+19][7:0] || b!==vectors[base+20][7:0] || x!==vectors[base+21][15:0] ||
       z!==vectors[base+22][0] || c!==vectors[base+23][0] || halted!==vectors[base+24][0] ||
       fault!==vectors[base+25][1:0] || boot!==vectors[base+26][0] || vb!==vectors[base+27][1:0] ||
       eb!==vectors[base+28][0] || row!==vectors[base+29][1:0])
       $fatal(1,"state mismatch case=%0d op=%h PC=%h SP=%h A=%h B=%h X=%h ZC=%b%b fault=%d expectedPC=%h expectedSP=%h expectedA=%h expectedX=%h",
         case_id,vectors[base+11],pc,sp,a,b,x,z,c,fault,vectors[base+17],vectors[base+18],vectors[base+19],vectors[base+21]);
     active=0;
   end
   $display("RESULT hc191=%0d instruction_cases=%0d transactions=%0d wait_checks=%0d failures=0",USE_HC191,CASES,total_transactions,wait_checks);
   $display("MEMORY_MODEL ram_valid_writes=%0d vram_valid_writes=%0d ram_aborts=%0d vram_aborts=%0d fixture_defaults=%0d",memory.ram_writes,memory.vram_writes,memory.ram_aborts,memory.vram_aborts,memory.FIXTURE_DEFAULTS);$display("RESET_BOUNDARY stage1_recovery_events=%0d stage2_recovery_events=%0d binary_resolution_late=1 analog_metastability_approved=0",memory.raster.U8_0.recovery_events,memory.raster.U8_1.recovery_events);$finish;
 end

 reg sampled_mmio_write=0;
 always @(posedge memory.peripheral.U1.clk)
   sampled_mmio_write=memory.io_commit && memory.saved_write && memory.select[3] && (|memory.io_select[3:0]);
 always @(memory.peripheral.U1.q)if(active && reset_n && power_good)
   if(sampled_mmio_write!==1'b1)$fatal(1,"MMIO register changed without sampled commit");
 initial begin wait(active && reset_n && power_good);force memory.peripheral.n_NEXT_0=1'b1;end
endmodule
