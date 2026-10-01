module tb_experimental_core_io;
 logic clk=0,reset=1,mem_ready=1,irq_accept=0; logic [15:0] irq_vector=0;
 logic [7:0] mem[0:65535],mem_rdata; logic [15:0] mem_addr; logic [7:0] mem_wdata;
 logic mem_we,mem_valid,halted,trap,instruction_boundary,iret_complete;
 logic [7:0] io_port,io_wdata,io_rdata=8'hA5; logic io_we,io_valid,io_ready=0;
 integer n; always #5 clk=~clk; assign mem_rdata=mem[mem_addr];
 always @(posedge clk) if(mem_valid&&mem_we&&mem_ready) mem[mem_addr]=mem_wdata;
 educpu_experimental_core dut(.*);
 task tick; begin @(posedge clk); #1; end endtask
 initial begin
  // IN R2,10; OUT 20,R2; HALT
  mem[0]=8'hE0; mem[1]=8'h02; mem[2]=8'h10;
  mem[3]=8'hE1; mem[4]=8'h20; mem[5]=8'h02; mem[6]=8'h01;
  tick; reset=0;
  for(n=0;n<10&&!io_valid;n=n+1) tick;
  if(!io_valid||io_we||io_port!==8'h10) $fatal(1,"IN bus request");
  if(mem_valid) $fatal(1,"memory bus active during IO wait");
  repeat(3) begin
   if(!io_valid||io_we||io_port!==8'h10) $fatal(1,"IN request not stable");
   tick;
  end
  if(dut.r[2]!==8'h00) $fatal(1,"IN committed before ready");
  io_ready=1; tick; io_ready=0;
  if(dut.r[2]!==8'hA5) $fatal(1,"IN value not committed");
  for(n=0;n<10&&!io_valid;n=n+1) tick;
  if(!io_valid||!io_we||io_port!==8'h20||io_wdata!==8'hA5) $fatal(1,"OUT bus request");
  repeat(2) begin
   if(!io_valid||!io_we||io_port!==8'h20||io_wdata!==8'hA5) $fatal(1,"OUT request not stable");
   tick;
  end
  io_ready=1; tick; io_ready=0;
  for(n=0;n<5&&!halted;n=n+1) tick;
  if(!halted||trap) $fatal(1,"program did not HALT cleanly");
  $display("PASS experimental IO wait-state handshake"); $finish;
 end
endmodule
