# 09 — Functions, CALL/RET and the ABI

## Learning objectives

After this lesson, you should be able to explain how CALL and RET use the stack, identify a return address, pass simple arguments according to the EduCPU ABI, identify caller- and callee-saved registers, and explain why a calling convention is necessary.

## Why functions need rules

A function call creates several questions:

- Where does execution continue afterwards?
- Where are arguments placed?
- Where is the return value placed?
- Which registers may the function change?
- Who restores temporary stack space?

An **ABI** (Application Binary Interface) answers these questions precisely.

EduCPU ABI v0 is deliberately small so we can follow every byte.

## CALL saves where to return

Consider:

```asm
CALL add_one
HALT

add_one:
    ADDI R0, 1
    RET
```

When CALL executes, PC already identifies the instruction after CALL. That address is the **return address**.

EduCPU pushes the 16-bit return address onto the stack and then loads the function address into PC.

For CALL, the return address is pushed **high byte first, then low byte**. Because the stack grows downward, the low byte ends up at `MEM[SP]`.

RET reverses the process: it pops the low byte, then the high byte, reconstructs the 16-bit address and loads it into PC.

> **How does EduCPU know where to return?**
>
> It does not understand functions. CALL stores a number — the return PC — using a precisely defined stack layout. RET reads those bytes back and puts the reconstructed number into PC.

## Arguments and return values

EduCPU ABI v0 passes up to four byte-sized arguments in registers:

| Purpose | Register |
| --- | --- |
| argument 1 | R0 |
| argument 2 | R1 |
| argument 3 | R2 |
| argument 4 | R3 |
| primary 8-bit return value | R0 |
| high byte of a 16-bit return value | R1 |

Example:

```asm
MOVI R0, 20
MOVI R1, 22
CALL add
HALT

add:
    ADD R0, R1
    RET
```

The caller places 20 and 22 in R0 and R1. The function returns 42 in R0.

No special hardware says “R0 is argument 1”. That meaning comes from the ABI contract shared by caller, callee and compiler.

## Caller-saved and callee-saved registers

ABI v0 defines:

- R0–R3: argument/return registers and caller-saved;
- R4–R6: callee-saved;
- R7: caller-saved scratch;
- FLAGS: caller-saved.

**Caller-saved** means the caller must preserve a value if it needs that value after the call.

**Callee-saved** means a function that changes the register must restore its original value before returning.

These rules let separately written functions cooperate.

## Stack balance

A function must return with SP balanced relative to its entry state, apart from CALL/RET's own return-address mechanism.

EduCPU also provides `ENTER n` and `LEAVE n` for local stack space:

```asm
worker:
    ENTER 2
    ; two bytes of local frame space
    LEAVE 2
    RET
```

`ENTER 2` moves SP down by two bytes. `LEAVE 2` restores it.

The compiler can access stack-frame bytes with `LOADS` and `STORES`. We will see why that matters when we follow EduC through code generation.

## Worked example

The lesson fixture calls a function with two arguments:

```asm
MOVI R0, 20
MOVI R1, 22
CALL add
HALT

add:
    ADD R0, R1
    RET
```

Before execution, predict:

1. the address immediately after CALL;
2. SP immediately before CALL;
3. the two memory bytes written by CALL;
4. SP on entry to `add`;
5. R0 after ADD;
6. PC and SP immediately after RET.

Then single-step and compare.

## ABI versus ISA

This distinction is important.

The **ISA** defines what CALL, RET, PUSH, registers and memory operations do.

The **ABI** defines conventions for using those mechanisms together: argument registers, return registers, saved registers and stack discipline.

The CPU enforces the ISA. Programs and tools agree to follow the ABI.

## Exercises

### Understanding

1. What exactly is a return address?
2. Which byte of an EduCPU return address is at `MEM[SP]`?
3. Where is the first byte argument passed?
4. Which registers are callee-saved?
5. Why can two functions disagree even when both use valid ISA instructions?

### Practice

Write a function `double` that accepts one byte in R0 and returns twice that value in R0.

Then write a function that temporarily changes R4. Preserve R4 according to the ABI.

### Explore

Single-step a CALL and RET while watching PC, SP and memory around the stack.

Then add another function call inside the first function. Draw both return addresses on the stack before running the program.

## Check your understanding

Follow the chain:

```text
caller → argument registers → CALL → return address on stack
       → callee → return value → RET → caller
```

Which parts are hardware/ISA behaviour, and which parts exist only because software agrees on the ABI?

## Next

We now know enough low-level machinery to ask a much bigger question: how can a programmer write something more expressive and have tools produce all of this automatically? Next: **what is a compiler?**
