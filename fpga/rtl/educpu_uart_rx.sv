// Minimal 8-N-1 UART receiver for the UPduino loader transport.
// One-cycle data_valid pulse after a complete byte. CLKS_PER_BIT is configurable.
module educpu_uart_rx #(
    parameter integer CLKS_PER_BIT = 104
) (
    input logic clk, input logic reset, input logic rx,
    output logic [7:0] data, output logic data_valid
);
    localparam integer CW = $clog2(CLKS_PER_BIT + 1);
    logic [CW-1:0] count;
    logic [3:0] bit_index;
    logic [7:0] shift;
    logic busy;

    always_ff @(posedge clk) begin
        data_valid <= 1'b0;
        if (reset) begin
            count <= 0; bit_index <= 0; shift <= 0; busy <= 0; data <= 0;
        end else if (!busy) begin
            if (!rx) begin
                busy <= 1'b1; count <= (CLKS_PER_BIT/2) - 1;
                bit_index <= 0;
            end
        end else if (count != 0) begin
            count <= count - 1'b1;
        end else if (bit_index < 8) begin
            shift[bit_index] <= rx;
            bit_index <= bit_index + 1'b1;
            count <= CLKS_PER_BIT - 1;
        end else begin
            // Stop bit must be high.
            if (rx) begin data <= shift; data_valid <= 1'b1; end
            busy <= 1'b0;
        end
    end
endmodule
