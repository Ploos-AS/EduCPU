# M8 — EduCPU Emulator

## Goal

M8 adds a second, independent implementation of the frozen EduCPU ISA v0. The emulator is a faithful machine implementation, not another teaching model and not a wrapper around the reference CPU.

The reference model remains the architectural oracle. The emulator must reach the same programmer-visible state for the same program and initial machine state.

## Independence rule

The emulator may share architecture constants and test vectors, but its instruction execution engine must not call `reference.educpu.CPU.step()`, inherit from that CPU, or copy reference-model execution state during a run. Differential testing is useful only when the two implementations can disagree.

## M8 machine state

The emulator exposes:

- R0-R7;
- PC;
- SP;
- FLAGS;
- 64 KiB byte-addressable memory;
- halted state;
- architectural trap state.

Reset follows ISA v0 exactly.

## Execution contract

For each instruction, the emulator must reproduce ISA v0 behavior for:

- instruction decoding and operand validation;
- PC advancement and control flow;
- arithmetic and logical flags;
- little-endian addresses;
- stack operations and CALL/RET byte order;
- SP-relative addressing;
- invalid opcode and invalid operand traps.

## Deterministic devices

ISA v0 defines byte memory semantics and reserves the top page for future machine conventions. M8 introduces a device abstraction without making a particular device part of ISA v0.

Initial device requirements:

- deterministic reads and writes;
- explicit reset;
- no wall-clock dependence in conformance tests;
- reproducible input streams;
- inspectable output;
- plain RAM behavior when no device is mapped.

Device behavior belongs to the emulator machine layer, not the CPU ISA.

## Debugger hooks

The emulator should expose hooks sufficient for tools without embedding a debugger into the execution core:

- before/after instruction callbacks;
- register/state snapshots;
- memory read/write observation;
- halt/trap observation;
- bounded run/step control.

## Differential qualification

Conformance tests execute the same vectors independently on the reference CPU and emulator and compare programmer-visible state.

Qualification grows in stages:

1. reset/NOP/HALT and traps;
2. moves, loads and stores;
3. arithmetic, flags, logic and shifts;
4. branches;
5. stack, CALL/RET and stack frames;
6. assembler-generated programs;
7. compiled EduC programs;
8. deterministic device tests.

Tests must compare observable results rather than internal implementation structure.

## Non-goals

M8 does not:

- change ISA v0;
- define FPGA timing;
- emulate a historical computer;
- add 32-bit architecture features;
- make the pedagogical micro-step model architectural;
- require nondeterministic peripherals.

## Qualification gate

M8 is complete when the independent emulator passes the ISA/conformance suite, differential tests against the reference CPU, deterministic device tests and representative EduASM/EduC program tests in CI.
