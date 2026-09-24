module tb_experimental_irq_entry;
 logic clk=0,reset=1,irq_accept=0,iret_request=0,mem_ready=1;
 logic [15:0] irq_vector=16'h8000,cpu_pc=16'h1234,cpu_sp=16'hff00;
 logic [7:0] cpu_flags=8'h05,mem_rdata=0; logic busy,mem_valid,mem_we,state_write,iret_complete;
 logic [15:0] mem_addr,next_pc,next_sp;logic [7:0] mem_wdata,next_flags;byte mem[0:65535];
 always #5 clk=~clk;
 educpu_experimental_irq_entry dut(.*);
 always @* mem_rdata = mem[mem_addr];
 always @(posedge clk) if(mem_valid && mem_we && mem_ready) mem[mem_addr] <= mem_wdata;
 task tick;begin @(posedge clk);#1;end endtask
 initial begin
  tick;reset=0;irq_accept=1;tick;irq_accept=0;
  wait(state_write); #1;
  if(next_pc!=16'h8000||next_sp!=16'hfefd) $fatal(1,"entry state");
  if(mem[16'hfeff]!=8'h12||mem[16'hfefe]!=8'h34||mem[16'hfefd]!=8'h05) $fatal(1,"entry stack");
  cpu_sp=16'hfefd;iret_request=1;tick;iret_request=0;
  wait(iret_complete); #1;
  if(!state_write||next_pc!=16'h1234||next_sp!=16'hff00||next_flags!=8'h05) $fatal(1,"iret");
  $display("PASS experimental IRQ entry/IRET sequencer");$finish;
 end
endmodule
