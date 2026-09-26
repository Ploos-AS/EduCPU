module tb_experimental_irq_entry;
 logic clk=0,reset=1,irq_accept=0,iret_request=0,mem_ready=1;
 logic [15:0] irq_vector=16'h8000,cpu_pc=16'h1234,cpu_sp=16'hff00;
 logic [7:0] cpu_flags=8'h05,mem_rdata=0;
 logic busy,mem_valid,mem_we,state_write,iret_complete;
 logic [15:0] mem_addr,next_pc,next_sp;
 logic [7:0] mem_wdata,next_flags;
 logic [7:0] stack_feff=0,stack_fefe=0,stack_fefd=0;

 always #5 clk=~clk;
 educpu_experimental_irq_entry dut(.*);

 // The sequencer test only needs the three-byte interrupt frame. Keeping the
 // memory model explicit avoids simulator-dependent behavior from a 64 KiB
 // unpacked array with an asynchronous variable-index read.
 always_comb begin
  case(mem_addr)
   16'hfeff: mem_rdata=stack_feff;
   16'hfefe: mem_rdata=stack_fefe;
   16'hfefd: mem_rdata=stack_fefd;
   default:  mem_rdata=8'h00;
  endcase
 end

 always_ff @(posedge clk) begin
  if(mem_valid && mem_we && mem_ready) begin
   case(mem_addr)
    16'hfeff: stack_feff <= mem_wdata;
    16'hfefe: stack_fefe <= mem_wdata;
    16'hfefd: stack_fefd <= mem_wdata;
   endcase
  end
 end

 task tick; begin @(posedge clk); #1; end endtask

 initial begin
  tick; reset=0; irq_accept=1; tick; irq_accept=0;
  wait(busy); wait(!busy); #1;
  if(next_pc!=16'h8000||next_sp!=16'hfefd) $fatal(1,"entry state");
  if(stack_feff!=8'h12||stack_fefe!=8'h34||stack_fefd!=8'h05) begin
   $display("stack %02x %02x %02x",stack_feff,stack_fefe,stack_fefd);
   $fatal(1,"entry stack");
  end

  cpu_sp=16'hfefd; iret_request=1; tick; iret_request=0;
  wait(busy); wait(!busy); #1;
  if(!state_write||next_pc!=16'h1234||next_sp!=16'hff00||next_flags!=8'h05)
   $fatal(1,"iret");

  $display("PASS experimental IRQ entry/IRET sequencer");
  $finish;
 end
endmodule
