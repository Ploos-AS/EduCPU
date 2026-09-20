# EduC backend strategy v0

M6 lowers validated EduIR to EduASM while keeping every storage decision visible.

## First backend slice

The first executable slice deliberately targets leaf functions with byte/bool parameters, constants, copies, addition/subtraction and returns. It establishes the mapping rules before calls, stack locals and control flow are added.

- EduC parameter 0..3 enters in R0..R3 according to ABI v0.
- IR temporaries are assigned from R7, R6, R5, R4 for the initial slice.
- A named parameter remains in its ABI register until copied.
- `const` becomes `MOVI`.
- `copy` becomes `MOV`.
- `add` / `sub` copy the left operand into the destination register and apply `ADD` / `SUB`.
- a non-void `ret value` moves the value to R0 when needed, then emits `RET`.

This is intentionally not yet a general allocator. M6 will next introduce stack-backed locals/temporaries, control flow and calls. The small first slice makes generated assembly easy to inspect and test against the frozen ABI.
