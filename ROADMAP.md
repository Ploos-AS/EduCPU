# EduCPU Roadmap

## M0 — Foundation
- [x] mission/scope, pedagogy principles, ISA envelope, toolchain, licensing and separation from EduK8

## M1 — ISA v0 + executable reference model
- [x] programmer-visible state, encoding, opcode map, flags, stack/calls, reference CPU and initial conformance tests

## M2 — EduASM
- [x] syntax, two-pass assembler, labels, diagnostics, educational listing, disassembler, tests and runnable example

## M3 — Pedagogical simulator + debugger
- [x] terminal and graphical teaching environments
- [x] source → bytes → instruction → micro-step → architectural state correlation
- [x] datapath visualization and shared reference semantics

## M4 — Programs, stack, ABI + linking
- [x] ABI v0 calling/return and preservation conventions
- [x] explicit SP-relative stack-frame ISA: LOADS/STORES/ENTER/LEAVE
- [x] stack-frame/local-variable example
- [x] transparent object-format v0
- [x] EduASM .export/.import syntax
- [x] EduASM object emission (`.eo`)
- [x] exported and object-local symbols
- [x] abs16 little-endian relocations
- [x] relocation of local labels when objects move
- [x] minimal EduLink linker and map support
- [x] duplicate/undefined-symbol diagnostics
- [x] complete eduasm -c → .eo → edulink → executable test path
- [x] linked multi-object function-call example
- [ ] recursive stack-frame example and qualification
- [ ] ABI/ISA v0 freeze review

M4 now has a real inspectable multi-file toolchain. The remaining work is to exercise recursion/frames and review the ABI/ISA together before freezing the interface used by EduC.

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
