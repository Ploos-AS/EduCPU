module educpu_core (
    input  logic clk,
    input  logic reset,
    input  logic [15:0] mem_rdata,
    output logic [15:0] mem_addr,
    output logic [15:0] mem_wdata,
    output logic mem_we,
    output logic halted,
    output logic trap
);
    logic [15:0] r [0:7];
    logic [15:0] pc;
    logic [15:0] sp;
    logic [7:0] flags;

    always_ff @(posedge clk) begin
        if (reset) begin
            pc <= 16'h0000;
            sp <= 16'hFF00;
            flags <= 8'h00;
            halted <= 1'b0;
            trap <= 1'b0;
        end
    end

    assign mem_addr = pc;
    assign mem_wdata = 16'h0000;
    assign mem_we = 1'b0;
endmodule
