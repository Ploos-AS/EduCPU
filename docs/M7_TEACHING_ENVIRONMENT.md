# M7 — Guided Teaching Environment

M7 turns the qualified EduCPU architecture and compiler pipeline into a structured learning path.

## Goal

A learner should be able to start with bits and bytes and progressively understand the complete path from source code to CPU state changes without needing to treat any stage as magic.

## Learning path

1. **Bits, bytes and hexadecimal**
2. **Logic and storing information**
3. **What is a CPU?**
4. **Registers, memory and machine state**
5. **Instructions and machine code**
6. **EduASM and what an assembler does**
7. **Arithmetic, flags and branches**
8. **The stack**
9. **Functions, CALL/RET and the ABI**
10. **What is a compiler?**
11. **EduC, AST and semantic analysis**
12. **EduIR and code generation**
13. **Objects, relocations and linking**
14. **Complete EduC-to-execution trace**
15. **How a CPU is built: ALU, datapath, control and the road to FPGA**

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
- [x] create lesson document/template and first binary/hex lesson
- [ ] add guided example runner
- [x] integrate compile-trace stages into guided lessons
- [ ] add simulator/visualizer launch path for lesson examples
- [x] cover machine state, machine code and EduASM
- [x] cover flags, branches, stack, calls and ABI
- [x] cover EduC, AST, semantic analysis and EduIR
- [x] cover compiler backend, object/link stages and final execution
- [x] add lesson fixtures and automated checks
- [x] M7 qualification\n- [x] separate bilingual exercise solutions


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
