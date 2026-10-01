module tb_experimental_irq_diff;
 logic clk=0,reset=1,mem_ready=1,irq_accept=0; logic [15:0] irq_vector=16'h8000;
 logic [7:0] mem[0:65535],mem_rdata; logic [15:0] mem_addr; logic [7:0] mem_wdata;
 logic mem_we,mem_valid,halted,trap,instruction_boundary,iret_complete; integer i,n;
 always #5 clk=~clk; assign mem_rdata=mem[mem_addr];
 always @(posedge clk) if(mem_valid&&mem_we) mem[mem_addr]=mem_wdata;
 logic [7:0] io_port,io_wdata,io_rdata=0; logic io_we,io_valid,io_ready=1;\n educpu_experimental_core dut(.*);
 task tick; begin @(posedge clk); #1; end endtask
 initial begin
  for(i=0;i<65536;i=i+1)mem[i]=0;
  mem[0]=8'h00; mem[1]=8'h01; mem[16'h8000]=8'hf0;
  tick;reset=0;tick;irq_accept=1;tick;irq_accept=0;
  for(n=0;n<30&&!halted&&!trap;n=n+1)tick;
  $display("pc=%04x sp=%04x flags=%02x halted=%0d trap=%0d frame=%02x,%02x,%02x",dut.pc,dut.sp,dut.flags,halted,trap,mem[16'hfeff],mem[16'hfefe],mem[16'hfefd]);
  if(!halted||trap)$fatal(1,"did not reach HALT"); $finish;
 end
endmodule
