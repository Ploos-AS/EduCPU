`timescale 1ns/1ps
module tb_loader;
    logic clk=0, reset=1, load_mode=1, load_valid=0;
    logic [15:0] load_addr; logic [7:0] load_data; logic load_ready;
    logic cpu_valid,cpu_we,cpu_ready,mem_valid,mem_we,mem_ready,halted,trap;
    logic [15:0] cpu_addr,mem_addr; logic [7:0] cpu_wdata,cpu_rdata,mem_wdata,mem_rdata;
    logic [7:0] memory [0:65535];
    logic pending; logic [15:0] addr_q; logic we_q; logic [7:0] wdata_q;
    integer i;
    always #5 clk=~clk;

    educpu_core cpu(.clk(clk),.reset(reset),.mem_rdata(cpu_rdata),.mem_addr(cpu_addr),
      .mem_wdata(cpu_wdata),.mem_we(cpu_we),.mem_valid(cpu_valid),.mem_ready(cpu_ready),
      .halted(halted),.trap(trap));
    educpu_loader_mux mux(.load_mode(load_mode),.load_valid(load_valid),.load_addr(load_addr),
      .load_data(load_data),.load_ready(load_ready),.cpu_valid(cpu_valid),.cpu_we(cpu_we),
      .cpu_addr(cpu_addr),.cpu_wdata(cpu_wdata),.cpu_rdata(cpu_rdata),.cpu_ready(cpu_ready),
      .mem_valid(mem_valid),.mem_we(mem_we),.mem_addr(mem_addr),.mem_wdata(mem_wdata),
      .mem_rdata(mem_rdata),.mem_ready(mem_ready));

    always_ff @(posedge clk) begin
      mem_ready<=0;
      if (pending) begin
        if (we_q) memory[addr_q]<=wdata_q; else mem_rdata<=memory[addr_q];
        mem_ready<=1; pending<=0;
      end else if (mem_valid) begin
        addr_q<=mem_addr; we_q<=mem_we; wdata_q<=mem_wdata; pending<=1;
      end
    end

    task load_byte(input [15:0] a,input [7:0] d);
      begin load_addr=a; load_data=d; load_valid=1; do @(posedge clk); while(!load_ready);
        load_valid=0; @(posedge clk); end
    endtask

    initial begin
      pending=0; mem_ready=0; mem_rdata=0;
      for(i=0;i<65536;i=i+1) memory[i]=0;
      repeat(2) @(posedge clk);
      load_byte(0,8'h11); load_byte(1,8'h00); load_byte(2,8'h2a); load_byte(3,8'h01);
      load_mode=0; reset=0;
      repeat(80) begin @(posedge clk);
        if(trap) $fatal(1,"loaded program trapped");
        if(halted) begin
          if(memory[0]!==8'h11 || memory[3]!==8'h01) $fatal(1,"loaded bytes corrupted");
          $display("EduCPU loader PASS"); $finish;
        end
      end
      $fatal(1,"loaded program did not halt");
    end
endmodule
