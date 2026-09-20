module educpu_machine (
    input logic clk,
    input logic reset,
    output logic halted,
    output logic trap
);
    logic [7:0] mem_rdata, mem_wdata;
    logic [15:0] mem_addr;
    logic mem_we, mem_valid, mem_ready;

    educpu_core cpu (
        .clk, .reset, .mem_rdata, .mem_addr, .mem_wdata, .mem_we,
        .mem_valid, .mem_ready, .halted, .trap
    );

    educpu_sync_ram ram (
        .clk, .reset, .valid(mem_valid), .we(mem_we), .addr(mem_addr),
        .wdata(mem_wdata), .rdata(mem_rdata), .ready(mem_ready)
    );
endmodule
