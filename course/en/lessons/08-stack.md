# 08 — The stack

## Learning objectives

After this lesson, you should be able to explain what a stack is, describe LIFO ordering, follow SP as PUSH and POP execute, identify the exact memory addresses used, and explain why balanced stack use matters.

## What is a stack?

A stack is a disciplined way to use memory for temporary storage.

Its rule is **last in, first out (LIFO)**. If you push A and then B, you pop B before A.

EduCPU uses the 16-bit **SP** register to identify the current top of the stack.

After reset:

```text
SP = 0xFF00
```

The stack grows toward lower addresses.

## PUSH

For EduCPU:

```asm
PUSH R0
```

conceptually performs:

```text
SP = SP - 1
MEM[SP] = R0
```

So if SP starts at `0xFF00` and R0 contains `0x2A`:

```text
before: SP = FF00
after:  SP = FEFF
        MEM[FEFF] = 2A
```

The decrement happens before the write.

## POP

```asm
POP R1
```

conceptually performs:

```text
R1 = MEM[SP]
SP = SP + 1
```

If SP is `0xFEFF` and that byte contains `0x2A`, R1 becomes `0x2A` and SP returns to `0xFF00`.

> **How does EduCPU know?**
>
> It does not know that a byte is “temporary data”. PUSH and POP have precise architectural rules involving SP and memory. LIFO behaviour emerges because PUSH decrements SP before writing and POP reads before incrementing it.

## Worked example

```asm
MOVI R0, 0x11
MOVI R1, 0x22
PUSH R0
PUSH R1
POP R2
POP R3
HALT
```

Track the stack:

```text
reset          SP=FF00
PUSH R0        SP=FEFF  MEM[FEFF]=11
PUSH R1        SP=FEFE  MEM[FEFE]=22
POP R2         R2=22    SP=FEFF
POP R3         R3=11    SP=FF00
```

R2 receives the value pushed last. That is LIFO.

Notice that popping a value does not erase the old memory byte. It changes SP so that byte is no longer part of the active stack.

## Stack balance

A useful invariant is:

```text
temporary pushes = matching pops
```

If a piece of code begins with SP=`0xFF00` and uses the stack only for temporary storage, it should normally restore SP to `0xFF00` before finishing.

Unbalanced stack operations can cause later code to read the wrong bytes or overwrite data unexpectedly.

This becomes especially important when functions start using the stack.

## Memory, not magic

The stack is not a separate physical storage system in the EduCPU architecture. It is ordinary memory used according to rules involving SP.

This means we can inspect both:

- SP, which tells us where the active stack begins;
- memory around SP, which shows the stored bytes.

That visibility is valuable when debugging.

## Run and observe

The CI-tested fixture is `course/examples/lesson08-stack.eduasm`.

Before running it, draw addresses `0xFEFE`, `0xFEFF` and `0xFF00`. Predict SP and the memory bytes after every PUSH and POP.

The test checks the exact intermediate stack states, not only the final register values.

## Exercises

### Understanding

1. What does LIFO mean?
2. Which direction does the EduCPU stack grow?
3. Does PUSH write before or after decrementing SP?
4. Does POP increment SP before or after reading memory?
5. Does POP erase the memory byte it reads?

### Practice

Start with R0=`0xAA`, R1=`0xBB` and SP=`0xFF00`.

Predict SP and memory after:

```asm
PUSH R0
PUSH R1
POP R4
```

What remains on the active stack?

### Explore

Push three distinct values. Pop only two and halt.

Compare the final SP with the reset SP. Then add the missing POP and observe how stack balance is restored.

## Check your understanding

Complete the transformations:

```text
PUSH Rx: SP → ______ ; MEM[SP] → ______
POP  Rx: Rx → ______ ; SP → ______
```

Why does this pair naturally produce LIFO ordering?

## Next

A stack becomes much more powerful when the CPU can save where a program should return. Next: **functions, CALL/RET and the EduCPU ABI**.
