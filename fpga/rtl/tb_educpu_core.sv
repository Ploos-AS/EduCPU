module tb_educpu_core;
    logic clk = 1'b0;
    logic reset = 1'b1;
    logic [7:0] mem [0:65535];
    logic [7:0] mem_rdata;
    logic [15:0] mem_addr;
    logic [7:0] mem_wdata;
    logic mem_we, halted, trap;
    integer i;

    assign mem_rdata = mem[mem_addr];

    educpu_core dut (
        .clk, .reset, .mem_rdata, .mem_addr, .mem_wdata, .mem_we, .halted, .trap
    );

    always #5 clk = ~clk;

    task clear_mem;
        begin
            for (i = 0; i < 65536; i = i + 1)
                mem[i] = 8'h00;
        end
    endtask

    task do_reset;
        begin
            reset = 1'b1;
            @(posedge clk); #1;
            reset = 1'b0;
        end
    endtask

    initial begin
        clear_mem();

        // MOVI R0,42; MOV R1,R0; HALT
        mem[16'h0000] = 8'h11;
        mem[16'h0001] = 8'h00;
        mem[16'h0002] = 8'h2A;
        mem[16'h0003] = 8'h10;
        mem[16'h0004] = 8'h01;
        mem[16'h0005] = 8'h00;
        mem[16'h0006] = 8'h01;

        do_reset();
        assert (dut.pc == 16'h0000);
        assert (dut.sp == 16'hFF00);
        assert (dut.flags == 8'h00);
        assert (dut.r[0] == 8'h00);
        assert (dut.r[7] == 8'h00);

        repeat (7) begin
            @(posedge clk); #1;
        end

        assert (dut.r[0] == 8'h2A);
        assert (dut.r[1] == 8'h2A);
        assert (dut.flags == 8'h00);
        assert (dut.pc == 16'h0007);
        assert (halted == 1'b1);
        assert (trap == 1'b0);

        // Invalid MOVI register operand must trap after consuming operand byte.
        clear_mem();
        mem[16'h0000] = 8'h11;
        mem[16'h0001] = 8'h08;
        do_reset();
        repeat (2) begin
            @(posedge clk); #1;
        end
        assert (dut.pc == 16'h0002);
        assert (trap == 1'b1);
        assert (halted == 1'b0);

        $display("EduCPU FPGA M0.3 MOV/MOVI PASS");
        $finish;
    end
endmodule
