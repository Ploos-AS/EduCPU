// M10 experimental CPU interrupt interface.
//
// This is the integration contract between an experimental CPU implementation
// and educpu_experimental_irq. It intentionally leaves educpu_core unchanged.
interface educpu_experimental_cpu_if;
    logic        instruction_boundary;
    logic        trap;
    logic        halted;
    logic [15:0] pc;
    logic [15:0] sp;
    logic [7:0]  flags;

    // IRQ controller -> experimental CPU
    logic        irq_accept;
    logic [15:0] irq_vector;

    // Experimental CPU -> IRQ controller
    logic        iret_complete;

    // Entry contract: when irq_accept is observed at an instruction boundary,
    // the CPU must save PC then FLAGS using the documented M10.1 stack order,
    // clear HALT, and transfer PC to irq_vector.
    //
    // Return contract: experimental IRET (0xF0) restores FLAGS then PC and
    // pulses iret_complete after architectural state has been restored.
    modport cpu (
        input  irq_accept, irq_vector,
        output instruction_boundary, trap, halted, pc, sp, flags, iret_complete
    );

    modport irq (
        input  instruction_boundary, trap, halted, pc, sp, flags, iret_complete,
        output irq_accept, irq_vector
    );
endinterface
