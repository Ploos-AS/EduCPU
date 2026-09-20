`timescale 1ns/1ps
module tb_serial_e2e;
  localparam integer CPB=4;
  logic clk=0, reset=1, rx=1;
  logic [7:0] rx_data; logic rx_valid;
  logic load_mode,load_valid,load_ready,started,err;
  logic [15:0] load_addr; logic [7:0] load_data;
  logic cpu_valid,cpu_we,cpu_ready,halted,trap;
  logic [15:0] cpu_addr,mem_addr; logic [7:0] cpu_wdata,cpu_rdata,mem_wdata,mem_rdata;
  logic mem_valid,mem_we,mem_ready,pending; logic [15:0] aq; logic weq; logic [7:0] wdq;
  logic [7:0] mem[0:65535]; integer i;
  always #5 clk=~clk;
  educpu_uart_rx #(.CLKS_PER_BIT(CPB)) urx(.clk(clk),.reset(reset),.rx(rx),.data(rx_data),.data_valid(rx_valid));
  educpu_serial_loader sl(.clk(clk),.reset(reset),.rx_data(rx_data),.rx_valid(rx_valid),
    .load_mode(load_mode),.load_valid(load_valid),.load_addr(load_addr),.load_data(load_data),
    .load_ready(load_ready),.started(started),.protocol_error(err));
  educpu_core cpu(.clk(clk),.reset(reset|load_mode),.mem_rdata(cpu_rdata),.mem_addr(cpu_addr),
    .mem_wdata(cpu_wdata),.mem_we(cpu_we),.mem_valid(cpu_valid),.mem_ready(cpu_ready),.halted(halted),.trap(trap));
  educpu_loader_mux mux(.load_mode(load_mode),.load_valid(load_valid),.load_addr(load_addr),.load_data(load_data),
    .load_ready(load_ready),.cpu_valid(cpu_valid),.cpu_we(cpu_we),.cpu_addr(cpu_addr),.cpu_wdata(cpu_wdata),
    .cpu_rdata(cpu_rdata),.cpu_ready(cpu_ready),.mem_valid(mem_valid),.mem_we(mem_we),.mem_addr(mem_addr),
    .mem_wdata(mem_wdata),.mem_rdata(mem_rdata),.mem_ready(mem_ready));
  always_ff @(posedge clk) begin
    mem_ready<=0;
    if(pending) begin if(weq) mem[aq]<=wdq; else mem_rdata<=mem[aq]; mem_ready<=1; pending<=0; end
    else if(mem_valid) begin aq<=mem_addr;weq<=mem_we;wdq<=mem_wdata;pending<=1; end
  end
  task uart_byte(input [7:0] b); integer k; begin
    rx=0; repeat(CPB) @(posedge clk);
    for(k=0;k<8;k=k+1) begin rx=b[k]; repeat(CPB) @(posedge clk); end
    rx=1; repeat(CPB) @(posedge clk); repeat(CPB) @(posedge clk);
  end endtask
  initial begin
    pending=0;mem_ready=0;mem_rdata=0;for(i=0;i<65536;i=i+1)mem[i]=0;
    repeat(4)@(posedge clk); reset=0; repeat(2)@(posedge clk);
    uart_byte(8'h55);uart_byte(8'haa);uart_byte(8'h04);uart_byte(8'h00);
    uart_byte(8'h11);uart_byte(8'h00);uart_byte(8'h2a);uart_byte(8'h01);
    repeat(200) begin @(posedge clk);
      if(err) $fatal(1,"serial protocol error");
      if(trap) $fatal(1,"loaded program trapped");
      if(halted) begin
        if(mem[0]!==8'h11||mem[1]!==8'h00||mem[2]!==8'h2a||mem[3]!==8'h01) $fatal(1,"loaded image mismatch");
        $display("EduCPU UART-to-CPU end-to-end PASS");$finish;
      end
    end
    $fatal(1,"UART-loaded program did not halt");
  end
endmodule
