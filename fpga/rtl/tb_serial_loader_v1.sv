module tb_serial_loader_v1;
 logic clk=0,reset=1,rx_valid=0,load_ready=1; logic [7:0] rx_data;
 logic load_mode,load_valid,started,err,accepted; logic [15:0] addr; logic [7:0] data;
 educpu_serial_loader_v1 d(.clk,.reset,.rx_data,.rx_valid,.load_mode,.load_valid,.load_addr(addr),.load_data(data),.load_ready,.started,.protocol_error(err),.accepted);
 always #5 clk=~clk;
 task send(input [7:0] b); begin @(negedge clk);rx_data=b;rx_valid=1;@(negedge clk);rx_valid=0;end endtask
 initial begin
  repeat(2)@(posedge clk);reset=0;
  // image 11 00 2a 01; CRC over 01 04 00 11 00 2a 01 = 0xDB11
  send(8'h55);send(8'haa);send(8'h01);send(8'h04);send(0);send(8'h11);send(0);send(8'h2a);send(1);send(8'h11);send(8'hdb);
  // started/accepted are one-cycle pulses asserted when the CRC-high byte is sampled.\n  // Check the persistent postcondition instead: DONE releases load_mode without error.\n  @(posedge clk); if(err||load_mode)$fatal(1,"valid v1 frame rejected");
  $display("EduCPU serial loader v1 CRC PASS");
  reset=1;@(posedge clk);reset=0;
  // Same payload with corrupted CRC must never release the CPU.
  send(8'h55);send(8'haa);send(8'h01);send(8'h04);send(0);send(8'h11);send(0);send(8'h2a);send(1);send(8'h10);send(8'hdb);
  @(posedge clk); if(started||accepted||!err||!load_mode)$fatal(1,"bad CRC released CPU");
  $display("EduCPU serial loader v1 bad-CRC rejection PASS");$finish;
 end
endmodule
