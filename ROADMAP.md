# EduCPU Roadmap

## M0 — Foundation
- [x] mission/scope, pedagogy principles, ISA envelope, toolchain, licensing and separation from EduK8

## M1 — ISA v0 + executable reference model
- [x] programmer-visible state, encoding, opcode map, flags, stack/calls, reference CPU and initial conformance tests

## M2 — EduASM
- [x] syntax, two-pass assembler, labels, diagnostics, educational listing, disassembler, tests and runnable example

## M3 — Pedagogical simulator + debugger
- [x] terminal interactive simulator/debugger
- [x] instruction stepping, run, state, memory, breakpoints and watchpoints
- [x] architectural state-change trace
- [x] conceptual fetch/decode/execute model
- [x] interactive instruction-specific micro-step state machine
- [x] EduASM address/byte/source debug metadata
- [x] source-line correlation
- [x] browser-based graphical teaching UI
- [x] PC → memory → decode → registers ↔ ALU → FLAGS datapath view
- [x] active datapath highlighting driven by real MicroStepper phases
- [x] graphical register/control/source/instruction state
- [x] shared reference CPU semantics across terminal and browser views
- [x] simulator, micro-step, source-correlation and visualizer tests

Exit: M3 provides a coherent source → bytes → instruction → conceptual datapath phase → architectural state teaching path in both terminal and graphical views.

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
