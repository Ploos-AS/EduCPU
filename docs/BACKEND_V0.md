# EduC backend strategy v0

M6 lowers validated EduIR to EduASM while keeping storage, calls and control flow visible to a learner.

## Stack-backed value model

The v0 backend deliberately favors clarity over optimization.

- EduC parameters 0..3 enter in R0..R3 according to ABI v0.
- Every parameter, named local and IR temporary receives a one-byte stack slot.
- A function emits `ENTER n`, saves its register parameters into their slots, and leaves through one common epilogue using `LEAVE n` and `RET`.
- R7 and R6 are scratch registers used while moving values between stack slots and machine operations.
- The v0 frame is limited to 128 slots because `LOADS`/`STORES` use the positive half of the signed 8-bit SP-relative offset range.
- Keeping live values in stack slots makes values naturally survive ordinary calls and recursive calls.

## Lowering

- `const` becomes `MOVI` followed by a stack store.
- `copy` becomes stack load/store.
- `add` and `sub` load operands into R7/R6, execute the ALU operation and store the result.
- `not` and comparisons materialize canonical boolean values 0 or 1.
- EduC byte comparisons are unsigned. After `CMP a,b`, C means no borrow (`a >= b`) and Z means equal.
- EduIR labels are namespaced by function before emission, so independently generated labels cannot collide in a multi-function object.
- `jmp` and `br` lower to the ISA jump instructions.
- Every return jumps to the function's common epilogue.

## Calls and recursion

- Call arguments are evaluated by EduIR and loaded left-to-right into R0..R3.
- `CALL` targets the function symbol directly.
- A value-returning call stores R0 into the destination stack slot after return.
- A void call emits no result store.
- The caller's stack frame remains active beneath the return address and callee frame, so recursion uses the same mechanism as ordinary calls.
- The callee restores SP before `RET`; a balanced top-level invocation therefore returns SP to its entry value.

This design is intentionally unoptimized. Later work may introduce allocation or optimization passes, but they must preserve an inspectable path from EduIR values to generated machine behavior.
