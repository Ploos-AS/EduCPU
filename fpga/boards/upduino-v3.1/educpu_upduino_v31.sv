// UPduino v3.x bring-up wrapper for EduCPU.
// Internal HF oscillator, deterministic power-on reset and a tiny read-only
// boot overlay exercise the real core before physical qualification.
module educpu_upduino_v31 (
    output logic led_r,
    output logic led_g,
    output logic led_b
);
    logic clk, reset;
    logic [3:0] reset_count = 4'hf;
    logic halted, trap;

    logic [15:0] mem_addr;
    logic [7:0] mem_wdata, mem_rdata, ram_rdata, rom_data;
    logic mem_we, mem_valid, mem_ready, ram_ready, rom_hit;
    logic rom_pending;
    logic [15:0] rom_addr_q;
    logic [7:0] rom_response_data;

    SB_HFOSC #(.CLKHF_DIV("0b10")) hfosc (
        .CLKHFPU(1'b1), .CLKHFEN(1'b1), .CLKHF(clk)
    );

    always_ff @(posedge clk) begin
        if (reset_count != 0)
            reset_count <= reset_count - 1'b1;
        if (reset) begin
            rom_pending <= 1'b0;
            rom_addr_q <= 16'h0000;
        end else if (rom_pending) begin
            rom_pending <= 1'b0;
        end else if (mem_valid && rom_hit) begin
            rom_pending <= 1'b1;
            rom_addr_q <= mem_addr;
        end
    end
    assign reset = (reset_count != 0);

    educpu_core cpu (
        .clk(clk), .reset(reset),
        .mem_rdata(mem_rdata), .mem_addr(mem_addr), .mem_wdata(mem_wdata),
        .mem_we(mem_we), .mem_valid(mem_valid), .mem_ready(mem_ready),
        .halted(halted), .trap(trap)
    );

    educpu_bringup_rom bootrom (.addr(mem_addr), .data(rom_data), .hit(rom_hit));
    educpu_bringup_rom response_rom (.addr(rom_addr_q), .data(rom_response_data), .hit());

    educpu_up5k_spram ram (
        .clk(clk), .reset(reset),
        .valid(mem_valid && !rom_hit), .we(mem_we),
        .addr(mem_addr), .wdata(mem_wdata),
        .rdata(ram_rdata), .ready(ram_ready)
    );

    // ROM reads complete one cycle after request, matching the synchronous RAM
    // contract. Writes to the overlay are deliberately ignored.
    assign mem_ready = rom_pending || ram_ready;
    assign mem_rdata = rom_pending ? rom_response_data : ram_rdata;

    // UPduino RGB LED pins are active-low.
    assign led_r = !trap;
    assign led_g = !(!halted && !trap);
    assign led_b = !(halted && !trap);
endmodule
