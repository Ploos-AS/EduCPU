module tb_experimental_microsequencer;
 logic clk=0,reset=1,dispatch=0;logic [7:0] ir=0;logic fetch_phase,valid;logic [3:0] micro_pc;logic [23:0] control_word;
 educpu_experimental_microsequencer dut(.*);
 always #5 clk=~clk;
 initial begin
  #12;reset=0;
  #10;if(!fetch_phase||micro_pc!=1||!valid)$fatal(1,"fetch step 1");
  ir=8'h00;dispatch=1;#10;dispatch=0;
  if(fetch_phase||micro_pc!=0||!valid)$fatal(1,"NOP dispatch");
  #10;if(!fetch_phase||micro_pc!=0)$fatal(1,"NOP return fetch");
  #20;ir=8'h01;dispatch=1;#10;dispatch=0;
  if(fetch_phase||!valid)$fatal(1,"HALT dispatch");
  #20;if(fetch_phase||micro_pc!=0)$fatal(1,"HALT must hold");
  $display("M10.3 experimental microsequencer PASS");$finish;
 end
endmodule
