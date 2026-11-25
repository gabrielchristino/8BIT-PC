`timescale 1ns/1ps
module tb_hc191_negative;
  parameter integer CASE=0;
  reg clk=0,load_n=0,cten_n=1,down=0;
  reg [3:0] d=0;
  hc191_timing_monitor monitor(clk,load_n,cten_n,down,d);
  initial begin
    #300;
    case(CASE)
      0: begin load_n=1;#50;load_n=0;#10;load_n=1;end
      1: begin d=1;#1;load_n=1;end
      2: begin load_n=1;#10;clk=1;end
      3: begin load_n=1;#100;cten_n=0;#20;clk=1;end
      4: begin load_n=1;#1;d=1;end
      5: begin load_n=1;#100;cten_n=0;#100;clk=1;#1;cten_n=1;end
      6: begin load_n=1;#100;cten_n=0;#100;clk=1;#1;down=1;end
    endcase
    #100;$fatal(1,"NEGATIVE_NOT_DETECTED");
  end
endmodule
