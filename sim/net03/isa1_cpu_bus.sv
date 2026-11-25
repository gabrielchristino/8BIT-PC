// GENERATED NET-03; source SHA256 7d75e8deb1a1116004189917e8fdab97f42df595e4db6fa76d83c54d787e5432
// GENERATED NET-02 adapter. Source SHA256: 16767753b645234a563d7839c898115dac0444b53672688db15854b30637e407
`timescale 1ns/1ps
// RTL-01: executable ROM/datapath contract, NOT a discrete-IC netlist.
module isa1_cpu #(parameter ROM_FILE="control.hex", parameter integer USE_HC191=0) (
 input wire clk, reset_n, power_good, run, boot,
 output wire request, write_enable,
 output wire [15:0] address,
 output wire [7:0] write_data,
 input wire acknowledge, input wire [7:0] read_data,
 output reg [15:0] pc, output wire [15:0] sp,x, output reg [7:0] a,b,
 output reg z,c,halted,retired, output reg [1:0] fault,
 output wire [12:0] control_address, output wire [31:0] control_word
);
 reg [31:0] rom [0:8191];
 initial $readmemh(ROM_FILE,rom);
 reg fetch_bank; reg [3:0] microstep; reg [7:0] ir; wire [7:0] mdr;
 reg [15:0] ea;
 reg bus_start; wire bus_ready,bus_done;
 localparam EXEC=0, RESPONSE=1, DROP=2, X_LOAD=3;
 reg [1:0] state;
 reg [15:0] x_register;
 reg x_load_request,x_load_completed;
 reg stack_checked;
 wire [15:0] chip_x;
 wire x_ready,x_done;
 wire x_count=USE_HC191 && state==EXEC && run && !halted && (x_op==2 || x_op==3);
 assign x=USE_HC191?chip_x:x_register;
 wire safe = reset_n && power_good;
 // Bus qualifiers are driven by the exported IC netlist.
 assign control_address = {fetch_bank,fetch_bank?8'b0:ir,microstep};
 assign control_word = rom[control_address];
 wire [2:0] addr_sel=control_word[2:0], src=control_word[5:3], dst=control_word[8:6];
 wire [1:0] mem=control_word[10:9], sp_op=control_word[15:14], x_op=control_word[17:16];
 wire [2:0] pc_op=control_word[13:11];
 wire [3:0] alu=control_word[21:18];
 wire [1:0] flags=control_word[23:22];
 wire [15:0] stack_sum;
 wire sp_down=addr_sel==5 || sp_op==2;
 wire sp_update=safe && run && !halted && state==EXEC &&
                (!USE_HC191 || x_ready) && mem==0 && (sp_op==1 || sp_op==2);
 stack_bank_netlist stack_bank(clk,safe,sp_update,sp_down,sp,stack_sum);
 // A disabled configuration has no simulated chip clock activity.
 counter_load_candidate x_bank(USE_HC191?clk:1'b0,safe,1'b0,1'b1,x_count,x_op==3,x_load_request,
                              ea,chip_x,x_ready,x_done, , );
 reg [8:0] arithmetic;
 reg [7:0] result, value;
 reg carry;
 reg [15:0] selected_address;
 transaction_bank_netlist bus_bank(clk,reset_n,power_good,bus_start,mem==2,acknowledge,
   selected_address,value,read_data,bus_ready,bus_done,request,write_enable,address,write_data,mdr, );
 always @* begin
   arithmetic=0; result=0; carry=c;
   case(alu)
     1: begin arithmetic={1'b0,a}+{1'b0,b};result=arithmetic[7:0];carry=arithmetic[8];end
     2,8: begin arithmetic={1'b0,a}+{1'b0,~b}+9'd1;result=arithmetic[7:0];carry=arithmetic[8];end
     3: result=a&b;
     4: result=a|b;
     5: result=a^b;
     6: begin result={a[6:0],1'b0};carry=a[7];end
     7: begin result={1'b0,a[7:1]};carry=a[0];end
     default: result=0;
   endcase
   case(src)
     1:value=a;2:value=pc[15:8];3:value=pc[7:0];4:value=mdr;5:value=result;
     default:value=0;
   endcase
   case(addr_sel)
     1:selected_address=pc;2:selected_address=ea;3:selected_address=x;
     4:selected_address=sp;5:selected_address=stack_sum;
     default:selected_address=0;
   endcase
 end
 task advance;
   begin
     if(fetch_bank && microstep==1) begin fetch_bank<=0;microstep<=0;ir<=value;stack_checked<=0;end
     else if(control_word[24]) begin fetch_bank<=1;microstep<=0;retired<=1;end
     else microstep<=microstep+1'b1;
   end
 endtask
 always @(posedge clk or negedge safe) begin
   if(!safe) begin
     pc<=0;x_register<=0;a<=0;b<=0;z<=0;c<=0;
     x_load_request<=0;x_load_completed<=0;
     stack_checked<=0;
     ea<=0;ir<=0;fetch_bank<=1;microstep<=0;
     halted<=0;fault<=0;retired<=0;bus_start<=0;state<=EXEC;
   end else begin
     retired<=0;
     case(state)
       RESPONSE: if(bus_done) begin bus_start<=0;state<=DROP;end
       DROP: if(bus_ready) begin state<=EXEC;advance();end
       X_LOAD: begin
         if(x_done)x_load_completed<=1;
         if(run && (x_done || x_load_completed))begin
           x_load_request<=0;x_load_completed<=0;state<=EXEC;advance();
         end
       end
       EXEC: if(run && !halted && (!USE_HC191 || x_ready)) begin
         if(mem!=0) begin
           if(addr_sel==5 && (sp==0 || sp>16'h8000 || (boot && sp<=16'h4000) ||
              (ir==8'h50 && !stack_checked && (sp<2 || (boot && sp<16'h4002)))))
             begin halted<=1;fault<=1;retired<=1;end
           else if(addr_sel==4 && (sp>=16'h8000 || (boot && sp<16'h4000) ||
                   (ir==8'h51 && !stack_checked && sp>16'h7ffe)))
             begin halted<=1;fault<=2;retired<=1;end
           else begin
             bus_start<=1;state<=RESPONSE;
             if(addr_sel==4 || addr_sel==5)stack_checked<=1;
           end
         end else begin
           case(dst)
             1:a<=value;2:b<=value;3:ea[7:0]<=value;
             4:ea[15:8]<=value;5:ir<=value;
           endcase
           if(flags!=0) z<=value==0;
           if(flags==2) c<=carry;
           case(pc_op)
             1:pc<=pc+16'd1;2:pc<=ea;
             3:if(z)pc<=ea;4:if(!z)pc<=ea;
           endcase
           // SP is stored by the pin-connected stack bank at this same edge.
           if(!USE_HC191)case(x_op)
             1:x_register<=ea;2:x_register<=x+16'd1;3:x_register<=x-16'd1;
           endcase
           if(control_word[25]) begin
             halted<=1;retired<=1;
             if(ir!=8'hff) fault<=3;
           end else if(USE_HC191 && x_op==1)begin
             x_load_request<=1;state<=X_LOAD;
           end else advance();
         end
       end
     endcase
   end
 end
endmodule
