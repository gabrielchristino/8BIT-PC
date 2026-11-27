`timescale 1ns/1ps
module tb_dac_packet;
 parameter NEGATIVE=0;
 reg p3=0,p1=0,hs=1,vs=1;
 reg [7:0] pixel=0;
 wire [9:0] r,g,b;
 wire ho,vo;
 real period=1000000000.0/25175000.0;
 integer i,h,v,visible=0,hs_count=0,vs_count=0,samples=0;
 reg probe_clk=0;
 reg [9:0] probe_data=0;
 wire [9:0] probe_code;
 net31_dac_latch probe(probe_clk,probe_data,probe_code);
 net31_packet_proposal #(.SYNC_LATE(NEGATIVE==4)) dut(p3,p1,pixel,hs,vs,r,g,b,ho,vo);
 task sample(input [7:0] value,input hh,vv);
   integer er,eg,eb;
   begin
     pixel=value;hs=hh;vs=vv;
     #20;p3=1;#1;p3=0;#(2*period-1);p1=1;
     #2;
     // Arithmetic reference independent of concatenation implementation.
     er=(((value>>5)&7)*1023+3)/7;
     eg=(((value>>2)&7)*1023+3)/7;
     eb=((value&3)*1023+1)/3;
     if(r!==er[9:0] || g!==eg[9:0] || b!==eb[9:0])$fatal(1,"RGB mapping mismatch");
     if(ho!==hh || vo!==vv)$fatal(1,"packet sync mismatch");
     #(period-2);p1=0;#(period-20);
   end
 endtask
 initial begin
   if(NEGATIVE>=1 && NEGATIVE<=3)begin
     #10;
     if(NEGATIVE==1)begin probe_data=10'h3ff;#1;probe_clk=1;end
     if(NEGATIVE==2)begin probe_clk=1;#1;probe_data=10'h3ff;end
     if(NEGATIVE==3)begin probe_clk=1;#2;probe_clk=0;end
     #10;$fatal(1,"negative guard failed to fire");
   end else begin
     for(i=0;i<256;i=i+1)sample(i[7:0],1,1);
     for(v=0;v<525;v=v+1)for(h=0;h<200;h=h+1)begin
       sample((h<160 && v<480)?((h*17+v*13)&255):0,
              !(h>=164 && h<188),!(v>=490 && v<492));
       samples=samples+1;
       if(h<160 && v<480)visible=visible+1;
       if(!ho)hs_count=hs_count+1;
       if(!vo)vs_count=vs_count+1;
     end
     if(samples!=105000 || visible!=76800 || hs_count!=12600 || vs_count!=400)
       $fatal(1,"contract coverage mismatch");
     $display("RESULT functional_proposal_only=1 rgb_codes=256 samples=%0d visible=%0d hsync=%0d vsync=%0d failures=0",samples,visible,hs_count,vs_count);
     $finish;
   end
 end
 initial begin #20000000;$fatal(1,"contract watchdog");end
endmodule
