module tb_experimental_irq;
 logic clk=0,reset=1,irq_request=0,instruction_boundary=0,cpu_trap=0,iret_complete=0;
 logic [15:0] irq_vector=16'h8000;
 logic irq_pending,irq_enabled,in_interrupt,irq_accept;
 logic [15:0] accepted_vector;
 always #5 clk=~clk;
 educpu_experimental_irq dut(.*);

 task tick; begin @(posedge clk); #1; end endtask
 initial begin
   tick; reset=0; tick;
   if (!irq_enabled || irq_pending || in_interrupt) $fatal(1,"bad reset state");

   irq_request=1; tick; irq_request=0;
   if (!irq_pending || irq_accept) $fatal(1,"IRQ must wait for boundary");

   instruction_boundary=1; tick; instruction_boundary=0;
   if (!irq_accept || !in_interrupt || irq_enabled || irq_pending) $fatal(1,"IRQ not accepted");
   if (accepted_vector != 16'h8000) $fatal(1,"wrong vector");

   irq_request=1; tick; irq_request=0;
   if (!irq_pending || !in_interrupt) $fatal(1,"nested IRQ must remain pending");

   iret_complete=1; tick; iret_complete=0;
   if (in_interrupt || !irq_enabled || !irq_pending) $fatal(1,"IRET state restore failed");

   cpu_trap=1; instruction_boundary=1; tick;
   if (irq_accept || !irq_pending) $fatal(1,"trapped CPU accepted IRQ");
   $display("PASS experimental IRQ boundary");
   $finish;
 end
endmodule
