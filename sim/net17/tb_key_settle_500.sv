`timescale 1ns/1ps
module tb_key_settle_500;
 parameter integer TIMED=1,BYPASS_READY=0;
 reg clk=0,reset_n=1,request=0,write_request=0;
 reg [15:0] address=0;reg [7:0] write_data=0;
 always #79.445 clk=~clk;
 wire boot,eb,key_ready;wire [1:0] vb,row;tri [3:0] row_wires;tri [15:0] column_wires;
 reg [63:0] keys=1;
 genvar rr,cc;
 generate for(rr=0;rr<4;rr=rr+1)begin:R
   for(cc=0;cc<16;cc=cc+1)begin:C
     tranif1 contact(row_wires[rr],column_wires[cc],keys[rr*16+cc]);
   end
 end endgenerate
 wire ack,accept,armed,held_write,bus_active,owner,drive,oe_n,we_n,io_commit,read_capture;
 wire [15:0] held_address;wire [7:0] held_data,read_data,io_data,phase;
 wire [3:0] select,cs_n;wire [5:0] io_select;wire [14:0] ra,va,ea;
 wire [7:0] read_bus=select[3]?io_data:8'h9b;
 memory_decode_netlist #(.TIMED(TIMED)) decode(held_address,boot,eb,vb,1'b1,reset_n,select,io_select,ra,va,ea);
 keyboard_access_netlist #(.TIMED(TIMED)) controller(.clk(clk),.reset_n(reset_n),.power_good(1'b1),
   .request(request),.write_request(write_request),.vram_slot(1'b1),.key_ready(BYPASS_READY?1'b1:key_ready),
   .io_col_lo(io_select[4]),.io_col_hi(io_select[5]),.address(address),.write_data(write_data),.read_bus(read_bus),.select(select),
   .ack(ack),.accept(accept),.armed(armed),.held_write(held_write),.bus_active(bus_active),.vram_owner(owner),.data_drive(drive),
   .oe_n(oe_n),.we_n(we_n),.io_commit(io_commit),.read_capture(read_capture),.held_address(held_address),.held_data(held_data),.read_data(read_data),.cs_n(cs_n),.phase(phase));
 keyboard_500_netlist #(.TIMED(TIMED)) peripheral(clk,reset_n,reset_n,io_commit,io_select,held_data,row_wires,column_wires,boot,eb,vb,row,io_data,key_ready);
 integer tests=0,long_reads=0,short_accesses=0,cycles=0,k;realtime quiet_since=0,min_quiet=1e12;
 always @(negedge key_ready)quiet_since=$realtime;
 always @(posedge io_commit)if(io_select[3])quiet_since=$realtime;
 always @(posedge key_ready)if(reset_n && $realtime>2000)begin
   if($realtime-quiet_since<2000000)$fatal(1,"quiet timer became ready in less than 2ms");
   if($realtime-quiet_since<min_quiet)min_quiet=$realtime-quiet_since;
 end
 task wait_armed;
 begin cycles=0;while(!armed)begin @(negedge clk);cycles=cycles+1;if(cycles>100)$fatal(1,"arm timeout");end end
 endtask
 task transaction(input [15:0] a,input bit wr,input [7:0] data,input [7:0] expected,input bit long_wait);
 begin
   wait_armed();@(negedge clk);#30;address=a;write_request=wr;write_data=data;request=1;cycles=0;
   while(!ack)begin @(negedge clk);cycles=cycles+1;if(cycles>18000)$fatal(1,"settled-key ACK timeout");end
   #30;
   if(!wr && (a==16'ha011 || a==16'ha012) && !key_ready)$fatal(1,"column read acknowledged before settling");
   if(!wr && read_data!==expected)$fatal(1,"settled-key read mismatch addr=%h got=%h expected=%h",a,read_data,expected);
   if(long_wait)begin if(cycles<16000)$fatal(1,"quiet wait too short");long_reads=long_reads+1;end
   else begin if(cycles>80)$fatal(1,"non-column/ready access unnecessarily stalled");short_accesses=short_accesses+1;end
   request=0;wait_armed();tests=tests+1;
 end
 endtask
 initial begin
   #100;reset_n=0;#1000;reset_n=1;wait_armed();
   transaction(16'ha011,0,0,8'hfe,1);
   transaction(16'ha010,1,1,0,0);
   transaction(16'ha000,0,0,0,0);
   transaction(16'ha012,1,8'h99,0,0);
   transaction(16'ha011,0,0,8'hff,1);
   transaction(16'ha012,0,0,8'hff,0);
   transaction(16'ha010,1,0,0,0);
   transaction(16'ha012,0,0,8'hff,1);
   transaction(16'ha011,0,0,8'hfe,0);
   transaction(16'ha010,1,2,0,0);
   wait_armed();@(negedge clk);address=16'ha011;write_request=0;request=1;
   repeat(500)@(negedge clk);
   if(ack || key_ready)$fatal(1,"pending quiet read completed early");
   reset_n=0;#1000;
   if(ack || !we_n || io_commit)$fatal(1,"unsafe pending key read effects");
   @(negedge clk);#10;reset_n=1;
   repeat(20)@(negedge clk);
   if(ack || armed)$fatal(1,"stale held key request replayed");
   request=0;wait_armed();transaction(16'ha011,0,0,8'hfe,1);
   $display("RESULT timed=%0d transactions=%0d long_column_reads=%0d short_accesses=%0d reset_pending=1 min_quiet_ns=%0.3f failures=0",TIMED,tests,long_reads,short_accesses,min_quiet);$finish;
 end
 initial begin #20000000;$fatal(1,"settling watchdog");end
endmodule
