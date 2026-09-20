`timescale 1ns/1ps
module tb_serial_loader;
 logic clk=0,reset=1,rx_valid=0,load_ready=0; logic[7:0]rx_data,load_data;
 logic load_mode,load_valid,started,err; logic[15:0]load_addr; logic[7:0] mem[0:15];
 always #5 clk=~clk;
 educpu_serial_loader dut(.clk(clk),.reset(reset),.rx_data(rx_data),.rx_valid(rx_valid),
  .load_mode(load_mode),.load_valid(load_valid),.load_addr(load_addr),.load_data(load_data),
  .load_ready(load_ready),.started(started),.protocol_error(err));
 always_comb begin
   load_ready = load_valid;
 end
 always_ff @(posedge clk) begin
   if(load_valid) mem[load_addr]<=load_data;
 end
 task send(input[7:0] b); begin rx_data=b;rx_valid=1;@(posedge clk);rx_valid=0;repeat(2)@(posedge clk);end endtask
 initial begin
  repeat(2)@(posedge clk);reset=0;
  send(8'h55);send(8'haa);send(8'h04);send(8'h00);
  send(8'h11);send(8'h00);send(8'h2a);send(8'h01);
  begin : wait_done
    integer timeout;
    for(timeout=0; timeout<20 && !started; timeout=timeout+1) @(posedge clk);
    if(!started) $fatal(1,"loader did not release CPU");
  end
  if(err) $fatal(1,"protocol error");
  if(mem[0]!==8'h11||mem[1]!==8'h00||mem[2]!==8'h2a||mem[3]!==8'h01) $fatal(1,"payload mismatch");
  $display("EduCPU serial loader protocol PASS");$finish;
 end
endmodule
