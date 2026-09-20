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


## Pedagogical direction: no magic boxes

The course takes inspiration from the general bottom-up teaching idea of making a computer understandable one layer at a time. It does not copy the text, illustrations, examples or presentation of any external book.

A recurring question is:

> **How does EduCPU know?**

When a new abstraction is introduced, the course should explain what actually exists below it. The CPU does not inherently know what a variable, function, loop or source-language type is. The course progressively exposes the transformations and machine state that make those abstractions work.

## Two complementary journeys

### Build upward

The learner first constructs a mental model from simple mechanisms toward software:

`bits -> logic -> storage/registers -> ALU -> datapath/control -> CPU -> instructions -> machine code -> assembly -> functions/ABI -> compiler -> EduC`

This path should eventually connect directly to the M9 FPGA realization, while clearly distinguishing explanatory logic models from the frozen ISA.

### Trace downward

Once the software layers are understood, the learner follows programs in the other direction:

`EduC -> AST -> semantic analysis -> EduIR -> generated EduASM -> object/relocations -> linker -> machine bytes -> CPU execution -> register/memory changes`

The same small programs should be reused across layers where practical so the learner can see abstractions being introduced and removed.

## Lesson pattern

Lessons should normally contain:

1. **What is it?** — plain-language concept and terminology.
2. **Why do we need it?** — the problem the concept solves.
3. **How does EduCPU do it?** — concrete architecture/tool behavior.
4. **Worked example** — small enough to reason through manually.
5. **Run and observe** — use real EduCPU tools where applicable.
6. **Explain the result** — connect observed state to the concept.
7. **Exercises** — understanding, coding and exploration.
8. **Check your understanding** — a short self-check.

Exercises should include prediction before execution whenever useful.

## Course publishing model

Markdown is the single source of truth for course content. Generated HTML is a publication artifact and must not become an independently edited source.

The course will use parallel English and Norwegian content and publish generated HTML through GitHub Pages. CI should validate course structure, links and executable examples before publication.

Real screenshots and diagrams derived from the actual EduCPU tools should be preferred when showing concrete interfaces or implementation behavior.
