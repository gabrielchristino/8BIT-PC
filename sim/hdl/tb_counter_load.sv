`timescale 1ns/1ps
module tb_counter_load;
    parameter integer TIMED=0;
    reg clk=0,reset_n=1,wait_in=0,bus_idle=1,commit=0,down=0,load_request=0;
    reg [15:0] load_data=0;
    wire [15:0] q,q_initial8000;
    wire ready,done,load_n,permit;
    integer checks=0,load_cases=0,reset_cases=0,gate_cases=0,v,s,p,k;
    reg [15:0] expected;
    counter_load_candidate #(.TIMED(TIMED)) dut
      (clk,reset_n,wait_in,bus_idle,commit,down,load_request,load_data,
       q,ready,done,load_n,permit);
    // Only an initialization probe for 8000h, not an integrated SP implementation.
    counter_load_candidate #(.INITIAL_VALUE(16'h8000),.TIMED(TIMED)) init8000
      (clk,reset_n,wait_in,bus_idle,commit,down,load_request,load_data,
       q_initial8000, , , , );
    always #500 clk=~clk;
    task check_value(input [15:0] wanted);
      begin
        if(q!==wanted || q_initial8000!==wanted)
          $fatal(1,"Value mismatch expected=%h X=%h probe=%h time=%t",wanted,q,q_initial8000,$time);
        checks=checks+1;
      end
    endtask
    task load_value(input [15:0] value);
      begin
        wait(ready);@(posedge clk);#200;
        load_data=value;load_request=1;
        wait(dut.state==3);@(posedge clk);#200;
        // Input bus may change after the capture hold time; saved payload must not.
        load_data=~value;
        wait(done);#200;check_value(value);
        @(posedge clk);#200;load_request=0;
        wait(ready);#200;check_value(value);
        load_cases=load_cases+1;
      end
    endtask
    task count_once(input bit direction,input [15:0] wanted);
      begin
        @(posedge clk);#200;down=direction;commit=1;
        @(posedge clk);#200;check_value(wanted);commit=0;
      end
    endtask
    initial begin
      if($test$plusargs("vcd")) begin
        $dumpfile("counter_load.vcd");$dumpvars(0,tb_counter_load);
      end
      #20;reset_n=0;#200;
      if(q!==0 || q_initial8000!==16'h8000 || permit!==0)
        $fatal(1,"Initial preset failure");
      #1000;reset_n=1;wait(ready);#200;
      if(q!==0 || q_initial8000!==16'h8000) $fatal(1,"Startup transition counted");

      for(v=0;v<65536;v=v+1) begin
        load_value(v[15:0]);
        count_once(0,(v+1)&16'hffff);
        count_once(1,v[15:0]);
        @(posedge clk);#200;wait_in=1;commit=1;
        repeat(2) begin @(posedge clk);#200;check_value(v[15:0]);end
        commit=0;wait_in=0;
      end

      // A held load request is consumed once, even if external data changes.
      load_value(16'ha55a);
      @(posedge clk);#200;load_request=1;load_data=16'h1234;
      wait(done);#200;check_value(16'h1234);load_data=16'hdead;
      repeat(4) begin @(posedge clk);#200;check_value(16'h1234);end
      load_request=0;@(posedge clk);#200;

      // Requests remain pending during WAIT or an outstanding bus transaction.
      for(k=0;k<2;k=k+1) begin
        @(posedge clk);#200;
        wait_in=(k==0);bus_idle=(k==0);load_data=16'hbeef;load_request=1;
        repeat(3) begin @(posedge clk);#200;check_value(16'h1234);end
        wait_in=0;bus_idle=1;wait(done);#200;check_value(16'hbeef);
        load_request=0;wait(ready);#200;
        load_value(16'h1234);gate_cases=gate_cases+1;
      end

      // Abort a load at each runtime state and four positions in its cycle.
      for(s=2;s<=6;s=s+1) for(p=0;p<4;p=p+1) begin
        wait(ready);@(posedge clk);#200;load_request=1;load_data=16'hffff;
        if(s!=2) wait(dut.state==s);
        #(20+100*p);reset_n=0;load_request=0;commit=0;#200;
        if(q!==0 || q_initial8000!==16'h8000 || permit!==0 || ready!==0)
          $fatal(1,"Reset failure state=%d phase=%d",s,p);
        #1100;reset_n=1;wait(ready);#200;
        if(q!==0 || q_initial8000!==16'h8000) $fatal(1,"Reset release counted");
        reset_cases=reset_cases+1;
      end
      $display("RESULT timed=%0d loads=%0d value_checks=%0d reset_cases=%0d gate_cases=%0d failures=0",
                TIMED,load_cases,checks,reset_cases,gate_cases);
      $finish;
    end
    initial begin #2000000000;$fatal(1,"Bench timeout");end
endmodule
