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
    always @(posedge clk) begin
        if (mem_we) mem[mem_addr] <= mem_wdata;
    end

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
        assert (dut.pc == 16'h0000) else $fatal(1, "assertion failed");
        assert (dut.sp == 16'hFF00) else $fatal(1, "assertion failed");
        assert (dut.flags == 8'h00) else $fatal(1, "assertion failed");
        assert (dut.r[0] == 8'h00) else $fatal(1, "assertion failed");
        assert (dut.r[7] == 8'h00) else $fatal(1, "assertion failed");

        repeat (7) begin
            @(posedge clk); #1;
        end

        assert (dut.r[0] == 8'h2A) else $fatal(1, "assertion failed");
        assert (dut.r[1] == 8'h2A) else $fatal(1, "assertion failed");
        assert (dut.flags == 8'h00) else $fatal(1, "assertion failed");
        assert (dut.pc == 16'h0007) else $fatal(1, "assertion failed");
        assert (halted == 1'b1) else $fatal(1, "assertion failed");
        assert (trap == 1'b0) else $fatal(1, "assertion failed");

        // Invalid MOVI register operand must trap after consuming operand byte.
        clear_mem();
        mem[16'h0000] = 8'h11;
        mem[16'h0001] = 8'h08;
        do_reset();
        repeat (2) begin
            @(posedge clk); #1;
        end
        assert (dut.pc == 16'h0002) else $fatal(1, "assertion failed");
        assert (trap == 1'b1) else $fatal(1, "assertion failed");
        assert (halted == 1'b0) else $fatal(1, "assertion failed");

        // Arithmetic/flags: 0x7f + 1 = 0x80 => N,V; then SUBI 0x80 => Z,C.
        clear_mem();
        mem[0]=8'h11; mem[1]=8'h00; mem[2]=8'h7F;
        mem[3]=8'h21; mem[4]=8'h00; mem[5]=8'h01;
        mem[6]=8'h23; mem[7]=8'h00; mem[8]=8'h80;
        mem[9]=8'h01;
        do_reset();
        repeat (10) begin @(posedge clk); #1; end
        assert (dut.r[0] == 8'h00) else $fatal(1, "assertion failed");
        assert (dut.flags == 8'h05) else $fatal(1, "assertion failed"); // Z=1, C=1
        assert (halted == 1'b1) else $fatal(1, "assertion failed");
        assert (trap == 1'b0) else $fatal(1, "assertion failed");

        // CMP updates flags without changing the register.
        clear_mem();
        mem[0]=8'h11; mem[1]=8'h02; mem[2]=8'h2A;
        mem[3]=8'h25; mem[4]=8'h02; mem[5]=8'h2A;
        mem[6]=8'h01;
        do_reset();
        repeat (7) begin @(posedge clk); #1; end
        assert (dut.r[2] == 8'h2A) else $fatal(1, "assertion failed");
        assert (dut.flags == 8'h05) else $fatal(1, "assertion failed");
        assert (halted == 1'b1) else $fatal(1, "assertion failed");

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
        assert (dut.r[0] == 8'h7E) else $fatal(1, "assertion failed");
        assert (dut.r[1] == 8'h0F) else $fatal(1, "assertion failed");
        assert (dut.flags == 8'h00) else $fatal(1, "assertion failed");
        assert (halted == 1'b1) else $fatal(1, "assertion failed");
        assert (trap == 1'b0) else $fatal(1, "assertion failed");

        // SHL 0x80 => zero with carry: Z=1,C=1.
        clear_mem();
        mem[0]=8'h11; mem[1]=8'h03; mem[2]=8'h80;
        mem[3]=8'h2C; mem[4]=8'h03;
        mem[5]=8'h01;
        do_reset();
        repeat (6) begin @(posedge clk); #1; end
        assert (dut.r[3] == 8'h00) else $fatal(1, "assertion failed");
        assert (dut.flags == 8'h05) else $fatal(1, "assertion failed");
        assert (halted == 1'b1) else $fatal(1, "assertion failed");

        // Absolute LOAD/STORE round trip.
        clear_mem();
        mem[0]=8'h11; mem[1]=8'h00; mem[2]=8'hA5;
        mem[3]=8'h13; mem[4]=8'h00; mem[5]=8'h20; mem[6]=8'h00;
        mem[7]=8'h12; mem[8]=8'h01; mem[9]=8'h00; mem[10]=8'h20;
        mem[11]=8'h01;
        do_reset();
        repeat (12) begin @(posedge clk); #1; end
        assert (mem[16'h2000] == 8'hA5) else $fatal(1, "assertion failed");
        assert (dut.r[1] == 8'hA5) else $fatal(1, "assertion failed");
        assert (dut.flags == 8'h00) else $fatal(1, "assertion failed");
        assert (halted == 1'b1) else $fatal(1, "assertion failed");
        assert (trap == 1'b0) else $fatal(1, "assertion failed");

        // Register-indirect page-zero memory.
        clear_mem();
        mem[0]=8'h11; mem[1]=8'h02; mem[2]=8'h80;
        mem[3]=8'h11; mem[4]=8'h03; mem[5]=8'h5A;
        mem[6]=8'h15; mem[7]=8'h02; mem[8]=8'h03;
        mem[9]=8'h14; mem[10]=8'h04; mem[11]=8'h02;
        mem[12]=8'h01;
        do_reset();
        repeat (13) begin @(posedge clk); #1; end
        assert (mem[16'h0080] == 8'h5A) else $fatal(1, "assertion failed");
        assert (dut.r[4] == 8'h5A) else $fatal(1, "assertion failed");
        assert (halted == 1'b1) else $fatal(1, "assertion failed");
        assert (trap == 1'b0) else $fatal(1, "assertion failed");

        // SP-relative signed offset memory.
        clear_mem();
        mem[0]=8'h11; mem[1]=8'h05; mem[2]=8'hCC;
        mem[3]=8'h17; mem[4]=8'hFE; mem[5]=8'h05;
        mem[6]=8'h16; mem[7]=8'h06; mem[8]=8'hFE;
        mem[9]=8'h01;
        do_reset();
        repeat (10) begin @(posedge clk); #1; end
        assert (mem[16'hFEFE] == 8'hCC) else $fatal(1, "assertion failed");
        assert (dut.r[6] == 8'hCC) else $fatal(1, "assertion failed");
        assert (halted == 1'b1) else $fatal(1, "assertion failed");
        assert (trap == 1'b0) else $fatal(1, "assertion failed");

        // Conditional branch: CMPI sets Z, JZ skips invalid opcode to HALT.
        clear_mem();
        mem[0]=8'h11; mem[1]=8'h00; mem[2]=8'h2A;
        mem[3]=8'h25; mem[4]=8'h00; mem[5]=8'h2A;
        mem[6]=8'h31; mem[7]=8'h0A; mem[8]=8'h00;
        mem[9]=8'hFF;
        mem[10]=8'h01;
        do_reset();
        repeat (10) begin @(posedge clk); #1; end
        assert (dut.pc == 16'h000B) else $fatal(1, "assertion failed");
        assert (halted == 1'b1) else $fatal(1, "assertion failed");
        assert (trap == 1'b0) else $fatal(1, "assertion failed");

        // Not-taken JNZ must consume both address bytes and continue sequentially.
        clear_mem();
        mem[0]=8'h11; mem[1]=8'h00; mem[2]=8'h00;
        mem[3]=8'h25; mem[4]=8'h00; mem[5]=8'h00;
        mem[6]=8'h32; mem[7]=8'h20; mem[8]=8'h00;
        mem[9]=8'h01;
        do_reset();
        repeat (10) begin @(posedge clk); #1; end
        assert (dut.pc == 16'h000A) else $fatal(1, "assertion failed");
        assert (halted == 1'b1) else $fatal(1, "assertion failed");
        assert (trap == 1'b0) else $fatal(1, "assertion failed");

        // JMP is unconditional and little-endian.
        clear_mem();
        mem[0]=8'h30; mem[1]=8'h34; mem[2]=8'h12;
        mem[16'h1234]=8'h01;
        do_reset();
        repeat (4) begin @(posedge clk); #1; end
        assert (dut.pc == 16'h1235) else $fatal(1, "assertion failed");
        assert (halted == 1'b1) else $fatal(1, "assertion failed");
        assert (trap == 1'b0) else $fatal(1, "assertion failed");

        // PUSH/POP and ENTER/LEAVE preserve visible stack semantics.
        clear_mem();
        mem[0]=8'h11; mem[1]=8'h00; mem[2]=8'h5A;
        mem[3]=8'h40; mem[4]=8'h00;
        mem[5]=8'h41; mem[6]=8'h01;
        mem[7]=8'h18; mem[8]=8'h04;
        mem[9]=8'h19; mem[10]=8'h04;
        mem[11]=8'h01;
        do_reset();
        repeat (12) begin @(posedge clk); #1; end
        assert (dut.r[1] == 8'h5A) else $fatal(1, "assertion failed");
        assert (dut.sp == 16'hFF00) else $fatal(1, "assertion failed");
        assert (mem[16'hFEFF] == 8'h5A) else $fatal(1, "assertion failed");
        assert (halted == 1'b1) else $fatal(1, "assertion failed");
        assert (trap == 1'b0) else $fatal(1, "assertion failed");

        // CALL pushes return PC high then low; RET reconstructs it.
        clear_mem();
        mem[0]=8'h38; mem[1]=8'h08; mem[2]=8'h00; // CALL 0008
        mem[3]=8'h01;                              // return target HALT
        mem[8]=8'h11; mem[9]=8'h02; mem[10]=8'h33;
        mem[11]=8'h39;                             // RET
        do_reset();
        repeat (12) begin @(posedge clk); #1; end
        assert (dut.r[2] == 8'h33) else $fatal(1, "assertion failed");
        assert (dut.sp == 16'hFF00) else $fatal(1, "assertion failed");
        assert (mem[16'hFEFF] == 8'h00) else $fatal(1, "assertion failed"); // return high
        assert (mem[16'hFEFE] == 8'h03) else $fatal(1, "assertion failed"); // return low at final SP after pushes
        assert (dut.pc == 16'h0004) else $fatal(1, "assertion failed");
        assert (halted == 1'b1) else $fatal(1, "assertion failed");
        assert (trap == 1'b0) else $fatal(1, "assertion failed");

        $display("EduCPU FPGA M0.7 stack/call PASS");
        $finish;
    end
endmodule
