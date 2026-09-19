# EduCPU Roadmap

## M0 — Foundation
- [x] mission/scope, pedagogy principles, ISA envelope, toolchain, licensing and separation from EduK8
## M1 — ISA v0 + executable reference model
- [x] programmer-visible state, encoding, opcode map, flags, stack/calls, reference CPU and initial conformance tests
## M2 — EduASM
- [x] syntax, assembler/disassembler, diagnostics, listings, tests and examples
## M3 — Pedagogical simulator + debugger
- [x] terminal/graphical teaching environments and source → datapath → state correlation
## M4 — Programs, stack, ABI + linking
- [x] frozen ISA/ABI v0, stack frames/recursion, objects, symbols, relocations and EduLink

## M5 — EduC front end
- [x] EduC v0 language scope/specification
- [x] byte, bool and void type syntax
- [x] function definitions and up to four ABI-aligned parameters
- [x] local declarations and assignment syntax
- [x] return, if/else and while syntax
- [x] literals, names, calls, unary !, arithmetic and comparisons
- [x] lexer with source positions
- [x] recursive-descent parser
- [x] explicit inspectable AST
- [x] token/AST CLI inspection
- [x] initial front-end tests and example
- [ ] semantic analysis: symbols, scopes and duplicate declarations
- [ ] type checking and return-path validation
- [ ] documented simple IR
- [ ] AST → IR lowering and IR inspection

M5 keeps EduC intentionally smaller than C. The front end should teach each compiler stage rather than hide it.

## M6 — EduC compiler back end
IR lowering, simple register allocation, code generation and complete source → AST → IR → assembly → bytes → execution correlation.
## M7 — Guided teaching environment
Course from binary/hex through compiler construction and complete execution.
## M8 — EduCPU emulator
Separate faithful implementation, deterministic devices, debugger hooks and differential/conformance testing.
## M9 — FPGA realization
Synthesizable realization of frozen architecture and qualification against ISA vectors.
## M10 — Advanced and experimental concepts
Optional interrupts, richer I/O, microcode, privilege, VM, pipelines/hazards, cache and alternative architecture experiments.
