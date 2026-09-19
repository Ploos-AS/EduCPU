# EduCPU ABI v0

The ABI is intentionally small and visible enough to inspect by hand.

## Register convention

- R0: primary 8-bit return value and first argument.
- R1: second argument.
- R2: third argument.
- R3: fourth argument.
- R4-R6: callee-saved working registers.
- R7: caller-saved scratch register.
- PC and SP have architectural roles.
- FLAGS are caller-saved.

Functions with more than four byte arguments pass additional bytes on the stack. Multi-byte values are passed low byte first through consecutive argument locations.

## Calls

`CALL target` pushes the 16-bit return address. The callee returns with `RET`.

A leaf function that only uses R0-R3/R7 needs no prologue when it requires no local stack storage.

If a function changes R4-R6, it must PUSH the registers it uses and POP them in reverse order before RET.

Example:

```asm
add_two:
    ADD R0, R1
    RET
```

## Stack frames

ISA v0 deliberately has no frame-pointer register and no SP-relative load/store instruction. M4 therefore defines a **minimal ABI**, not an artificial pseudo-frame mechanism.

Functions may use PUSH/POP for saved registers and temporary byte values. Compiler-grade addressable local variables and stack arguments beyond the simple convention require either explicit stack access instructions or a future ABI/ISA revision.

This limitation is documented rather than hidden: it is a useful architecture-design lesson and will be reviewed before the EduC back end is frozen.

## Return values

- byte / bool / char: R0.
- 16-bit teaching values: R0 = low byte, R1 = high byte.
- no-value functions leave R0/R1 unspecified.

## Preservation summary

| State | Rule |
|---|---|
| R0-R3 | caller-saved / arguments |
| R4-R6 | callee-saved |
| R7 | caller-saved scratch |
| FLAGS | caller-saved |
| SP | restored by callee before RET |

## Recursion

CALL/RET are naturally recursive. A recursive function must preserve any live register values explicitly with PUSH/POP. Each recursive invocation gets its own bytes after `ENTER`, so recursive addressable locals are now supported within the signed stack-offset window.

## Educational goal

The ABI makes ownership visible: students can watch arguments enter registers, the return PC appear on the stack, saved registers move to memory, and the result return in R0.
