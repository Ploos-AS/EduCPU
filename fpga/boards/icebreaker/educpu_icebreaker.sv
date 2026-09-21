// Secondary iCEBreaker bring-up wrapper for EduCPU.
// Uses the board's 12 MHz clock and the same UP5K SPRAM/bring-up ROM path as
// the canonical UPduino target. Physical qualification remains separate.
module educpu_icebreaker (
    input logic clk_12mhz,
    input logic reset_n,
    output logic led
);
    logic reset;
    logic [3:0] reset_count = 4'hf;
    logic halted, trap;
    logic [15:0] mem_addr;
    logic [7:0] mem_wdata, mem_rdata, ram_rdata, rom_data;
    logic mem_we, mem_valid, mem_ready, ram_ready, rom_hit;
    logic rom_pending;
    logic [15:0] rom_addr_q;
    logic [7:0] rom_response_data;

    always_ff @(posedge clk_12mhz) begin
        if (!reset_n) reset_count <= 4'hf;
        else if (reset_count != 0) reset_count <= reset_count - 1'b1;
        if (reset) begin rom_pending <= 1'b0; rom_addr_q <= 16'h0000; end
        else if (rom_pending) rom_pending <= 1'b0;
        else if (mem_valid && rom_hit) begin rom_pending <= 1'b1; rom_addr_q <= mem_addr; end
    end
    assign reset = !reset_n || (reset_count != 0);

    educpu_core cpu(.clk(clk_12mhz),.reset(reset),.mem_rdata(mem_rdata),.mem_addr(mem_addr),.mem_wdata(mem_wdata),.mem_we(mem_we),.mem_valid(mem_valid),.mem_ready(mem_ready),.halted(halted),.trap(trap));
    educpu_bringup_rom bootrom(.addr(mem_addr),.data(rom_data),.hit(rom_hit));
    educpu_bringup_rom response_rom(.addr(rom_addr_q),.data(rom_response_data),.hit());
    educpu_up5k_spram ram(.clk(clk_12mhz),.reset(reset),.valid(mem_valid && !rom_hit),.we(mem_we),.addr(mem_addr),.wdata(mem_wdata),.rdata(ram_rdata),.ready(ram_ready));
    assign mem_ready = rom_pending || ram_ready;
    assign mem_rdata = rom_pending ? rom_response_data : ram_rdata;
    assign led = halted && !trap;
endmodule
