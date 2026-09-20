# EduCPU FPGA

Board-neutral FPGA implementation of standalone EduCPU ISA v0.

## M0 scope

M0 establishes synthesizable SystemVerilog project structure and the implementation contract before selecting a board. The core will contain architectural state, fetch/decode/execute, ALU, memory interface, branches, stack operations, HALT and invalid-opcode traps.

M0 does not claim synthesis or hardware bring-up yet. Board-specific clock, memory, video, serial and GPIO wrappers remain outside the CPU core.

See `docs/FPGA_M0.md` for the qualification plan.
