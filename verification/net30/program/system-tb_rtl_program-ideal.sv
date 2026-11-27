`timescale 1ns/1ps
module tb_rtl_program;
 defparam memory.reset_domains.CPU_PERIOD_NS=2*CPU_HALF, memory.reset_domains.MASTER_PERIOD_NS=2*VIDEO_HALF, memory.reset_domains.CPU_STARTUP_NS=100, memory.reset_domains.MASTER_STARTUP_NS=100;
 parameter integer RETIREMENTS=1,BUS_COUNT=1;
 parameter integer USE_HC191=0;parameter realtime CPU_HALF=5,VIDEO_HALF=1.75;
 reg reset_n=0,power_good=1,run=0;
 wire clk=memory.cpu_source,video_clk=memory.master_source;

 wire req,wr,ack,boot,eb,z,c,halted,retired;
 wire [15:0] address,pc,sp,x;wire [7:0] wdata,rdata,a,b,pixel,h;
 wire [9:0] v;wire [1:0] vb,row,fault;wire [12:0] ca;wire [31:0] cw;
 isa1_cpu #(.USE_HC191(USE_HC191)) dut(memory.cpu_core_clk,memory.cpu_reset_n,1'b1,run,boot,req,wr,address,wdata,ack,rdata,
              pc,sp,x,a,b,z,c,halted,retired,fault,ca,cw);
 isa1_clocked_memory #(.FIXTURE_DEFAULTS(0)) memory(reset_n,power_good,power_good,req,wr,address,wdata,
                    ack,rdata,boot,vb,row,eb,pixel,h,v);
 reg [82:0] expected_state[0:RETIREMENTS-1];reg [32:0] expected_bus[0:BUS_COUNT-1];
 reg [7:0] rom_image[0:32767];
 integer n=0,transactions=0,i,p,f,frame_pixels=0,wait_checks=0,pause_checks=0;
 reg fixture_ready=0;reg finished=0,frame_active=0;
 reg [15:0] held_address;reg [7:0] held_data;reg held_write;
 reg [68:0] held_core;
 always @(posedge req)begin
   #0.001;held_address=address;held_data=wdata;held_write=wr;
   held_core={pc,sp,x,a,b,z,c,halted,fault};
 end
 always @(posedge clk)begin
   #0.002;
   if(req && !ack)begin
     if({address,wdata,wr}!=={held_address,held_data,held_write} ||
        {pc,sp,x,a,b,z,c,halted,fault}!==held_core)$fatal(1,"program WAIT instability");
     wait_checks=wait_checks+1;
   end
 end
 always @(posedge ack)if(fixture_ready)begin
   #0.001;
   if(transactions>=BUS_COUNT)$fatal(1,"excess program bus commit");
   if({address,wr,wr?wdata:8'b0,wr?8'b0:rdata}!==expected_bus[transactions])
     $fatal(1,"program bus mismatch n=%0d PC=%h got=%h expected=%h",transactions,pc,
       {address,wr,wr?wdata:8'b0,wr?8'b0:rdata},expected_bus[transactions]);
   transactions=transactions+1;
 end
 always @(posedge clk)begin
   #1;
   if(retired)begin
     if(n>=RETIREMENTS)$fatal(1,"excess retirements");
     if({dut.ir,pc,sp,x,a,b,z,c,halted,fault,boot,vb,eb,row}!==expected_state[n])
       $fatal(1,"program retirement mismatch n=%0d op=%h PC=%h SP=%h A=%h",n,dut.ir,pc,sp,a);
     n=n+1;
     if(halted)begin finished=1;run=0;end
   end
 end
 initial begin
   #500;reset_n=1;#500;reset_n=0;
   $readmemh("rom_image.hex",rom_image);
   $readmemh("program_state.hex",expected_state);$readmemh("program_bus.hex",expected_bus);
   repeat(2)@(negedge clk);reset_n=1;
   @(negedge clk);
   memory.generation=1;
   memory.keys=(64'b1<<0)|(64'b1<<1)|(64'b1<<16);
   for(i=0;i<32768;i=i+1)begin memory.frontend.U3.mem[i]=rom_image[i];memory.frontend.U3.tag[i]=1;end
   fixture_ready=1;run=1;
   // Pause repeatedly at arbitrary instruction/bus phases. An accepted bus
   // operation drains; no new micro-operation may start while RUN is low.
   fork
     begin:watchdog
       repeat(20000000)@(posedge clk);
       $fatal(1,"program timeout PC=%h",pc);
     end
     begin:execution
       while(!finished)begin
         repeat(997)@(negedge clk);
         if(!finished)begin
           run=0;
           repeat(5)begin @(negedge clk);pause_checks=pause_checks+1;end
           if(!finished)run=1;
         end
       end
       disable watchdog;
     end
   join
   if(n!=RETIREMENTS || transactions!=BUS_COUNT || memory.ram_read(16'h5ff0)!==8'ha5 || fault!=0)
     $fatal(1,"program completion failure");
   for(i=0;i<32768;i=i+1)if(memory.vram_read(i)!==i[7:0])$fatal(1,"VRAM byte mismatch %0d",i);
   // Observe the actual registered pixel/capture clock, preserving
   // all samples and the reference PPM despite pipeline/clock division.
   begin:find_frame
     forever begin
       @(posedge memory.capture_clk);
       if(h==0 && v==0)disable find_frame;
     end
   end
   f=$fopen("frame.ppm","wb");$fwrite(f,"P6\n160 480\n255\n");
   for(i=0;i<105000;i=i+1)begin
     p=0;
     if(h<160 && v<480)p=memory.vram_read((v/4)*256+h);
     frame_active=h<160 && v<480;
     #0.001;
     if(pixel!==p[7:0])$fatal(1,"VGA pin pixel mismatch raster index=%0d",i);
     if(frame_active)begin
       $fwrite(f,"%c%c%c",((p>>5)&7)*255/7,((p>>2)&7)*255/7,(p&3)*255/3);
       frame_pixels=frame_pixels+1;
     end
     @(posedge memory.capture_clk);
   end
   $fclose(f);
   if(frame_pixels!=76800 || h!=0 || v!=0)$fatal(1,"frame geometry failure");
   $display("RESULT hc191=%0d cpu_half=%0d video_half=%0d retirements=%0d transactions=%0d vram_transactions=%0d frame_pixels=%0d wait_checks=%0d pause_checks=%0d failures=0",
     USE_HC191,CPU_HALF,VIDEO_HALF,n,transactions,memory.vram_transactions,frame_pixels,wait_checks,pause_checks);$display("MEMORY_MODEL ram_valid_writes=%0d vram_valid_writes=%0d ram_aborts=%0d vram_aborts=%0d fixture_defaults=%0d",memory.ram_writes,memory.vram_writes,memory.ram_aborts,memory.vram_aborts,memory.FIXTURE_DEFAULTS);$display("RESET_BOUNDARY warm_recovery_events=%0d warm_setup_events=%0d binary_resolution_late=1 analog_metastability_approved=0",memory.raster.U8.recovery_events,memory.raster.U8.setup_events);$finish;
 end
endmodule
