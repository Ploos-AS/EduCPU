# EduCPU Roadmap

## M0 — Foundation

- [x] mission and scope
- [x] pedagogy-first principles
- [x] ISA design envelope
- [x] toolchain architecture
- [x] roadmap
- [x] MIT license
- [x] separation from EduK8

Exit: the repository defines what EduCPU is, what it is not, and what M1 must decide.

## M1 — ISA v0 + executable reference model

Freeze programmer-visible state, registers/flags, endianness, encoding, opcode map, addressing modes, reset/invalid-instruction behavior, arithmetic/flag semantics; implement a minimal reference model and golden conformance vectors.

## M2 — EduASM

Specify EduASM; implement assembler, labels/constants, diagnostics, disassembler, annotated source-to-byte output, round-trip tests, and introductory examples.

## M3 — Pedagogical simulator + debugger

Build the primary teaching simulator. Interactive execution; register/flag/memory/stack views; breakpoints/watchpoints; traces; datapath and fetch/decode/execute visualization; conceptual micro-operation/cycle stepping; source/assembly/byte correlation.

The simulator is intentionally allowed to expose idealized teaching views that are not required to correspond to one concrete hardware implementation.

## M4 — Programs, stack, ABI + linking

Calling convention, stack frames, object representation, minimal linker, symbols/relocations, function and recursion lessons.

## M5 — EduC front end

Small EduC specification, lexer, parser, AST, semantic checks, simple documented IR, and inspection tools.

## M6 — EduC compiler back end

IR lowering, simple register allocation, code generation and complete source → AST → IR → assembly → bytes → execution correlation.

## M7 — Guided teaching environment

A coherent course from binary/hex through memory, registers, ALU/flags, machine code, assembly, control flow, stack/functions, assembler internals, compiler construction, and complete execution. Visualizations use real EduCPU state and traces.

## M8 — EduCPU emulator

Build a separate emulator focused on faithfully executing the frozen EduCPU architectural specification rather than providing the simulator's pedagogical visualization.

Planned work:

- independent ISA execution engine where practical;
- binary/program loading;
- deterministic virtual memory and I/O devices;
- terminal/console execution;
- debugger hooks;
- conformance against the same golden ISA vectors as the reference model;
- differential testing between reference model, simulator, and emulator;
- suitable command-line/headless mode for CI.

This distinction is deliberate: the simulator teaches how the machine works; the emulator behaves like the machine.

## M9 — FPGA realization

Create a synthesizable hardware realization of the frozen EduCPU architecture without allowing FPGA implementation convenience to retroactively distort the educational ISA.

Planned work:

- define a concrete EduCPU microarchitecture;
- RTL implementation;
- ALU, register file, control unit, PC/SP, flags and memory interface;
- simulation/testbench qualification against ISA conformance vectors;
- synthesis for at least one accessible FPGA development board;
- memory and basic memory-mapped I/O;
- serial/debug interface;
- run EduASM-produced binaries unchanged where architectural facilities permit;
- compare architectural traces against the software reference implementation.

The FPGA implementation is a realization of EduCPU, not the definition of EduCPU.

## M10 — Advanced and experimental concepts

Optional isolated extensions may explore interrupts and richer I/O, microcoded implementations, privilege concepts, conceptual virtual memory, simple pipelines and hazards, cache simulation, alternative implementation strategies, and alternative ISA experiments.

Advanced experiments must remain separable from the small base architecture so that EduCPU stays understandable for beginners.
