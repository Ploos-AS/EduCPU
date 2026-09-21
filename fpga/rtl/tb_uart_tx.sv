module tb_uart_tx;
 logic clk=0,reset=1,valid=0,ready,tx; logic [7:0] data=0; integer i; logic [7:0] got;
 educpu_uart_tx #(.CLKS_PER_BIT(4)) d(.clk,.reset,.data,.valid,.ready,.tx);
 always #5 clk=~clk;
 initial begin
  repeat(2) @(posedge clk); reset=0; @(negedge clk); data=8'h48;valid=1; @(negedge clk);valid=0;
  wait(tx==0); repeat(2) @(posedge clk);
  for(i=0;i<8;i=i+1) begin repeat(4) @(posedge clk); got[i]=tx; end
  repeat(4) @(posedge clk); if(tx!==1'b1)$fatal(1,"bad stop bit");
  if(got!==8'h48)$fatal(1,"UART TX byte mismatch");
  $display("EduCPU UART TX PASS");$finish;
 end
endmodule
