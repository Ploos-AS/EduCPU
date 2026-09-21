// Convert loader/CPU events into protocol-v1 status bytes.
module educpu_loader_status(
 input logic clk,input logic reset,input logic accepted,input logic protocol_error,
 input logic halted,input logic trap,input logic tx_ready,
 output logic tx_valid,output logic [7:0] tx_data
);
 logic old_err,old_halt,old_trap;
 always_ff @(posedge clk) begin
  if(reset) begin tx_valid<=0;tx_data<=0;old_err<=0;old_halt<=0;old_trap<=0;end
  else begin
   tx_valid<=0;
   if(tx_ready) begin
    if(accepted) begin tx_data<=8'h06;tx_valid<=1;end
    else if(protocol_error&&!old_err) begin tx_data<=8'h15;tx_valid<=1;end
    else if(trap&&!old_trap) begin tx_data<=8'h54;tx_valid<=1;end
    else if(halted&&!old_halt) begin tx_data<=8'h48;tx_valid<=1;end
   end
   old_err<=protocol_error;old_halt<=halted;old_trap<=trap;
  end
 end
endmodule
