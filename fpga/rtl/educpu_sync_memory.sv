module educpu_sync_memory #(
    parameter ADDR_WIDTH = 16,
    parameter INIT_FILE = ""
) (
    input  logic                  clk,
    input  logic                  reset,
    input  logic                  mem_valid,
    input  logic                  mem_we,
    input  logic [ADDR_WIDTH-1:0] mem_addr,
    input  logic [7:0]            mem_wdata,
    output logic [7:0]            mem_rdata,
    output logic                  mem_ready
);
    logic [7:0] memory [0:(1<<ADDR_WIDTH)-1];
    logic pending;
    logic [ADDR_WIDTH-1:0] req_addr;
    logic req_we;
    logic [7:0] req_wdata;
    logic wait_release;

    initial begin
        if (INIT_FILE != "")
            $readmemh(INIT_FILE, memory);
    end

    always_ff @(posedge clk) begin
        if (reset) begin
            mem_ready <= 1'b0;
            pending <= 1'b0;
            wait_release <= 1'b0;
            mem_rdata <= 8'h00;
        end else begin
            mem_ready <= 1'b0;
            if (pending) begin
                if (req_we)
                    memory[req_addr] <= req_wdata;
                else
                    mem_rdata <= memory[req_addr];
                mem_ready <= 1'b1;
                pending <= 1'b0;
                wait_release <= 1'b1;
            end else if (wait_release) begin
                wait_release <= 1'b0;
            end else if (mem_valid) begin
                req_addr <= mem_addr;
                req_we <= mem_we;
                req_wdata <= mem_wdata;
                pending <= 1'b1;
            end
        end
    end
endmodule
