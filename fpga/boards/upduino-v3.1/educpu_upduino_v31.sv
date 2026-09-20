// UPduino v3.x bring-up wrapper for EduCPU.
// Uses the iCE40 UltraPlus internal HF oscillator so no external clock jumper is required.
// RGB outputs expose machine state; board-specific LED polarity is handled here.
module educpu_upduino_v31 (
    output logic led_r,
    output logic led_g,
    output logic led_b
);
    logic clk;
    logic reset;
    logic [3:0] reset_count = 4'hf;
    logic halted, trap;

    SB_HFOSC #(.CLKHF_DIV("0b10")) hfosc (
        .CLKHFPU(1'b1), .CLKHFEN(1'b1), .CLKHF(clk)
    );

    always_ff @(posedge clk) begin
        if (reset_count != 0)
            reset_count <= reset_count - 1'b1;
    end
    assign reset = (reset_count != 0);

    educpu_up5k_machine machine (
        .clk(clk), .reset(reset), .halted(halted), .trap(trap)
    );

    // Bring-up indicators: green=running, blue=halted, red=trap.
    assign led_r = trap;
    assign led_g = !halted && !trap;
    assign led_b = halted && !trap;
endmodule
