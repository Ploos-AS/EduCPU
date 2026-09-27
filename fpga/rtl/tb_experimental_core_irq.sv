module tb_experimental_core_irq;
 logic clk=0,reset=1,mem_ready=1,irq_accept=0; logic [15:0] irq_vector=16'h8000;
 logic [7:0] mem_rdata; logic [15:0] mem_addr; logic [7:0] mem_wdata; logic mem_we,mem_valid,halted,trap,instruction_boundary,iret_complete;
 byte mem[0:65535]; always #5 clk=~clk; assign mem_rdata=mem[mem_addr];
 always @(posedge clk) if(mem_valid&&mem_we&&mem_ready) mem[mem_addr]=mem_wdata;
 educpu_experimental_core dut(.*);
 task tick; begin @(posedge clk); #1; end endtask
 integer n;
 initial begin
  mem[0]=8'h00; mem[1]=8'h01; // NOP; HALT
  mem[16'h8000]=8'hf0;         // IRET
  tick; reset=0; tick;
  // Accept between instructions with architectural return PC=1.
  irq_accept=1; tick; irq_accept=0;
  for(n=0;n<20 && !iret_complete;n=n+1) tick;
  if(!iret_complete) $fatal(1,"IRET did not complete");
  if(dut.pc!==16'h0001 || dut.sp!==16'hff00) $fatal(1,"return state pc=%h sp=%h",dut.pc,dut.sp);
  if(mem[16'hfeff]!==8'h00 || mem[16'hfefe]!==8'h01 || mem[16'hfefd]!==8'h00) $fatal(1,"IRQ frame");
  tick;
  if(!halted || trap) $fatal(1,"baseline HALT after IRET");
  $display("PASS integrated experimental IRQ/IRET core"); $finish;
 end
endmodule
