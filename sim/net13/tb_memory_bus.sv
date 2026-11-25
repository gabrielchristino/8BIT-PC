`timescale 1ns/1ps
module tb_memory_bus;
 parameter integer TIMED=0,EARLY_ON=0;
 reg reset_n=0,power_good=1,vram_owner=0,data_drive=0,oe_n=1,we_n=1;
 reg [14:0] ram_address=0,vram_address=0,rom_address=0,video_address=0;
 reg [7:0] write_data=0,io_data=0;reg [3:0] cs_n=15,select=0;
 wire [7:0] read_data,video_data;
 memory_bus_netlist #(.TIMED(TIMED),.EARLY_ON(EARLY_ON)) dut(.*);
 integer i,k,pass,which,writes=0,reads=0,video_reads=0,ignored=0,prior;
 reg [7:0] expected;
 function [7:0] image(input integer a);image=(a*17+(a>>8)+167)&255;endfunction
 function [7:0] pattern(input integer a,input integer p);pattern=p?(a>>8)^8'ha5:a[7:0]^8'h5a;endfunction
 task deselect;
 begin we_n=1;data_drive=0;oe_n=1;cs_n=15;select=0;#300;vram_owner=0;#300;end
 endtask
 task target(input integer w);
 begin deselect();vram_owner=(w==1);select=4'b1<<w;cs_n=~(4'b1<<w);#300;end
 endtask
 task store(input integer addr,input [7:0] value);
 begin
   oe_n=1;we_n=1;data_drive=0;ram_address=addr;vram_address=addr;write_data=value;
   #200;data_drive=1;#200;we_n=0;#200;we_n=1;#200;data_drive=0;#200;writes=writes+1;
 end
 endtask
 initial begin
   #2000;reset_n=1;#1000;
   if(!$isunknown(dut.U1.peek(0)) || !$isunknown(video_data))$fatal(1,"SRAM power-up was artificially initialized");
   for(i=0;i<32768;i=i+1)begin dut.U3.mem[i]=image(i);dut.U3.tag[i]=0;end
   dut.U3.update_seq=dut.U3.update_seq+1;
   for(pass=0;pass<2;pass=pass+1)for(which=0;which<2;which=which+1)begin
     target(which);
     for(i=0;i<32768;i=i+1)begin
       expected=pattern(i,pass);store(i,expected);
       if(which==0 && dut.U1.peek(i)!==expected || which==1 && dut.U2.peek(i)!==expected)$fatal(1,"physical write offset mismatch %0d/%0d",which,i);
     end
     data_drive=0;we_n=1;oe_n=0;
     for(i=0;i<32768;i=i+1)begin
       ram_address=i;vram_address=i;#400;
       if(read_data!==pattern(i,pass))$fatal(1,"read mismatch chip=%0d addr=%h got=%h",which,i,read_data);
       reads=reads+1;
     end
     if(which==1)begin
       deselect();
       for(i=0;i<32768;i=i+1)begin
         video_address=i;#400;if(video_data!==pattern(i,pass))$fatal(1,"video address/data path mismatch %h",i);
         video_reads=video_reads+1;
       end
     end
   end
   target(2);oe_n=0;
   for(i=0;i<32768;i=i+1)begin rom_address=i;#400;if(read_data!==image(i))$fatal(1,"EEPROM read mismatch %h",i);reads=reads+1;end
   oe_n=1;
   for(k=0;k<16;k=k+1)begin
     rom_address=1<<k;store(0,8'h00);
     if(dut.U3.peek(rom_address)!==image(rom_address))$fatal(1,"protected EEPROM changed");ignored=ignored+1;
   end
   target(3);oe_n=0;
   for(i=0;i<256;i=i+1)begin io_data=i;#400;if(read_data!==i[7:0])$fatal(1,"MMIO read mux mismatch");reads=reads+1;end
   target(0);ram_address=15'h1234;oe_n=1;write_data=8'h17;data_drive=1;#300;we_n=0;#50;reset_n=0;
   #500;
   if(dut.U1.aborted_writes!=1 || !$isunknown(dut.U1.peek(15'h1234)))$fatal(1,"reset-truncated write not represented as unknown");
   we_n=1;data_drive=0;cs_n=15;oe_n=1;#300;reset_n=1;#500;
   $display("RESULT timed=%0d early_on=%0d normal_writes=%0d reads=%0d video_reads=%0d ignored_rom_writes=%0d reset_unknown_writes=%0d failures=0",TIMED,EARLY_ON,dut.U1.normal_writes+dut.U2.normal_writes,reads,video_reads,ignored,dut.U1.aborted_writes);$finish;
 end
endmodule
