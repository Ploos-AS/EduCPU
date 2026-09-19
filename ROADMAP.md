# EduCPU Roadmap

## M0 — Foundation
- [x] mission/scope, pedagogy principles, ISA envelope, toolchain, licensing and separation from EduK8

## M1 — ISA v0 + executable reference model
- [x] programmer-visible state, encoding, opcode map, flags, stack/calls, reference CPU and initial conformance tests

## M2 — EduASM
- [x] syntax, two-pass assembler, labels, diagnostics, educational listing, disassembler, tests and runnable example

## M3 — Pedagogical simulator + debugger
- [x] terminal-based interactive simulator/debugger foundation
- [x] instruction stepping and bounded run
- [x] register, PC, SP and FLAGS state view
- [x] decoded next-instruction view
- [x] per-instruction architectural state-change trace
- [x] memory inspection
- [x] breakpoints
- [x] memory watchpoints
- [x] reset
- [x] conceptual fetch/decode/execute/micro-operation teaching view
- [x] simulator tests
- [ ] rich datapath visualization / graphical teaching UI
- [ ] source-line correlation using assembler debug metadata
- [ ] interactive cycle/micro-operation state machine rather than explanatory sequence

M3 is intentionally iterative: the deterministic debugger/trace foundation is operational; richer visual teaching layers remain M3 work.

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
