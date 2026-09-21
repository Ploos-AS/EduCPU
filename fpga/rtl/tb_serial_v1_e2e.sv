`timescale 1ns/1ps
module tb_serial_v1_e2e;
 localparam integer CPB=4; logic clk=0,reset=1,rx=1,tx; logic [7:0] rd;logic rv;
 logic lm,lv,lr,started,err,accepted,cv,cw,cr,mv,mw,mr,halted,trap,tv,tr; logic [15:0] la,ca,ma;logic [7:0] ld,cd,md,mrd,crd,td;
 logic pending;logic [15:0] aq;logic weq;logic [7:0] wdq;logic [7:0] mem[0:65535];integer i;
 always #5 clk=~clk;
 educpu_uart_rx #(.CLKS_PER_BIT(CPB)) urx(.clk,.reset,.rx,.data(rd),.data_valid(rv));
 educpu_serial_loader_v1 sl(.clk,.reset,.rx_data(rd),.rx_valid(rv),.load_mode(lm),.load_valid(lv),.load_addr(la),.load_data(ld),.load_ready(lr),.started,.protocol_error(err),.accepted);
 educpu_core cpu(.clk,.reset(reset|lm),.mem_rdata(crd),.mem_addr(ca),.mem_wdata(cd),.mem_we(cw),.mem_valid(cv),.mem_ready(cr),.halted,.trap);
 educpu_loader_mux mux(.load_mode(lm),.load_valid(lv),.load_addr(la),.load_data(ld),.load_ready(lr),.cpu_valid(cv),.cpu_we(cw),.cpu_addr(ca),.cpu_wdata(cd),.cpu_rdata(crd),.cpu_ready(cr),.mem_valid(mv),.mem_we(mw),.mem_addr(ma),.mem_wdata(md),.mem_rdata(mrd),.mem_ready(mr));
 educpu_loader_status st(.clk,.reset,.accepted,.protocol_error(err),.halted,.trap,.tx_ready(tr),.tx_valid(tv),.tx_data(td));
 educpu_uart_tx #(.CLKS_PER_BIT(CPB)) utx(.clk,.reset,.data(td),.valid(tv),.ready(tr),.tx);
 always_ff @(posedge clk) begin mr<=0;if(pending)begin if(weq)mem[aq]<=wdq;else mrd<=mem[aq];mr<=1;pending<=0;end else if(mv)begin aq<=ma;weq<=mw;wdq<=md;pending<=1;end end
 task send(input[7:0]b);integer k;begin rx=0;repeat(CPB)@(posedge clk);for(k=0;k<8;k=k+1)begin rx=b[k];repeat(CPB)@(posedge clk);end rx=1;repeat(CPB+2)@(posedge clk);end endtask
 task recv(output[7:0]b);integer k;begin @(negedge tx);repeat(CPB+CPB/2)@(posedge clk);for(k=0;k<8;k=k+1)begin b[k]=tx;repeat(CPB)@(posedge clk);end repeat(CPB)@(posedge clk);end endtask
 logic[7:0] a,b;
 initial begin
  #2000000;
  $display("DEBUG lm=%b started=%b err=%b accepted=%b halted=%b trap=%b tv=%b tr=%b tx=%b la=%h mem0=%h",lm,started,err,accepted,halted,trap,tv,tr,tx,la,mem[0]);\n  $fatal(1,"timeout waiting for protocol-v1 ACK/HALT");
 end
 initial begin pending=0;mr=0;mrd=0;for(i=0;i<65536;i=i+1)mem[i]=0;repeat(4)@(posedge clk);reset=0;
  fork
   begin recv(a); recv(b); end
   begin send(8'h55);send(8'haa);send(8'h01);send(8'h04);send(0);send(8'h11);send(0);send(8'h2a);send(1);send(8'h04);send(8'h48); end
  join
  if(a!==8'h06)$fatal(1,"missing ACK");if(b!==8'h48)$fatal(1,"missing HALT");if(err||trap)$fatal(1,"v1 execution failed");
  $display("EduCPU UART v1 bidirectional end-to-end PASS");$finish;
 end
endmodule
