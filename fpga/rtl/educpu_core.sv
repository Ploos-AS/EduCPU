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

    typedef enum logic [3:0] {
        S_FETCH,
        S_MOV_RD,
        S_MOV_RS,
        S_MOVI_RD,
        S_MOVI_IMM,
        S_ALU_RD,
        S_ALU_SRC,
        S_UNARY_RD,
        S_MEM_RD,
        S_MEM_ARG,
        S_MEM_ADDR_LO,
        S_MEM_ADDR_HI,
        S_MEM_ACCESS
    } state_t;

    state_t state;
    logic [2:0] operand_rd;
    logic [7:0] current_op;
    logic [8:0] alu_ext;
    logic [7:0] alu_out;
    logic [15:0] operand_addr;
    integer i;

    localparam logic [15:0] RESET_SP = 16'hFF00;
    localparam logic [7:0] OP_NOP  = 8'h00;
    localparam logic [7:0] OP_HALT = 8'h01;
    localparam logic [7:0] OP_MOV  = 8'h10;
    localparam logic [7:0] OP_MOVI = 8'h11;
    localparam logic [7:0] OP_LOAD = 8'h12;
    localparam logic [7:0] OP_STORE = 8'h13;
    localparam logic [7:0] OP_LOADR = 8'h14;
    localparam logic [7:0] OP_STORER = 8'h15;
    localparam logic [7:0] OP_LOADS = 8'h16;
    localparam logic [7:0] OP_STORES = 8'h17;
    localparam logic [7:0] OP_ADD  = 8'h20;
    localparam logic [7:0] OP_ADDI = 8'h21;
    localparam logic [7:0] OP_SUB  = 8'h22;
    localparam logic [7:0] OP_SUBI = 8'h23;
    localparam logic [7:0] OP_CMP  = 8'h24;
    localparam logic [7:0] OP_CMPI = 8'h25;
    localparam logic [7:0] OP_AND  = 8'h28;
    localparam logic [7:0] OP_OR   = 8'h29;
    localparam logic [7:0] OP_XOR  = 8'h2A;
    localparam logic [7:0] OP_NOT  = 8'h2B;
    localparam logic [7:0] OP_SHL  = 8'h2C;
    localparam logic [7:0] OP_SHR  = 8'h2D;

    always_ff @(posedge clk) begin
        if (reset) begin
            pc <= 16'h0000;
            sp <= RESET_SP;
            flags <= 8'h00;
            halted <= 1'b0;
            trap <= 1'b0;
            state <= S_FETCH;
            operand_rd <= 3'd0;
            current_op <= 8'h00;
            operand_addr <= 16'h0000;
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
                        OP_LOAD, OP_STORE, OP_LOADR, OP_STORER, OP_LOADS, OP_STORES: begin
                            current_op <= mem_rdata;
                            pc <= pc + 16'd1;
                            state <= S_MEM_RD;
                        end
                        OP_ADD, OP_ADDI, OP_SUB, OP_SUBI, OP_CMP, OP_CMPI,
                        OP_AND, OP_OR, OP_XOR: begin
                            current_op <= mem_rdata;
                            pc <= pc + 16'd1;
                            state <= S_ALU_RD;
                        end
                        OP_NOT, OP_SHL, OP_SHR: begin
                            current_op <= mem_rdata;
                            pc <= pc + 16'd1;
                            state <= S_UNARY_RD;
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

                S_ALU_RD: begin
                    pc <= pc + 16'd1;
                    if (mem_rdata > 8'd7)
                        trap <= 1'b1;
                    else begin
                        operand_rd <= mem_rdata[2:0];
                        state <= S_ALU_SRC;
                    end
                end

                S_ALU_SRC: begin
                    pc <= pc + 16'd1;
                    if ((current_op == OP_ADD || current_op == OP_SUB || current_op == OP_CMP || current_op == OP_AND || current_op == OP_OR || current_op == OP_XOR) && mem_rdata > 8'd7)
                        trap <= 1'b1;
                    else begin
                        if (current_op == OP_AND || current_op == OP_OR || current_op == OP_XOR) begin
                            if (current_op == OP_AND) alu_out = r[operand_rd] & r[mem_rdata[2:0]];
                            else if (current_op == OP_OR) alu_out = r[operand_rd] | r[mem_rdata[2:0]];
                            else alu_out = r[operand_rd] ^ r[mem_rdata[2:0]];
                            r[operand_rd] <= alu_out;
                            flags <= {6'b000000, alu_out[7], alu_out == 8'h00};
                        end else if (current_op == OP_ADD || current_op == OP_ADDI) begin
                            alu_ext = {1'b0, r[operand_rd]} + {1'b0, (current_op == OP_ADD ? r[mem_rdata[2:0]] : mem_rdata)};
                            alu_out = alu_ext[7:0];
                            flags <= {4'b0000,
                                      (~(r[operand_rd] ^ (current_op == OP_ADD ? r[mem_rdata[2:0]] : mem_rdata)) & (r[operand_rd] ^ alu_out) & 8'h80) != 0,
                                      alu_ext[8], alu_out[7], alu_out == 8'h00};
                            if (current_op != OP_CMP) r[operand_rd] <= alu_out;
                        end else begin
                            alu_out = r[operand_rd] - (current_op == OP_SUB || current_op == OP_CMP ? r[mem_rdata[2:0]] : mem_rdata);
                            flags <= {4'b0000,
                                      ((r[operand_rd] ^ (current_op == OP_SUB || current_op == OP_CMP ? r[mem_rdata[2:0]] : mem_rdata)) & (r[operand_rd] ^ alu_out) & 8'h80) != 0,
                                      r[operand_rd] >= (current_op == OP_SUB || current_op == OP_CMP ? r[mem_rdata[2:0]] : mem_rdata),
                                      alu_out[7], alu_out == 8'h00};
                            if (current_op == OP_SUB || current_op == OP_SUBI) r[operand_rd] <= alu_out;
                        end
                        state <= S_FETCH;
                    end
                end

                S_MEM_RD: begin
                    pc <= pc + 16'd1;
                    if (current_op == OP_LOAD || current_op == OP_LOADR || current_op == OP_LOADS) begin
                        if (mem_rdata > 8'd7) trap <= 1'b1;
                        else begin operand_rd <= mem_rdata[2:0]; state <= S_MEM_ARG; end
                    end else if (current_op == OP_STORE) begin
                        operand_addr[7:0] <= mem_rdata;
                        state <= S_MEM_ADDR_HI;
                    end else begin
                        operand_addr[7:0] <= mem_rdata;
                        state <= S_MEM_ARG;
                    end
                end

                S_MEM_ARG: begin
                    pc <= pc + 16'd1;
                    if (current_op == OP_LOAD) begin
                        operand_addr[7:0] <= mem_rdata;
                        state <= S_MEM_ADDR_HI;
                    end else if (current_op == OP_LOADR) begin
                        if (mem_rdata > 8'd7) trap <= 1'b1;
                        else begin operand_addr <= {8'h00, r[mem_rdata[2:0]]}; state <= S_MEM_ACCESS; end
                    end else if (current_op == OP_LOADS) begin
                        operand_addr <= sp + {{8{mem_rdata[7]}}, mem_rdata};
                        state <= S_MEM_ACCESS;
                    end else if (current_op == OP_STORER) begin
                        if (operand_addr[7:0] > 8'd7 || mem_rdata > 8'd7) trap <= 1'b1;
                        else begin operand_addr <= {8'h00, r[operand_addr[2:0]]}; operand_rd <= mem_rdata[2:0]; state <= S_MEM_ACCESS; end
                    end else begin
                        if (mem_rdata > 8'd7) trap <= 1'b1;
                        else begin operand_addr <= sp + {{8{operand_addr[7]}}, operand_addr[7:0]}; operand_rd <= mem_rdata[2:0]; state <= S_MEM_ACCESS; end
                    end
                end

                S_MEM_ADDR_HI: begin
                    pc <= pc + 16'd1;
                    operand_addr[15:8] <= mem_rdata;
                    if (current_op == OP_LOAD) state <= S_MEM_ACCESS;
                    else state <= S_MEM_ARG;
                end

                S_MEM_ACCESS: begin
                    if (current_op == OP_LOAD || current_op == OP_LOADR || current_op == OP_LOADS)
                        r[operand_rd] <= mem_rdata;
                    state <= S_FETCH;
                end

                S_UNARY_RD: begin
                    pc <= pc + 16'd1;
                    if (mem_rdata > 8'd7)
                        trap <= 1'b1;
                    else begin
                        if (current_op == OP_NOT) begin
                            alu_out = ~r[mem_rdata[2:0]];
                            r[mem_rdata[2:0]] <= alu_out;
                            flags <= {6'b000000, alu_out[7], alu_out == 8'h00};
                        end else if (current_op == OP_SHL) begin
                            alu_out = r[mem_rdata[2:0]] << 1;
                            r[mem_rdata[2:0]] <= alu_out;
                            flags <= {5'b00000, r[mem_rdata[2:0]][7], alu_out[7], alu_out == 8'h00};
                        end else begin
                            alu_out = r[mem_rdata[2:0]] >> 1;
                            r[mem_rdata[2:0]] <= alu_out;
                            flags <= {5'b00000, r[mem_rdata[2:0]][0], alu_out[7], alu_out == 8'h00};
                        end
                        state <= S_FETCH;
                    end
                end

                default: begin
                    trap <= 1'b1;
                    state <= S_FETCH;
                end
            endcase
        end
    end

    assign mem_addr = (state == S_MEM_ACCESS) ? operand_addr : pc;
    assign mem_wdata = r[operand_rd];
    assign mem_we = (state == S_MEM_ACCESS) &&
                    (current_op == OP_STORE || current_op == OP_STORER || current_op == OP_STORES);
endmodule
