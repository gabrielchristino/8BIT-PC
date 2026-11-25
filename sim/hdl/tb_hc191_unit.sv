`timescale 1ns/1ps
module tb_hc191_unit;
  reg clk=0,load_n=1,cten_n=1,down=0;
  reg [3:0] d=0;
  wire [3:0] q;
  wire terminal;
  integer value,direction,inhibited,level,count_cases=0,load_cases=0;
  reg [3:0] expected;
  sn74hc191_model dut(clk,load_n,cten_n,down,d,q,terminal);
  initial begin
    for(value=0;value<16;value=value+1)
      for(direction=0;direction<2;direction=direction+1)
        for(inhibited=0;inhibited<2;inhibited=inhibited+1) begin
          clk=0;load_n=0;d=value;#1;
          if(q!==value[3:0]) $fatal(1,"Preset truth table failed");
          load_n=1;cten_n=inhibited;down=direction;#1;clk=1;#1;
          expected=inhibited ? value : direction ? value-1 : value+1;
          if(q!==expected) $fatal(1,"Counting truth table failed");
          if(terminal!==(direction ? expected==0 : expected==15))
            $fatal(1,"MAX/MIN truth table failed");
          count_cases=count_cases+1;
        end
    for(level=0;level<2;level=level+1) begin
      clk=level;load_n=0;cten_n=0;
      for(value=0;value<16;value=value+1) begin
        d=value;#1;
        if(q!==value[3:0]) $fatal(1,"LOAD is not transparent without CLK");
        load_cases=load_cases+1;
      end
      load_n=1;#1;
      if(q!==4'hf) $fatal(1,"Releasing LOAD invented a count edge");
    end
    load_n=0;d=4'h9;clk=0;#1;clk=1;#1;
    if(q!==4'h9) $fatal(1,"LOAD did not override count");
    $display("UNIT count_cases=%0d transparent_load_cases=%0d priority_cases=1 failures=0",
             count_cases,load_cases);
    $finish;
  end
endmodule
