# M7 — Guided Teaching Environment

M7 turns the qualified EduCPU architecture and compiler pipeline into a structured learning path.

## Goal

A learner should be able to start with bits and bytes and progressively understand the complete path from source code to CPU state changes without needing to treat any stage as magic.

## Learning path

1. **Bits, bytes and hexadecimal** — binary representation, unsigned bytes and addresses.
2. **Machine state** — PC, SP, R0-R7, FLAGS and memory.
3. **Machine code** — instruction bytes, operands and little-endian addresses.
4. **EduASM** — labels, arithmetic, memory and control flow.
5. **Flags and branches** — comparisons and decisions.
6. **The stack** — PUSH/POP, CALL/RET and stack growth.
7. **Functions and ABI** — parameters, return values and stack frames.
8. **EduC syntax and types** — byte, bool, functions and structured control flow.
9. **AST and semantic analysis** — how source becomes a checked program model.
10. **EduIR** — explicit compiler operations before machine details.
11. **Compiler back end** — stack slots, generated EduASM and linking.
12. **Complete execution** — EduC source through machine bytes to observable CPU state.

## Teaching environment requirements

- Every lesson has an explicit learning objective.
- Prefer executable examples over static pseudocode.
- Show relevant state before and after each important step.
- Use the existing simulator, micro-step model and browser visualizer rather than inventing a second CPU model.
- Expose source, AST, EduIR, EduASM and machine bytes where they are pedagogically relevant.
- Clearly distinguish architectural behavior from explanatory implementation models.
- Keep examples deterministic and small enough to reason through manually.
- Important examples become automated tests where practical.
- Advanced topics are optional and must not obscure the base mental model.

## M7 implementation plan

- [x] define course structure and teaching-environment requirements
- [ ] create lesson document/template and first binary/hex lesson
- [ ] add guided example runner
- [ ] integrate compile-trace stages into guided views
- [ ] add simulator/visualizer launch path for lesson examples
- [ ] cover machine state, machine code and EduASM
- [ ] cover flags, branches, stack, calls and ABI
- [ ] cover EduC, AST, semantic analysis and EduIR
- [ ] cover compiler backend, object/link stages and final execution
- [ ] add lesson fixtures and automated checks
- [ ] M7 qualification
