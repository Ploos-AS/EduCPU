module educpu_core (
    input  logic        clk,
    input  logic        reset,
    input  logic [7:0]  mem_rdata,
    output logic [15:0] mem_addr,
    output logic [7:0]  mem_wdata,
    output logic        mem_we,
    output logic        halted,
    output logic        trap
);
    logic [7:0]  r [0:7];
    logic [15:0] pc;
    logic [15:0] sp;
    logic [7:0]  flags;

    typedef enum logic [2:0] {
        S_FETCH,
        S_MOV_RD,
        S_MOV_RS,
        S_MOVI_RD,
        S_MOVI_IMM
    } state_t;

    state_t state;
    logic [2:0] operand_rd;
    integer i;

    localparam logic [15:0] RESET_SP = 16'hFF00;
    localparam logic [7:0] OP_NOP  = 8'h00;
    localparam logic [7:0] OP_HALT = 8'h01;
    localparam logic [7:0] OP_MOV  = 8'h10;
    localparam logic [7:0] OP_MOVI = 8'h11;

    always_ff @(posedge clk) begin
        if (reset) begin
            pc <= 16'h0000;
            sp <= RESET_SP;
            flags <= 8'h00;
            halted <= 1'b0;
            trap <= 1'b0;
            state <= S_FETCH;
            operand_rd <= 3'd0;
            for (i = 0; i < 8; i = i + 1)
                r[i] <= 8'h00;
        end else if (!halted && !trap) begin
            case (state)
                S_FETCH: begin
                    case (mem_rdata)
                        OP_NOP: pc <= pc + 16'd1;
                        OP_HALT: begin
                            pc <= pc + 16'd1;
                            halted <= 1'b1;
                        end
                        OP_MOV: begin
                            pc <= pc + 16'd1;
                            state <= S_MOV_RD;
                        end
                        OP_MOVI: begin
                            pc <= pc + 16'd1;
                            state <= S_MOVI_RD;
                        end
                        default: begin
                            pc <= pc + 16'd1;
                            trap <= 1'b1;
                        end
                    endcase
                end

                S_MOV_RD: begin
                    pc <= pc + 16'd1;
                    if (mem_rdata > 8'd7)
                        trap <= 1'b1;
                    else begin
                        operand_rd <= mem_rdata[2:0];
                        state <= S_MOV_RS;
                    end
                end

                S_MOV_RS: begin
                    pc <= pc + 16'd1;
                    if (mem_rdata > 8'd7)
                        trap <= 1'b1;
                    else begin
                        r[operand_rd] <= r[mem_rdata[2:0]];
                        state <= S_FETCH;
                    end
                end

                S_MOVI_RD: begin
                    pc <= pc + 16'd1;
                    if (mem_rdata > 8'd7)
                        trap <= 1'b1;
                    else begin
                        operand_rd <= mem_rdata[2:0];
                        state <= S_MOVI_IMM;
                    end
                end

                S_MOVI_IMM: begin
                    pc <= pc + 16'd1;
                    r[operand_rd] <= mem_rdata;
                    state <= S_FETCH;
                end

                default: begin
                    trap <= 1'b1;
                    state <= S_FETCH;
                end
            endcase
        end
    end

    assign mem_addr  = pc;
    assign mem_wdata = 8'h00;
    assign mem_we    = 1'b0;
endmodule
