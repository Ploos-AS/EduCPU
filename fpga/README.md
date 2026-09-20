# EduCPU FPGA

Board-neutral FPGA implementation of standalone EduCPU ISA v0.

## M0 scope

M0 establishes synthesizable SystemVerilog project structure and the implementation contract before selecting a board. The core will contain architectural state, fetch/decode/execute, ALU, memory interface, branches, stack operations, HALT and invalid-opcode traps.

M0 does not claim synthesis or hardware bring-up yet. EduCPU is **own-PCB first**, with inexpensive development-board targets for bring-up and experimentation. Board-specific clock, memory, video, serial and GPIO wrappers remain outside the CPU core.

The first development-board target is the iCE40UP5K-based UPduino v3.1; iCEBreaker and compatible UP5K boards are secondary targets. The custom EduCPU PCB is the canonical hardware target.

See `docs/FPGA_M0.md` for the qualification plan.
