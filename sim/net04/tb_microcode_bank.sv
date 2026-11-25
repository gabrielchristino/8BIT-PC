`timescale 1ns/1ps
module tb_microcode_bank;
 parameter integer TIMED=0;
 localparam HALF=TIMED?500:5,SETTLE=TIMED?300:1;
 reg clk=0,reset_n=0,power_good=1,advance_req=0,execute_pulse=0;reg [7:0] opcode=0;
 wire ready,execute_clk,dispatch,fetch,actual;wire [3:0] step;wire [7:0] ir;
 wire [12:0] addr;wire [31:0] word;wire spu,spd;
 wire [7:0] an,sn,dn,pn;wire [3:0] mn,spn,xn,fn;wire [15:0] aln;
 microcode_bank_netlist #(.TIMED(TIMED)) dut(clk,reset_n,power_good,advance_req,execute_pulse,opcode,
   ready,execute_clk,dispatch,fetch,actual,step,ir,addr,word,spu,spd,an,sn,dn,pn,mn,spn,xn,fn,aln);
 reg [31:0] vectors[0:16383],rom_expected[0:8191];integer op,index,base,length,n=0,stalls=0,decode_checks=0,halts=0,k,s,a,rom_checks=0;
 reg [31:0] expected,fixture;reg [12:0] expected_addr;
 task tick;begin #(HALF);clk=1;#(HALF);clk=0;#(SETTLE);end endtask
 task check_decoders;
   begin
     if(an!==(8'hff^(8'b1<<word[2:0])) || sn!==(8'hff^(8'b1<<word[5:3])) ||
        dn!==(8'hff^(8'b1<<word[8:6])) || mn!==(4'hf^(4'b1<<word[10:9])) ||
        pn!==(8'hff^(8'b1<<word[13:11])) || spn!==(4'hf^(4'b1<<word[15:14])) ||
        xn!==(4'hf^(4'b1<<word[17:16])) || aln!==(16'hffff^(16'b1<<word[21:18])) ||
        fn!==(4'hf^(4'b1<<word[23:22])))$fatal(1,"control field decode mismatch word=%h",word);
     if(spd!==((word[2:0]==5)||(word[15:14]==2)))$fatal(1,"SP direction decode mismatch");
     if(spu!==(execute_pulse && ready && !word[25] && (word[15:14]==1 || word[15:14]==2)))$fatal(1,"SP enable qualification mismatch");
     decode_checks=decode_checks+1;
   end
 endtask
 initial begin
   $readmemh("sequences.hex",vectors);
   $readmemh("control.hex",rom_expected);
   for(op=0;op<256;op=op+1)begin
     advance_req=0;execute_pulse=0;reset_n=0;opcode=op;repeat(2)tick();reset_n=1;repeat(2)tick();
     if(!ready || addr!==4096)$fatal(1,"initial FETCH word not ready");
     base=op*64;length=vectors[base];
     for(index=0;index<length;index=index+1)begin
       expected_addr=vectors[base+1+2*index];expected=vectors[base+2+2*index];
       if(!ready || addr!==expected_addr || word!==expected)$fatal(1,"ROM/sequencer mismatch opcode=%h index=%d addr=%h word=%h expected=%h/%h",op,index,addr,word,expected_addr,expected);
       check_decoders();execute_pulse=1;#(SETTLE);check_decoders();execute_pulse=0;#(SETTLE);
       // Perturb asynchronous ROM outputs at the same address during WAIT.
       dut.U11.rom[addr]=~expected[7:0];dut.U12.rom[addr]=~expected[15:8];
       dut.U13.rom[addr]=~expected[23:16];dut.U14.rom[addr]=~expected[31:24];
       repeat(2)begin tick();if(word!==expected || addr!==expected_addr || !ready)$fatal(1,"ROM outputs leaked through held word");stalls=stalls+1;end
       dut.U11.rom[addr]=expected[7:0];dut.U12.rom[addr]=expected[15:8];dut.U13.rom[addr]=expected[23:16];dut.U14.rom[addr]=expected[31:24];
       #(SETTLE);
       advance_req=1;tick();advance_req=0;#(SETTLE);
       if(expected[25])begin
         if(addr!==expected_addr || word!==expected)$fatal(1,"HALT permitted microstep advance");halts=halts+1;
       end
       n=n+1;
     end
     if(!expected[25] && (addr!==4096 || !fetch))$fatal(1,"END did not restart FETCH");
   end
   // Fixture-seeded address bank: every reachable execution/FETCH ROM address.
   for(k=0;k<4112;k=k+1)begin
     dut.U1.q=k[3:0];dut.U2_0.q=k<4096;dut.U4.q=k[11:4];
     dut.U2_1.q=0;dut.U3_0.q=1;
     tick();
     if(!ready || addr!==k[12:0] || word!==rom_expected[k])$fatal(1,"physical ROM address mapping mismatch %h",k);
     check_decoders();rom_checks=rom_checks+1;
   end
   // Independent decoder fixtures, including unused field encodings/HALT masks.
   for(k=0;k<256;k=k+1)begin
     fixture=(k*32'h1a23bd)^32'h00c53186;
     dut.U7.q=fixture[7:0];dut.U8.q=fixture[15:8];dut.U9.q=fixture[23:16];dut.U10.q=fixture[31:24];
     execute_pulse=k%2;#(SETTLE);check_decoders();
   end
   for(s=0;s<4;s=s+1)for(a=0;a<8;a=a+1)begin
     fixture=(s<<14)|a;
     dut.U7.q=fixture[7:0];dut.U8.q=fixture[15:8];dut.U9.q=0;dut.U10.q=0;
     execute_pulse=1;#(SETTLE);check_decoders();
   end
   execute_pulse=0;reset_n=0;repeat(2)tick();
   if(ready || spu || addr!==4096)$fatal(1,"unsafe/reset control not inhibited");
   $display("RESULT timed=%0d opcode_sequences=256 micro_words=%0d held_word_checks=%0d rom_address_checks=%0d decoder_checks=%0d halt_blocks=%0d failures=0",TIMED,n,stalls,rom_checks,decode_checks,halts);$finish;
 end
endmodule
