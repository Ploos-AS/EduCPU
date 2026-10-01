module tb_experimental_io_diff;
 logic clk=0,reset=1,mem_ready=1,irq_accept=0; logic [15:0] irq_vector=0;
 logic [7:0] mem[0:65535],mem_rdata; logic [15:0] mem_addr; logic [7:0] mem_wdata;
 logic mem_we,mem_valid,halted,trap,instruction_boundary,iret_complete;
 logic [7:0] io_port,io_wdata,io_rdata; logic io_we,io_valid,io_ready=1;
 integer i,n,tx_count=0; logic [7:0] tx0_port,tx0_value,tx1_port,tx1_value,tx2_port,tx2_value;
 always #5 clk=~clk; assign mem_rdata=mem[mem_addr];
 always @(posedge clk) if(mem_valid&&mem_we&&mem_ready) mem[mem_addr]=mem_wdata;
 always_comb begin
  if(io_port==8'h10) io_rdata=8'hA5; else io_rdata=8'h00;
 end
 always @(posedge clk) if(io_valid&&io_ready) begin
  if(tx_count==0) begin tx0_port<=io_port;tx0_value<=io_we?io_wdata:io_rdata;end
  if(tx_count==1) begin tx1_port<=io_port;tx1_value<=io_we?io_wdata:io_rdata;end
  if(tx_count==2) begin tx2_port<=io_port;tx2_value<=io_we?io_wdata:io_rdata;end
  tx_count<=tx_count+1;
 end
 educpu_experimental_core dut(.*);
 task tick; begin @(posedge clk); #1; end endtask
 initial begin
  for(i=0;i<65536;i=i+1)mem[i]=0;
  // IN R2,10; OUT 20,R2; IN R3,77(unmapped); HALT
  mem[0]=8'hE0;mem[1]=8'h02;mem[2]=8'h10;
  mem[3]=8'hE1;mem[4]=8'h20;mem[5]=8'h02;
  mem[6]=8'hE0;mem[7]=8'h03;mem[8]=8'h77;mem[9]=8'h01;
  tick;reset=0;
  for(n=0;n<40&&!halted&&!trap;n=n+1)tick;
  $display("pc=%04x sp=%04x flags=%02x r2=%02x r3=%02x halted=%0d trap=%0d tx=%0d p0=%02x v0=%02x p1=%02x v1=%02x p2=%02x v2=%02x",dut.pc,dut.sp,dut.flags,dut.r[2],dut.r[3],halted,trap,tx_count,tx0_port,tx0_value,tx1_port,tx1_value,tx2_port,tx2_value);
  if(!halted||trap||tx_count!=3)$fatal(1,"IO differential program failed");$finish;
 end
endmodule
