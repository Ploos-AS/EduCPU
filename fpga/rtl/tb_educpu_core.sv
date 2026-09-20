module tb_educpu_core;
    logic clk = 1'b0;
    logic reset = 1'b1;
    logic [15:0] mem_rdata = 16'h0000;
    logic [15:0] mem_addr, mem_wdata;
    logic mem_we, halted, trap;

    educpu_core dut (.clk, .reset, .mem_rdata, .mem_addr, .mem_wdata, .mem_we, .halted, .trap);
    always #5 clk = ~clk;

    initial begin
        #20;
        reset = 1'b0;
        #10;
        assert (dut.pc == 16'h0000);
        assert (dut.sp == 16'hFF00);
        assert (dut.flags == 8'h00);
        assert (dut.r[0] == 16'h0000);
        assert (dut.r[7] == 16'h0000);
        assert (mem_addr == 16'h0000);
        assert (mem_we == 1'b0);
        assert (halted == 1'b0);
        assert (trap == 1'b0);
        $display("EduCPU FPGA M0 reset PASS");
        $finish;
    end
endmodule
