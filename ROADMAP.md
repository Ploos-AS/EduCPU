# EduCPU Roadmap

## M0 — Foundation

- [x] mission and scope
- [x] pedagogy-first principles
- [x] ISA design envelope
- [x] toolchain architecture
- [x] roadmap
- [x] MIT license
- [x] separation from EduK8

## M1 — ISA v0 + executable reference model

- [x] freeze programmer-visible state
- [x] eight general 8-bit registers R0-R7
- [x] 16-bit PC and SP
- [x] Z/N/C/V flags
- [x] little-endian 16-bit values
- [x] regular byte-oriented instruction encoding
- [x] initial opcode map and addressing modes
- [x] reset, HALT, invalid-opcode and invalid-operand behavior
- [x] exact arithmetic/flag semantics
- [x] downward-growing stack and CALL/RET semantics
- [x] executable Python architectural reference model
- [x] initial conformance tests

Exit: ISA v0 has documented semantics and an executable architectural oracle suitable for expanding golden conformance vectors.

## M2 — EduASM

Specify EduASM; implement assembler, labels/constants, diagnostics, disassembler, annotated source-to-byte output, round-trip tests, and introductory examples.

## M3 — Pedagogical simulator + debugger

Build the primary teaching simulator. Interactive execution; register/flag/memory/stack views; breakpoints/watchpoints; traces; datapath and fetch/decode/execute visualization; conceptual micro-operation/cycle stepping; source/assembly/byte correlation.

The simulator may expose idealized teaching views that are not required to correspond to one concrete hardware implementation.

## M4 — Programs, stack, ABI + linking

Calling convention, stack frames, object representation, minimal linker, symbols/relocations, function and recursion lessons.

## M5 — EduC front end

Small EduC specification, lexer, parser, AST, semantic checks, simple documented IR, and inspection tools.

## M6 — EduC compiler back end

IR lowering, simple register allocation, code generation and complete source → AST → IR → assembly → bytes → execution correlation.

## M7 — Guided teaching environment

A coherent course from binary/hex through memory, registers, ALU/flags, machine code, assembly, control flow, stack/functions, assembler internals, compiler construction, and complete execution.

## M8 — EduCPU emulator

Build a separate emulator focused on faithfully executing the frozen EduCPU architectural specification. Include binary loading, deterministic devices, debugger hooks, CI/headless operation, conformance testing and differential testing against the reference model and simulator.

The simulator teaches how the machine works; the emulator behaves like the machine.

## M9 — FPGA realization

Create a synthesizable hardware realization of the frozen EduCPU architecture. Define a concrete microarchitecture and RTL, qualify it against ISA vectors, synthesize for at least one accessible FPGA board, provide memory/basic I/O/debug interfaces, and run EduASM-produced binaries.

The FPGA implementation is a realization of EduCPU, not the definition of EduCPU.

## M10 — Advanced and experimental concepts

Optional isolated extensions may explore interrupts, richer I/O, microcoded implementations, privilege concepts, conceptual virtual memory, pipelines/hazards, cache simulation and alternative ISA/implementation experiments without complicating the base teaching architecture.
