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

## M3 — Simulator + debugger

Interactive execution; register/flag/memory/stack views; breakpoints/watchpoints; traces; fetch/decode/execute visualization; conceptual micro-operation stepping; source/assembly/byte correlation.

## M4 — Programs, stack, ABI + linking

Calling convention, stack frames, object representation, minimal linker, symbols/relocations, function and recursion lessons.

## M5 — EduC front end

Small EduC specification, lexer, parser, AST, semantic checks, simple documented IR, and inspection tools.

## M6 — EduC compiler back end

IR lowering, simple register allocation, code generation and complete source → AST → IR → assembly → bytes → execution correlation.

## M7 — Guided teaching environment

A coherent course from binary/hex through memory, registers, ALU/flags, machine code, assembly, control flow, stack/functions, assembler internals, compiler construction, and complete execution. Visualizations use real EduCPU state and traces.

## M8 — Optional advanced concepts

Interrupts, richer memory-mapped I/O, microcoded model, privilege concepts, conceptual virtual memory, simple pipelines/hazards, cache simulation, alternative ISA experiments, and optional FPGA/gate-level realization. These must not complicate the base CPU.
