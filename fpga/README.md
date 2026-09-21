# EduCPU FPGA

Board-neutral FPGA implementation of standalone EduCPU ISA v0.

## M0 scope

M0 establishes synthesizable SystemVerilog project structure and the implementation contract before selecting a board. The core will contain architectural state, fetch/decode/execute, ALU, memory interface, branches, stack operations, HALT and invalid-opcode traps.

M0 established the board-neutral implementation contract. EduCPU now uses **UPduino v3.1 as its canonical physical FPGA reference hardware**. Board-specific clock, memory, serial and GPIO wrappers remain outside the CPU core so the architecture stays portable.

The primary hardware target is the iCE40UP5K-based UPduino v3.1. Its wrapper, constraints, synthesis and physical qualification define the canonical EduCPU hardware path. iCEBreaker and compatible UP5K boards may be supported as secondary targets. A custom EduCPU PCB is an optional future goal and is not required for EduCPU releases.

See `docs/FPGA_M0.md` for the qualification plan.
