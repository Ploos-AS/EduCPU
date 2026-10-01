# M10.3 — Microcode and Control

M10.3 teaches the question: **How does the control unit turn one machine instruction into a sequence of internal actions?**

The goal is explanatory visibility, not novelty. A learner who already understands the ISA should be able to predict and inspect the internal work required to execute an instruction.

## Scope

M10.3 begins with a conceptual micro-operation model. It does **not** replace the frozen ISA-v0 CPU or claim that the existing RTL is a microcoded implementation.

The first model exposes operations such as:

- fetch an instruction byte;
- decode an opcode;
- fetch operand bytes;
- read registers;
- select an ALU operation;
- read or write memory;
- update PC or SP;
- write a register;
- update FLAGS;
- commit architectural state.

This creates a bridge from ISA semantics to datapath and control.

## Teaching progression

1. **NOP/HALT** — control flow with almost no datapath work.
2. **MOV/LDI** — move a byte through the datapath.
3. **ADD/SUB/CMP** — ALU selection, result and FLAGS.
4. **LOAD/STORE** — address selection and memory transfer.
5. **Jumps/branches** — conditional PC update.
6. **PUSH/POP/CALL/RET** — multi-step state changes involving SP and memory.
7. **IN/OUT** — external transfer and wait-state handshake.
8. Compare hardwired control with a genuinely microprogrammed experimental controller.

## Predict → run → inspect

For each instruction the learner should first predict:

- which architectural operands must be read;
- which internal value moves where;
- which state may change;
- which state must remain unchanged;
- the ordering constraints between operations.

The teaching simulator can then show the conceptual plan before executing the instruction and the actual architectural changes afterward.

## Terminology boundary

A **micro-operation** is a small explanatory state-transfer/control action.

A **microinstruction** is an encoded control word in a microprogrammed control unit.

A **microprogram** is a sequence of microinstructions used to implement an ISA instruction.

EduCPU will keep these terms distinct. The conceptual plans introduced first are micro-operation plans, not hidden claims that ISA v0 uses a microcode ROM.

## First control-word format

The first executable microprogrammed model uses a deliberately readable 24-bit control word. Fields select a source, destination, ALU operation, memory read/write, PC increment and next-control action. Unused bits are reserved rather than compressed away.

The shared fetch microprogram is visible as two microinstructions: request memory at PC, then transfer the returned byte to IR, increment PC and dispatch. NOP returns to fetch; HALT enters the halted control state. A step-visible microsequencer exposes `phase`, `micro_pc`, the dispatched opcode and the encoded control word at every transition. Dispatch requires an explicit IR value and rejects opcodes that do not yet have a microprogram.

This representation is intentionally educational. A later RTL encoding may optimize the bit layout, but it must preserve a way to inspect the same control decisions.

## Qualification strategy

M10.3 will qualify in stages:

- deterministic conceptual plans for representative ISA-v0 instruction families;
- tests proving plans decode operands consistently with the ISA;
- teaching-simulator presentation;
- a separate experimental microinstruction/control-word format;
- a microsequencer and control store;
- execution comparison against the reference architecture;
- optional experimental RTL after software semantics are understood.

The frozen ISA-v0 reference CPU and `fpga/rtl/educpu_core.sv` remain unchanged.
