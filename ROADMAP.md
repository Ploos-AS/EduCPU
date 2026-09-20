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
- [x] documented simple IR
- [x] AST to IR lowering
- [x] IR validation and inspection CLI
- [x] M5 front-end qualification — CI green on Python 3.11, 3.12 and 3.13

M5 covers source syntax, semantic meaning, explicit EduIR lowering and independent IR validation. The complete front-end pipeline is qualified in CI.

## M6 — EduC compiler back end
- [x] documented backend strategy
- [x] EduIR to EduASM code generator
- [x] ABI register parameters and return-value mapping
- [x] stack-backed parameters, locals and temporaries
- [x] constants, copies and byte add/sub
- [x] comparisons and control flow
- [x] function-local label namespacing
- [x] function calls, void calls and recursion
- [x] generated EduASM object assembly and EduLink execution tests
- [x] complete EduC to executable CLI pipeline
- [x] source to AST to IR to assembly to bytes to execution correlation
- [x] M6 qualification — 82 tests PASS on Python 3.11, 3.12 and 3.13; see docs/M6_QUALIFICATION.md

## M7 — Guided teaching environment — COMPLETE
Course from binary/hex through compiler construction and complete execution. Final qualification: `docs/M7_QUALIFICATION.md`.
- [x] course structure and teaching-environment requirements
- [x] bilingual Markdown course framework and lesson template
- [x] GitHub Pages generation pipeline
- [x] lessons 01–15 in English and Norwegian
- [x] compile-trace integration in guided end-to-end lesson
- [x] simulator/visualizer lesson integration
- [x] complete progressive course coverage
- [x] executable lesson fixtures and checks
- [x] M7 course-content qualification — CI and Pages PASS; see docs/M7_QUALIFICATION.md
- [x] separate bilingual exercise solutions
- [x] EduAVR further-learning path on course landing pages
- [x] bilingual EPUB generation + validation — Ebooks #6 PASS with metadata, deterministic covers and epubcheck
- [x] Kindle distribution workflow documented from generated EPUB; final Amazon preview remains a release-time manual gate
## M8 — EduCPU emulator
Separate faithful implementation, deterministic devices, debugger hooks and differential/conformance testing. See `docs/M8_EMULATOR.md`.
- [x] define emulator architecture, independence rule and qualification gate
- [ ] implement independent ISA v0 execution core
- [ ] add reset/NOP/HALT and trap conformance
- [ ] add data movement and memory conformance
- [ ] add arithmetic/flags/logic/shift conformance
- [ ] add branch conformance
- [ ] add stack/CALL/RET/frame conformance
- [ ] add debugger hooks and bounded execution
- [ ] add deterministic device abstraction and tests
- [ ] differential-test EduASM programs against reference CPU
- [ ] differential-test compiled EduC programs against reference CPU
- [ ] M8 qualification — CI green
## M9 — FPGA realization
Synthesizable realization of frozen architecture and qualification against ISA vectors.
## M10 — Advanced and experimental concepts
Optional interrupts, richer I/O, microcode, privilege, VM, pipelines/hazards, cache and alternative architecture experiments.
