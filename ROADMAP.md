# EduCPU Roadmap

## M0 — Foundation
- [x] mission/scope, pedagogy principles, ISA envelope, toolchain, licensing and separation from EduK8

## M1 — ISA v0 + executable reference model
- [x] programmer-visible state, encoding, opcode map, flags, stack/calls, reference CPU and initial conformance tests

## M2 — EduASM
- [x] EduASM v0 syntax
- [x] two-pass label-aware assembler
- [x] assembler diagnostics and range checks
- [x] educational address/byte/source listing
- [x] disassembler
- [x] assembler/disassembler tests
- [x] assembled program executed on reference CPU
- [x] introductory sum example

Exit: learners can write symbolic EduCPU programs, inspect their exact machine bytes, disassemble binaries and execute assembled output on the M1 reference CPU.

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
A separate faithful machine implementation with binary loading, deterministic devices, debugger hooks, CI/headless operation, conformance and differential testing. The simulator teaches how the machine works; the emulator behaves like the machine.

## M9 — FPGA realization
Synthesizable realization of the frozen architecture, with a concrete microarchitecture/RTL, ISA-vector qualification, accessible FPGA target, memory/I/O/debug interfaces and execution of EduASM binaries. FPGA realizes EduCPU; it does not define it.

## M10 — Advanced and experimental concepts
Optional interrupts, richer I/O, microcode, privilege concepts, conceptual VM, pipelines/hazards, cache and alternative architecture experiments kept separate from the beginner core.
