# M10.1 interrupt experiment

Status: **proposal**

Capability: `experimental.interrupts`

This document defines the first interrupt experiment without changing frozen ISA v0 behaviour.

## Goals

Interrupts should teach asynchronous control transfer with the smallest observable mechanism possible. The design is deterministic, single-level initially, and explicit about saved state.

## Architectural state

The experimental machine adds state outside the ISA v0 CPU:

- `irq_pending` — an interrupt request is waiting;
- `irq_enabled` — global interrupt acceptance flag;
- `irq_vector` — 16-bit handler address;
- `in_interrupt` — handler context is active.

None of these fields exist in the baseline `isa-v0` profile.

## Acceptance point

An IRQ is accepted only between completed instructions. It is never taken halfway through an ISA v0 instruction.

The reference machine accepts an interrupt when:

1. `experimental.interrupts` is present;
2. `irq_pending` is true;
3. `irq_enabled` is true;
4. the CPU is not trapped;
5. `in_interrupt` is false.

A halted CPU may be awakened by an accepted IRQ. A trapped CPU cannot be interrupted.

## Entry semantics

On acceptance:

1. clear `irq_pending`;
2. clear `halted` if set;
3. push the current 16-bit PC using the existing CALL-compatible return-address byte order;
4. push the current FLAGS byte;
5. set `in_interrupt`;
6. disable further IRQ acceptance;
7. set PC to `irq_vector`.

This produces deterministic single-level interrupt handling and reuses concepts students already learn from CALL/RET and the stack.

## Return semantics

M10.1 requires a dedicated experimental interrupt-return operation because ordinary RET does not restore FLAGS or interrupt state. For the experimental profile it is assigned opcode **0xF0** (`IRET`). This encoding is outside the frozen ISA v0 instruction set: baseline ISA v0 continues to trap on 0xF0.

Interrupt return (`IRET`, experimental opcode `0xF0`) will:

1. restore FLAGS;
2. restore PC;
3. clear `in_interrupt`;
4. re-enable interrupt acceptance.

## Request model

The reference API will expose a request operation rather than modeling electrical timing. Multiple requests while one is pending coalesce into one pending IRQ in M10.1. Priority, masking, multiple vectors and nested interrupts are future experiments.

## Compatibility

The baseline ISA v0 machine has no interrupt state and no interrupt-return opcode. Existing ISA v0 byte streams retain exactly their current meaning.

The experimental capability must be explicitly selected. No assembler syntax or opcode is added to baseline EduASM as part of the proposal stage.

## Qualification

Before this experiment advances beyond proposal:

- baseline ISA v0 regression remains green;
- IRQ entry is tested at an instruction boundary;
- HALT wake-up is tested;
- disabled IRQ remains pending without changing CPU state;
- trapped CPU rejects IRQ entry;
- return restores PC and FLAGS;
- nested IRQ acceptance is prevented.
