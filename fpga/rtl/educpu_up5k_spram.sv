// iCE40 UltraPlus physical memory backend for EduCPU.
// 64 KiB byte-addressable memory using two SB_SPRAM256KA blocks.
// Each primitive is 16K x 16 (32 KiB). addr[15] selects the bank;
// addr[14:1] selects the 16-bit word; addr[0] selects low/high byte.
module educpu_up5k_spram (
    input  logic        clk,
    input  logic        reset,
    input  logic        valid,
    input  logic        we,
    input  logic [15:0] addr,
    input  logic [7:0]  wdata,
    output logic [7:0]  rdata,
    output logic        ready
);
    logic pending, wait_release;
    logic bank_q, byte_q, we_q;
    logic [13:0] word_q;
    logic [7:0] wdata_q;
    logic [15:0] dout0, dout1;
    logic cs0, cs1;
    logic [15:0] din;
    logic [3:0] mask;
    logic spram_we;

    assign cs0 = pending && !bank_q;
    assign cs1 = pending &&  bank_q;
    assign din = byte_q ? {wdata_q, 8'h00} : {8'h00, wdata_q};
    // MASKWREN is nibble-granular: enable the two nibbles of the selected byte.
    assign mask = byte_q ? 4'b1100 : 4'b0011;
    assign spram_we = pending && we_q;

    SB_SPRAM256KA ram0 (
        .ADDRESS(word_q), .DATAIN(din), .MASKWREN(mask),
        .WREN(spram_we), .CHIPSELECT(cs0), .CLOCK(clk),
        .STANDBY(1'b0), .SLEEP(1'b0), .POWEROFF(1'b1), .DATAOUT(dout0)
    );
    SB_SPRAM256KA ram1 (
        .ADDRESS(word_q), .DATAIN(din), .MASKWREN(mask),
        .WREN(spram_we), .CHIPSELECT(cs1), .CLOCK(clk),
        .STANDBY(1'b0), .SLEEP(1'b0), .POWEROFF(1'b1), .DATAOUT(dout1)
    );

    always_ff @(posedge clk) begin
        if (reset) begin
            pending <= 1'b0;
            wait_release <= 1'b0;
            ready <= 1'b0;
            rdata <= 8'h00;
        end else begin
            ready <= 1'b0;
            if (pending) begin
                if (!we_q)
                    rdata <= byte_q
                        ? (bank_q ? dout1[15:8] : dout0[15:8])
                        : (bank_q ? dout1[7:0]  : dout0[7:0]);
                ready <= 1'b1;
                pending <= 1'b0;
                wait_release <= 1'b1;
            end else if (wait_release) begin
                wait_release <= 1'b0;
            end else if (valid) begin
                bank_q <= addr[15];
                byte_q <= addr[0];
                word_q <= addr[14:1];
                we_q <= we;
                wdata_q <= wdata;
                pending <= 1'b1;
            end
        end
    end
endmodule
