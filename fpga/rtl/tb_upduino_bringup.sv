`timescale 1ns/1ps
module tb_upduino_bringup;
    logic clk = 0, reset = 1;
    logic [15:0] mem_addr;
    logic [7:0] mem_wdata, mem_rdata, rom_data;
    logic mem_we, mem_valid, mem_ready, halted, trap, rom_hit;
    logic rom_pending;
    logic [15:0] rom_addr_q;

    always #5 clk = ~clk;

    educpu_core cpu (
        .clk(clk), .reset(reset), .mem_rdata(mem_rdata), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_we(mem_we), .mem_valid(mem_valid),
        .mem_ready(mem_ready), .halted(halted), .trap(trap)
    );
    educpu_bringup_rom rom (.addr(mem_addr), .data(rom_data), .hit(rom_hit));

    educpu_bringup_rom response_rom (.addr(rom_addr_q), .data(mem_rdata), .hit());
    assign mem_ready = rom_pending;

    always_ff @(posedge clk) begin
        if (reset) begin
            rom_pending <= 0;
            rom_addr_q <= 0;
        end else if (rom_pending) begin
            rom_pending <= 0;
        end else if (mem_valid && rom_hit) begin
            rom_addr_q <= mem_addr;
            rom_pending <= 1;
        end
    end

    initial begin
        repeat (3) @(posedge clk);
        reset <= 0;
        repeat (100) begin
            @(posedge clk);
            if (trap) $fatal(1, "bring-up program trapped");
            if (halted) begin
                $display("EduCPU UPduino bring-up program PASS");
                $finish;
            end
        end
        $fatal(1, "bring-up program did not halt");
    end
endmodule
