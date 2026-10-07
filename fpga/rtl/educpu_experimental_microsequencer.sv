// M10.3 experimental microsequencer/control-store teaching RTL.
// Deliberately separate from the frozen educpu_core.sv.
module educpu_experimental_microsequencer(
 input logic clk,input logic reset,input logic [7:0] ir,input logic dispatch,
 output logic fetch_phase,output logic [3:0] micro_pc,
 output logic [23:0] control_word,output logic valid
);
 logic [7:0] opcode;
 function automatic [23:0] rom(input logic fetch,input logic [7:0] op,input logic [3:0] u);
  begin
   rom=24'h000000;
   if(fetch) begin
    case(u)
     0: rom=24'h100010; // PC -> memory-read
     1: rom=24'h260101; // MEM -> IR, PC++, dispatch
     default: rom=24'h000000;
    endcase
   end else begin
    case(op)
     8'h00: rom=(u==0)?24'h000002:24'h000000; // NOP -> fetch
     8'h01: rom=(u==0)?24'h000003:24'h000000; // HALT
     default: rom=24'h000000;
    endcase
   end
  end
 endfunction
 always_comb begin
  control_word=rom(fetch_phase,opcode,micro_pc);
  valid=fetch_phase ? (micro_pc<2) : ((opcode==8'h00||opcode==8'h01)&&micro_pc==0);
 end
 always_ff @(posedge clk) begin
  if(reset) begin fetch_phase<=1'b1;micro_pc<=0;opcode<=0;end
  else if(fetch_phase) begin
   if(micro_pc==0) micro_pc<=1;
   else if(dispatch) begin opcode<=ir;fetch_phase<=0;micro_pc<=0;end
  end else begin
   if(opcode==8'h00) begin fetch_phase<=1;micro_pc<=0;end
   else if(opcode==8'h01) micro_pc<=0;
  end
 end
endmodule
