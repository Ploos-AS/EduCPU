# EduCPU Roadmap

## M0 — Foundation
- [x] mission/scope, pedagogy principles, ISA envelope, toolchain, licensing and separation from EduK8
## M1 — ISA v0 + executable reference model
- [x] programmer-visible state, encoding, opcode map, flags, stack/calls, reference CPU and conformance tests
## M2 — EduASM
- [x] syntax, assembler/disassembler, diagnostics, listings, tests and examples
## M3 — Pedagogical simulator + debugger
- [x] terminal/graphical teaching environments and source to datapath to state correlation
## M4 — Programs, stack, ABI + linking
- [x] frozen ISA/ABI v0, stack frames/recursion, objects, symbols, relocations and EduLink

## M5 — EduC front end
- [x] EduC v0 language specification
- [x] lexer with source positions
- [x] recursive-descent parser and inspectable AST
- [x] byte/bool/void, functions, locals, assignment, return, if/else, while and expressions
- [x] function symbol table and duplicate-function checks
- [x] parameter/local symbol checks and shadowing rejection
- [x] unknown variable/function diagnostics
- [x] byte/bool expression type checking
- [x] function-call arity and argument-type checking
- [x] if/while bool-condition enforcement
- [x] return type checking
- [x] conservative all-path return validation
- [x] CLI semantic check: educ --check
- [x] semantic-analysis tests
- [ ] documented simple IR
- [ ] AST to IR lowering
- [ ] IR validation and inspection CLI
- [x] M5 front-end qualification — CI green on Python 3.11, 3.12 and 3.13

M5 now covers source syntax, semantic meaning, explicit EduIR lowering and independent IR validation. The complete front-end pipeline is qualified in CI. M5 is complete; M6 starts with lowering validated EduIR to EduASM.

## M6 — EduC compiler back end
IR lowering, simple register allocation, code generation and complete source to AST to IR to assembly to bytes to execution correlation.
## M7 — Guided teaching environment
Course from binary/hex through compiler construction and complete execution.
## M8 — EduCPU emulator
Separate faithful implementation, deterministic devices, debugger hooks and differential/conformance testing.
## M9 — FPGA realization
Synthesizable realization of frozen architecture and qualification against ISA vectors.
## M10 — Advanced and experimental concepts
Optional interrupts, richer I/O, microcode, privilege, VM, pipelines/hazards, cache and alternative architecture experiments.
