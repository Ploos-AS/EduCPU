module tb_loader_status;
 logic clk=0,reset=1,accepted=0,err=0,halted=0,trap=0,ready=1,valid; logic [7:0] data;
 educpu_loader_status d(.clk,.reset,.accepted,.protocol_error(err),.halted,.trap,.tx_ready(ready),.tx_valid(valid),.tx_data(data));
 always #5 clk=~clk;
 task pulse(input integer kind,input [7:0] expect); begin
   @(negedge clk); case(kind) 0:accepted=1;1:err=1;2:halted=1;3:trap=1;endcase
   @(posedge clk); #1; if(!valid||data!=expect)$fatal(1,"status mismatch");
   @(negedge clk); accepted=0;
 end endtask
 initial begin repeat(2)@(posedge clk);reset=0;
   pulse(0,8'h06); pulse(1,8'h15); pulse(2,8'h48); pulse(3,8'h54);
   $display("EduCPU loader status PASS");$finish;
 end
endmodule
