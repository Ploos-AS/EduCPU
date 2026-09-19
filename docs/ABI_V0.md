# EduCPU ABI v0

Status: **frozen for EduC v0**. Changes that break this contract require an explicit ABI revision.

The ABI is intentionally small and inspectable by hand.

## Register convention

- R0: first argument and primary 8-bit return value.
- R1: second argument; high byte of a 16-bit return value.
- R2: third argument.
- R3: fourth argument.
- R4-R6: callee-saved working registers.
- R7: caller-saved scratch register.
- PC and SP retain their architectural roles.
- FLAGS are caller-saved.

The first four byte arguments use R0-R3. Additional stack arguments are reserved for a later, explicitly specified extension; EduC v0 must not silently invent a layout for them.

## Calls and returns

`CALL target` pushes the 16-bit return PC high byte then low byte and transfers control. `RET` pops low byte then high byte and restores PC.

A leaf function using only caller-saved registers needs no prologue. A function modifying R4-R6 must PUSH the registers it changes and POP them in reverse order before RET.

## Stack frames and locals

The stack grows downward. M4 defines explicit frame operations:

- `ENTER n`: SP = SP - n.
- `LEAVE n`: SP = SP + n.
- `LOADS rd,[off8]`: rd = MEM[SP + signed off8].
- `STORES [off8],rs`: MEM[SP + signed off8] = rs.

The signed offset range is -128..+127. A normal frame uses non-negative offsets starting at zero after ENTER. This makes local-variable storage visible without introducing an implicit frame pointer.

A function must restore SP to its entry value before RET, apart from the return address consumed by RET itself.

## Return values

- byte / bool / char: R0.
- 16-bit teaching value: R0 low byte, R1 high byte.
- void: R0/R1 unspecified.

## Preservation summary

| State | Rule |
|---|---|
| R0-R3 | caller-saved / argument registers |
| R4-R6 | callee-saved |
| R7 | caller-saved scratch |
| FLAGS | caller-saved |
| SP | balanced by callee |

## Recursion

Recursion is supported. Each invocation can reserve independent locals with ENTER and address them relative to its current SP. `examples/recursive_sum.eduasm` demonstrates recursive calls with a one-byte local and complete SP restoration.

## Freeze rationale

The v0 contract now supports the needs required before EduC code generation: register arguments, return values, calls, saved registers, addressable local bytes, recursion, and deterministic stack restoration.

General stack-passed arguments, larger aggregate values, alignment rules, interrupts and re-entrant system conventions are deliberately outside ABI v0 rather than being underspecified.

## Educational goal

Students can inspect every part of a call: arguments in registers, return PC on the stack, local allocation through ENTER, local reads/writes through SP-relative addressing, recursive frames, LEAVE, and the final return value in R0.
