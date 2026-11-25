// GENERATED NET-08 base SHA256 20a9f9ae40870d242debed8514f0b32c016d7d282159f3ac434cccc6c39d5f26
// GENERATED NET-07 base SHA256 1ebb18921f8c9604b0b0502c285cf54d6135610b242f2cc2f50c4f34fdbe5db0
// GENERATED NET-06 base SHA256 9a563464cb666de1f5a50ec848c9b16bf7c1b05a9e1609a22de467fb9c21e641
// GENERATED NET-05 base SHA256 9276f7ea2f993c962a5e9c5cdc0973f7eb028b64a875f9ab648ae5767507ab00
// GENERATED NET-04 source SHA256 d0dbe9984de317b513e1f3592b9d7a2c4dbbbe8645469a063ca53c6dc9426b7b
// GENERATED NET-03; source SHA256 7d75e8deb1a1116004189917e8fdab97f42df595e4db6fa76d83c54d787e5432
// GENERATED NET-02 adapter. Source SHA256: 16767753b645234a563d7839c898115dac0444b53672688db15854b30637e407
`timescale 1ns/1ps
// RTL-01: executable ROM/datapath contract, NOT a discrete-IC netlist.
module isa1_cpu #(parameter ROM_PREFIX="control_lane", parameter integer USE_HC191=0) (
 input wire clk, reset_n, power_good, run, boot,
 output wire request, write_enable,
 output wire [15:0] address,
 output wire [7:0] write_data,
 input wire acknowledge, input wire [7:0] read_data,
 output wire [15:0] pc, output wire [15:0] sp,x, output wire [7:0] a,b,
 output wire z,c,halted,retired, output wire [1:0] fault,
 output wire [12:0] control_address, output wire [31:0] control_word
);
 wire fetch_bank; wire [3:0] microstep; wire [7:0] ir; wire [7:0] mdr;
 wire control_ready,execute_clk,dispatch;
 wire [15:0] ea;
 wire [7:0] dst_n_bus; wire [3:0] flags_n_bus;
 wire bus_start; wire bus_ready,bus_done;
 localparam EXEC=0, RESPONSE=1, DROP=2, X_LOAD=3;
 wire [1:0] state;
 reg [15:0] x_register;
 wire x_load_request;
 wire stack_checked;
 wire [15:0] chip_x;
 wire x_ready,x_done;
 wire x_count; wire [7:0] addr_n_bus; wire [3:0] mem_n_bus,x_n_bus;
 assign x=USE_HC191?chip_x:x_register;
 wire safe = reset_n && power_good;
 // Bus qualifiers are driven by the exported IC netlist.
 // Control address/word now come from the exported ROM/sequencer netlist.
 wire [2:0] addr_sel=control_word[2:0], src=control_word[5:3], dst=control_word[8:6];
 wire [1:0] mem=control_word[10:9], sp_op=control_word[15:14], x_op=control_word[17:16];
 wire [2:0] pc_op=control_word[13:11];
 wire [3:0] alu=control_word[21:18];
 wire [1:0] flags=control_word[23:22];
 wire [15:0] stack_sum;
 wire sp_down,sp_update;
 stack_bank_netlist stack_bank(clk,safe,sp_update,sp_down,sp,stack_sum);
 // A disabled configuration has no simulated chip clock activity.
 counter_word_candidate x_bank(USE_HC191?clk:1'b0,safe,1'b0,1'b1,x_count,x_op==3,x_load_request,
                              ea,chip_x,x_ready,x_done, , );
 wire [7:0] result,value; wire carry,alu_zero;
 alu_bank_netlist alu_bank(a,b,alu,c,result,carry,alu_zero);
 wire [15:0] selected_address; wire [7:0] pc_n_bus;
 wire execute_pulse,seq_advance;
 microcode_bank_netlist #(.ROM_PREFIX(ROM_PREFIX)) micro_bank(
   .clk(clk),.reset_n(reset_n),.power_good(power_good),.advance_req(seq_advance),.execute_pulse(execute_pulse),.opcode(mdr),
   .control_ready(control_ready),.execute_clk(execute_clk),.dispatch(dispatch),.fetch(fetch_bank),.step(microstep),.ir(ir),
   .rom_address(control_address),.control_word(control_word),.sp_update(sp_update),.sp_down(sp_down),.dst_n(dst_n_bus),.flags_n(flags_n_bus),.pc_n(pc_n_bus),.addr_n(addr_n_bus),.mem_n(mem_n_bus),.x_n(x_n_bus));
 register_bank_netlist register_bank(execute_clk,reset_n,power_good,execute_pulse && control_ready,
   src,dst_n_bus,flags_n_bus,pc,mdr,result,carry,a,b,value,ea,z,c);
 transaction_bank_netlist bus_bank(clk,reset_n,power_good,bus_start,mem==2,acknowledge,
   selected_address,value,read_data,bus_ready,bus_done,request,write_enable,address,write_data,mdr, );
 address_bank_netlist address_bank(execute_clk,reset_n,power_good,execute_pulse && control_ready,
   addr_sel,pc_n_bus,z,ea,x,sp,stack_sum,pc,selected_address);
 execution_bank_netlist execution_bank(execute_clk,reset_n,power_good,run,control_ready,
   !USE_HC191 || x_ready,x_done,USE_HC191!=0,boot,bus_ready,bus_done,dispatch,control_word[24],control_word[25],
   ir,addr_n_bus,mem_n_bus,x_n_bus,sp,execute_pulse,seq_advance,bus_start,x_load_request,x_count,stack_checked,halted,retired,fault,state);
 // Only the alternative ideal-X reference remains procedural here.
 always @(posedge execute_clk or negedge safe)begin
   if(!safe)x_register<=0;
   else if(!USE_HC191 && execute_pulse && control_ready)case(x_op)
     1:x_register<=ea;2:x_register<=x+16'd1;3:x_register<=x-16'd1;
   endcase
 end
endmodule
