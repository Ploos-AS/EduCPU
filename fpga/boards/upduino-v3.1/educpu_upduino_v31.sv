// UPduino v3.x bring-up wrapper for EduCPU.
// Uses the iCE40 UltraPlus internal HF oscillator so no external clock jumper is required.
// RGB outputs expose machine state; board-specific LED polarity is handled here.
module educpu_upduino_v31 (
    input  logic reset_n,
    output logic led_r,
    output logic led_g,
    output logic led_b
);
    logic clk;
    logic halted, trap;

    SB_HFOSC #(.CLKHF_DIV("0b10")) hfosc (
        .CLKHFPU(1'b1), .CLKHFEN(1'b1), .CLKHF(clk)
    );

    educpu_up5k_machine machine (
        .clk(clk), .reset(!reset_n), .halted(halted), .trap(trap)
    );

    // Bring-up indicators: green=running, blue=halted, red=trap.
    assign led_r = trap;
    assign led_g = !halted && !trap;
    assign led_b = halted && !trap;
endmodule
