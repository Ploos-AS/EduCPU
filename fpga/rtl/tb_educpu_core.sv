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

        // Arithmetic/flags: 0x7f + 1 = 0x80 => N,V; then SUBI 0x80 => Z,C.
        clear_mem();
        mem[0]=8'h11; mem[1]=8'h00; mem[2]=8'h7F;
        mem[3]=8'h21; mem[4]=8'h00; mem[5]=8'h01;
        mem[6]=8'h23; mem[7]=8'h00; mem[8]=8'h80;
        mem[9]=8'h01;
        do_reset();
        repeat (10) begin @(posedge clk); #1; end
        assert (dut.r[0] == 8'h00);
        assert (dut.flags == 8'h05); // Z=1, C=1
        assert (halted == 1'b1);
        assert (trap == 1'b0);

        // CMP updates flags without changing the register.
        clear_mem();
        mem[0]=8'h11; mem[1]=8'h02; mem[2]=8'h2A;
        mem[3]=8'h25; mem[4]=8'h02; mem[5]=8'h2A;
        mem[6]=8'h01;
        do_reset();
        repeat (7) begin @(posedge clk); #1; end
        assert (dut.r[2] == 8'h2A);
        assert (dut.flags == 8'h05);
        assert (halted == 1'b1);

        // Logic and shift operations: logical ops clear C/V; shifts expose outgoing bit in C.
        clear_mem();
        mem[0]=8'h11; mem[1]=8'h00; mem[2]=8'h81; // MOVI R0,81
        mem[3]=8'h11; mem[4]=8'h01; mem[5]=8'h0F; // MOVI R1,0F
        mem[6]=8'h28; mem[7]=8'h00; mem[8]=8'h01; // AND R0,R1 => 01
        mem[9]=8'h2B; mem[10]=8'h00;              // NOT R0 => FE, N
        mem[11]=8'h2C; mem[12]=8'h00;             // SHL R0 => FC, C,N
        mem[13]=8'h2D; mem[14]=8'h00;             // SHR R0 => 7E, C=0
        mem[15]=8'h01;
        do_reset();
        repeat (16) begin @(posedge clk); #1; end
        assert (dut.r[0] == 8'h7E);
        assert (dut.r[1] == 8'h0F);
        assert (dut.flags == 8'h00);
        assert (halted == 1'b1);
        assert (trap == 1'b0);

        // SHL 0x80 => zero with carry: Z=1,C=1.
        clear_mem();
        mem[0]=8'h11; mem[1]=8'h03; mem[2]=8'h80;
        mem[3]=8'h2C; mem[4]=8'h03;
        mem[5]=8'h01;
        do_reset();
        repeat (6) begin @(posedge clk); #1; end
        assert (dut.r[3] == 8'h00);
        assert (dut.flags == 8'h05);
        assert (halted == 1'b1);

        $display("EduCPU FPGA M0.4 complete ALU/FLAGS PASS");
        $finish;
    end
endmodule
