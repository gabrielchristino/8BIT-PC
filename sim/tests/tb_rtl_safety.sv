`timescale 1ns/1ps
module tb_rtl_safety;
 parameter integer USE_HC191=0;
 reg clk=0,video_clk=0,reset_n=0,power_good=1,run=0;
 always #5 clk=~clk;always #7 video_clk=~video_clk;
 wire req,wr,ack,boot,eb,z,c,halted,retired;
 wire [15:0] address,pc,sp,x;wire [7:0] wdata,rdata,a,b,pixel,h;
 wire [9:0] v;wire [1:0] vb,row,fault;wire [12:0] ca;wire [31:0] cw;
 isa1_cpu #(.USE_HC191(USE_HC191)) dut(clk,reset_n,power_good,run,boot,req,wr,address,wdata,ack,rdata,
              pc,sp,x,a,b,z,c,halted,retired,fault,ca,cw);
 isa1_memory memory(clk,video_clk,reset_n,power_good,req,wr,address,wdata,
                    ack,rdata,boot,vb,row,eb,pixel,h,v);
 integer ops[0:25];integer oi,cut,power_cut,cycles,baseline,cases=0,commits,ram_before,vram_before,j;
 task fixture(input integer op);
   begin
     run=0;reset_n=0;power_good=1;
     repeat(2)@(negedge clk);
     reset_n=1;repeat(3)@(negedge clk);
     memory.generation=memory.generation+1;memory.boot=0;memory.latency=3;
     memory.ram[16384]=op;memory.ram_tag[16384]=memory.generation;
     memory.ram[16385]=0;memory.ram_tag[16385]=memory.generation;
     memory.ram[16386]=8'h80;memory.ram_tag[16386]=memory.generation;
     memory.ram[32764]=0;memory.ram_tag[32764]=memory.generation;
     memory.ram[32765]=8'h40;memory.ram_tag[32765]=memory.generation;
     dut.pc=16'h4000;dut.sp=16'h7ffc;dut.a=8'h55;dut.b=3;dut.x_register=16'h8000;
     dut.x_bank.nibble[0].counter.q=0;dut.x_bank.nibble[1].counter.q=0;
     dut.x_bank.nibble[2].counter.q=0;dut.x_bank.nibble[3].counter.q=8;
     run=1;
   end
 endtask
 initial begin
   ops[0]=0;ops[1]=16;ops[2]=17;
   for(j=0;j<7;j=j+1)ops[3+j]=32+j;
   for(j=0;j<7;j=j+1)ops[10+j]=48+j;
   ops[17]=64;ops[18]=65;ops[19]=66;
   for(j=0;j<5;j=j+1)ops[20+j]=80+j;
   ops[25]=255;
   for(oi=0;oi<26;oi=oi+1)begin
     fixture(ops[oi]);baseline=0;
     begin:baseline_loop
       repeat(2000)begin @(posedge clk);#1;baseline=baseline+1;if(retired)disable baseline_loop;end
       $fatal(1,"safety baseline timeout");
     end
     for(power_cut=0;power_cut<2;power_cut=power_cut+1)begin
       for(cut=0;cut<=baseline+2;cut=cut+1)begin
         fixture(ops[oi]);
         for(cycles=0;cycles<cut;cycles=cycles+1)begin
           @(posedge clk);#1;if(retired)run=0;
         end
         #2;
         if(power_cut)power_good=0;else reset_n=0;
         #0.01;
         ram_before=memory.ram_writes;vram_before=memory.vram_writes;commits=memory.transactions;
         if(req || wr || ack || pc!==0 || sp!==16'h8000 || {a,b,x,z,c,halted,fault}!==0)
           $fatal(1,"reset state failure op=%h cut=%0d power=%0d",ops[oi],cut,power_cut);
         repeat(8)begin
           @(posedge clk);#1;
           if(req || wr || ack || memory.ram_writes!=ram_before || memory.vram_writes!=vram_before || memory.transactions!=commits)
             $fatal(1,"stale write/ack after reset op=%h cut=%0d",ops[oi],cut);
         end
         run=0;power_good=1;reset_n=1;#1;
         if(ca!==4096 || !boot || vb!==0 || eb!==0 || row!==0)
           $fatal(1,"restart contract failure");
         cases=cases+1;
       end
     end
   end
   $display("RESULT hc191=%0d reset_power_cases=%0d opcodes=26 failures=0",USE_HC191,cases);$finish;
 end
endmodule
