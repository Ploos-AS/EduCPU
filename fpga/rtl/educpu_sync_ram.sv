module educpu_sync_ram #(
    parameter ADDR_WIDTH = 16,
    parameter DATA_WIDTH = 8
) (
    input  logic                  clk,
    input  logic                  reset,
    input  logic                  valid,
    input  logic                  we,
    input  logic [ADDR_WIDTH-1:0] addr,
    input  logic [DATA_WIDTH-1:0] wdata,
    output logic [DATA_WIDTH-1:0] rdata,
    output logic                  ready
);
    logic [DATA_WIDTH-1:0] mem [0:(1<<ADDR_WIDTH)-1];
    logic pending;
    logic pending_we;
    logic [ADDR_WIDTH-1:0] pending_addr;
    logic [DATA_WIDTH-1:0] pending_wdata;
    logic wait_release;

    always_ff @(posedge clk) begin
        if (reset) begin
            ready <= 1'b0;
            pending <= 1'b0;
            wait_release <= 1'b0;
            rdata <= '0;
        end else begin
            ready <= 1'b0;
            if (pending) begin
                if (pending_we)
                    mem[pending_addr] <= pending_wdata;
                else
                    rdata <= mem[pending_addr];
                ready <= 1'b1;
                pending <= 1'b0;
                wait_release <= 1'b1;
            end else if (wait_release) begin
                wait_release <= 1'b0;
            end else if (valid) begin
                pending <= 1'b1;
                pending_we <= we;
                pending_addr <= addr;
                pending_wdata <= wdata;
            end
        end
    end
endmodule
