// Minimal 8N1 UART transmitter.
module educpu_uart_tx #(parameter integer CLKS_PER_BIT=104)(
 input logic clk,input logic reset,input logic [7:0] data,input logic valid,
 output logic ready,output logic tx
);
 logic [9:0] shreg; integer count; logic [3:0] bits;
 assign ready=(bits==0); assign tx=(bits==0)?1'b1:shreg[0];
 always_ff @(posedge clk) begin
  if(reset) begin shreg<=10'h3ff;count<=0;bits<=0;end
  else if(bits==0) begin
   if(valid) begin shreg<={1'b1,data,1'b0};bits<=10;count<=CLKS_PER_BIT-1;end
  end else if(count==0) begin
   shreg<={1'b1,shreg[9:1]};bits<=bits-1'b1;count<=CLKS_PER_BIT-1;
  end else count<=count-1;
 end
endmodule
