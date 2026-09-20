module educpu_core (
    input  logic clk,
    input  logic reset,
    input  logic [7:0]  mem_rdata,
    output logic [15:0] mem_addr,
    output logic [7:0]  mem_wdata,
    output logic mem_we,
    output logic halted,
    output logic trap
);
    logic [7:0] r [0:7];
    logic [15:0] pc;
    logic [15:0] sp;
    logic [7:0] flags;

    localparam logic [15:0] RESET_SP = 16'hFF00;
    localparam logic [7:0] OP_NOP = 8'h00;
    localparam logic [7:0] OP_HALT = 8'h01;
    localparam logic [7:0] OP_INVALID_MAX = 8'hFF;

    always_ff @(posedge clk) begin
        if (reset) begin
            pc <= 16'h0000;
            sp <= RESET_SP;
            flags <= 8'h00;
            halted <= 1'b0;
            trap <= 1'b0;
        end else if (!halted && !trap) begin
            case (mem_rdata)
                OP_NOP: pc <= pc + 16'd1;
                OP_HALT: begin
                    pc <= pc + 16'd1;
                    halted <= 1'b1;
                end
                default: begin
                    pc <= pc + 16'd1;
                    trap <= 1'b1;
                end
            endcase
        end
    end

    assign mem_addr = pc;
    assign mem_wdata = 8'h00;
    assign mem_we = 1'b0;

    // M0.1 architectural-state observability for simulation and future conformance harnesses.
    // These remain internal for now; board wrappers must not redefine architectural state.
    // synthesis translate_off
    // synthesis translate_on
endmodule
