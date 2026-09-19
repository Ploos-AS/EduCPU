# EduCPU Design Principles

1. **Pedagogy first.** Features exist because they teach something useful.
2. **The whole core must be learnable.** The base CPU stays small enough for a complete mental model.
3. **Regularity beats exceptions.** Prefer orthogonal registers, consistent operands, predictable flags, few addressing modes, and regular encodings.
4. **Machine code must be approachable.** Instruction bytes should visibly reinforce EduASM concepts.
5. **State changes must be observable.** Tools expose instruction, PC, SP, registers, flags, memory effects and branch decisions.
6. **Determinism by default.** Identical initial state and inputs produce identical transitions.
7. **Progressive disclosure.** Teach registers, arithmetic, memory, branches, stack, functions, I/O and interrupts in layers.
8. **Do not teach accidental complexity.** Historical quirks belong in comparisons, not the base architecture.
9. **Simplify without lying.** Clearly distinguish ISA guarantees from explanatory implementation models.
10. **Tools are teaching instruments.** Human-readable and machine-readable traces are first-class outputs.
11. **Specifications before clever implementations.** Observable behavior is defined independently of a simulator.
12. **Documentation is testable.** Specification examples should become executable fixtures where practical.
