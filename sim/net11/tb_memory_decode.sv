`timescale 1ns/1ps
module tb_memory_decode;
 parameter integer TIMED=0,SMOKE=0;
 reg [15:0] address=0;reg boot=0,eb=0;reg [1:0] vb=0;reg access=0,safe=0;
 wire [3:0] select;wire [5:0] io_select;wire [14:0] ram_address,vram_address,rom_address;
 memory_decode_netlist #(.TIMED(TIMED)) dut(address,boot,eb,vb,access,safe,select,io_select,ram_address,vram_address,rom_address);
 integer bank,a,q,cases=0,region;reg [3:0] expected;reg [5:0] expected_io;
 task check;
 begin
   #1000;
   if(boot && address<16'h4000)region=2;
   else if(address<16'h8000)region=0;
   else if(address<16'ha000)region=1;
   else if(address<16'hc000)region=3;
   else region=2;
   expected=(safe && access)?(4'b1<<region):0;
   expected_io=0;
   if(safe && access)case(address)
     16'ha000:expected_io=1;16'ha001:expected_io=2;16'ha002:expected_io=4;
     16'ha010:expected_io=8;16'ha011:expected_io=16;16'ha012:expected_io=32;
   endcase
   if(select!==expected || io_select!==expected_io)
     $fatal(1,"decode mismatch address=%h boot=%b bank=%b/%b safe/access=%b%b got=%b/%b expected=%b/%b",address,boot,eb,vb,safe,access,select,io_select,expected,expected_io);
   if(ram_address!==address[14:0] || vram_address!=={vb,address[12:0]} || rom_address!=={(address[15]&eb),address[13:0]})
     $fatal(1,"physical address mismatch address=%h eb=%b vb=%b RAM=%h VRAM=%h ROM=%h",address,eb,vb,ram_address,vram_address,rom_address);
   cases=cases+1;
 end
 endtask
 initial begin
   address=16'hc123;eb=1;safe=1;access=1;check();
   if(SMOKE)begin $display("RESULT smoke failures=0");$finish;end
   for(bank=0;bank<16;bank=bank+1)begin
     boot=bank[3];eb=bank[2];vb=bank[1:0];
     for(a=0;a<65536;a=a+1)begin
       address=a;
       for(q=0;q<4;q=q+1)begin safe=q[1];access=q[0];check();end
     end
   end
   $display("RESULT timed=%0d address_bank_enable_cases=%0d failures=0",TIMED,cases);$finish;
 end
endmodule
