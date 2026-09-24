// M10.1 experimental interrupt boundary.
//
// This module deliberately does not modify educpu_core. It defines the
// capability-gated external IRQ contract that a future experimental core
// implementation must satisfy while the qualified ISA v0 RTL stays frozen.
module educpu_experimental_irq (
    input  logic        clk,
    input  logic        reset,
    input  logic        irq_request,
    input  logic [15:0] irq_vector,
    input  logic        instruction_boundary,
    input  logic        cpu_trap,
    input  logic        iret_complete,
    output logic        irq_pending,
    output logic        irq_enabled,
    output logic        in_interrupt,
    output logic        irq_accept,
    output logic [15:0] accepted_vector
);
    always_ff @(posedge clk) begin
        if (reset) begin
            irq_pending    <= 1'b0;
            irq_enabled    <= 1'b1;
            in_interrupt   <= 1'b0;
            irq_accept     <= 1'b0;
            accepted_vector <= 16'h0000;
        end else begin
            irq_accept <= 1'b0;

            if (irq_request)
                irq_pending <= 1'b1;

            if (iret_complete && in_interrupt) begin
                in_interrupt <= 1'b0;
                irq_enabled  <= 1'b1;
            end

            if (instruction_boundary && irq_enabled && !in_interrupt &&
                !cpu_trap && (irq_pending || irq_request)) begin
                irq_pending     <= 1'b0;
                irq_enabled     <= 1'b0;
                in_interrupt    <= 1'b1;
                irq_accept      <= 1'b1;
                accepted_vector <= irq_vector;
            end
        end
    end
endmodule
