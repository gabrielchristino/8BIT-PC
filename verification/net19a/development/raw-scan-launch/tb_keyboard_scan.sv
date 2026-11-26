`timescale 1ns/1ps
module tb_keyboard_scan;
 parameter TIMED=0,BYPASS_READY=0;
 localparam realtime CPU_HALF=TIMED?5000:5,MASTER_HALF=TIMED?19.860973:1.75;
 reg clk=0,master=0,reset_n=1,power_good=1,run=0,cpu_running=1;
 always #CPU_HALF if(cpu_running)clk=~clk;
 always #MASTER_HALF master=~master;
 wire req,wr,ack,boot,eb,z,c,halted,retired;
 wire [15:0] address,pc,sp,x;wire [7:0] wdata,rdata,a,b,pixel,h;
 wire [9:0] v;wire [1:0] vb,row,fault;wire [12:0] ca;wire [31:0] cw;
 isa1_cpu #(.TIMED(TIMED)) dut(clk,reset_n,power_good,run,boot,req,wr,address,wdata,ack,rdata,
              pc,sp,x,a,b,z,c,halted,retired,fault,ca,cw);
 isa1_memory #(.TIMED(TIMED),.FIXTURE_DEFAULTS(0)) memory(clk,master,reset_n,power_good,req,wr,address,wdata,
                    ack,rdata,boot,vb,row,eb,pixel,h,v);
 generate if(BYPASS_READY)begin:NEGATIVE
   initial force memory.access_controller.n_KEY_READY=1'b1;
 end endgenerate
 reg [7:0] image[0:32767];reg [63:0] patterns[0:4];reg [15:0] expected[0:19];
 integer test_index=0,i,k,retire_count=0,column_reads=0,row_writes=0,total_reads=0,total_rows=0;
 integer backend_edges=0,capture_edges=0,row_commit_edge=-100000,stopped_checks=0,reset_pending_checks=0;
 integer before_captures,before_reads;reg [9:0] before_v;reg monitoring=0;
 reg [15:0] held_address;reg [7:0] held_data;reg held_write;
 integer expected_row;
 always @(posedge memory.backend_clk)backend_edges=backend_edges+1;
 always @(posedge memory.capture_clk)capture_edges=capture_edges+1;
 always @(posedge memory.io_commit)if(monitoring && memory.io_select[3])begin
   row_commit_edge=backend_edges;row_writes=row_writes+1;total_rows=total_rows+1;
 end
 always @(posedge req)if(monitoring)begin
   #0.001;held_address=address;held_data=wdata;held_write=wr;
 end
 always @(posedge clk)if(monitoring)begin
   #(TIMED ? 1000 : 0.002);
   if(req && !ack && {address,wdata,wr}!=={held_address,held_data,held_write})
     $fatal(1,"CPU scan payload changed in WAIT");
   if(retired)retire_count=retire_count+1;
 end
 always @(posedge ack)if(monitoring && memory.safe)begin
   #(TIMED ? 60 : 0.001);
   if(!wr && (address==16'ha011 || address==16'ha012))begin
     if(backend_edges-row_commit_edge<16384)
       $fatal(1,"CPU column read before hardware settling");
     expected_row=test_index*4+row;
     if(rdata!==(address==16'ha011 ? expected[expected_row][7:0]:expected[expected_row][15:8]))
       $fatal(1,"CPU scan byte mismatch case=%0d row=%0d address=%h got=%h",test_index,row,address,rdata);
     column_reads=column_reads+1;total_reads=total_reads+1;
   end
 end
 task prepare_case;
 begin
   monitoring=0;run=0;reset_n=0;cpu_running=1;
   repeat(10)@(negedge clk);reset_n=1;
   repeat(20)@(negedge memory.backend_clk);
   memory.generation=test_index+1;memory.keys=patterns[test_index];
   for(i=0;i<32768;i=i+1)begin memory.frontend.U3.mem[i]=image[i];memory.frontend.U3.tag[i]=memory.generation;end
   retire_count=0;column_reads=0;row_writes=0;row_commit_edge=-100000;
   @(negedge clk);monitoring=1;run=1;
 end
 endtask
 task wait_halt;
 begin:execute
   repeat(1000000)begin
     @(negedge clk);
     if(halted)disable execute;
   end
   $fatal(1,"CPU scan watchdog PC=%h",pc);
 end
 endtask
 initial begin
   $readmemh("scan_image.hex",image);$readmemh("scan_patterns.hex",patterns);$readmemh("scan_expected.hex",expected);
   #100;reset_n=0;
   for(test_index=0;test_index<5;test_index=test_index+1)begin
     prepare_case();
     if(test_index==3)begin
       wait(req && !wr && address==16'ha011);
       @(negedge clk);cpu_running=0;
       before_captures=capture_edges;before_v=v;before_reads=column_reads;
       repeat(20000)@(negedge memory.backend_clk);
       if(ack!==1 || column_reads!=before_reads+1 || capture_edges-before_captures<19000 || v==before_v)
         $fatal(1,"CPU clock pause blocked scan completion/video or repeated ACK");
       if({address,wdata,wr}!=={held_address,held_data,held_write})$fatal(1,"paused CPU payload changed");
       stopped_checks=stopped_checks+1;cpu_running=1;
     end
     if(test_index==4)begin
       wait(req && !wr && address==16'ha011);
       repeat(100)@(negedge memory.backend_clk);
       if(ack!==0 || column_reads!=0)$fatal(1,"pending reset fixture missed quiet WAIT");
       monitoring=0;run=0;reset_n=0;
       repeat(20)@(negedge clk);
       if(ack!==0 || req!==0)$fatal(1,"pending scan reset did not cancel old handshake");
       reset_pending_checks=reset_pending_checks+1;
       prepare_case();
     end
     wait_halt();run=0;
     repeat(5)@(negedge clk);
     if(fault!==0 || retire_count!=26 || column_reads!=8 || row_writes!=4 || boot!==1 || row!==3)
       $fatal(1,"CPU scan completion case=%0d retired=%0d reads=%0d writes=%0d fault=%h",test_index,retire_count,column_reads,row_writes,fault);
     for(k=0;k<8;k=k+1)
       if(memory.ram_read(16'h6000+k)!==(k%2?expected[test_index*4+k/2][15:8]:expected[test_index*4+k/2][7:0]))
         $fatal(1,"CPU scan RAM result mismatch");
     monitoring=0;
   end
   $display("RESULT timed=%0d scan_frames=5 completed_column_reads=40 total_column_reads=%0d completed_row_writes=20 total_row_writes=%0d stopped_cpu_checks=%0d reset_pending_checks=%0d capture_edges=%0d failures=0",TIMED,total_reads,total_rows,stopped_checks,reset_pending_checks,capture_edges);
   $finish;
 end
endmodule
