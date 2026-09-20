# 07 — Arithmetic, FLAGS and branches

## Learning objectives

After this lesson, you should be able to explain how arithmetic updates FLAGS, use Z/N/C/V to describe results, distinguish ADD/SUB from CMP, and follow conditional branches through a program.

## Arithmetic changes more than a register

For EduCPU, arithmetic instructions produce an 8-bit result and update four status flags:

| Flag | Meaning |
| --- | --- |
| Z | result is zero |
| N | bit 7 of the result is set |
| C | carry from addition, or no borrow for subtraction |
| V | signed overflow |

Values are always stored as eight bits, so arithmetic wraps modulo 256.

For example, `255 + 1` produces `0`. The result alone loses information about what happened; FLAGS preserve useful facts about the operation.

> **How does EduCPU know?**
>
> The ALU produces both the result bits and condition information. The instruction definition says which flag bits are updated. A later branch tests those stored bits; it does not understand concepts such as “equal” or “overflow”.

## ADD and subtraction

```asm
MOVI R0, 255
ADDI R0, 1
```

After the addition, R0 is `0`, Z is set, and C is set.

EduCPU subtraction uses C as **no borrow**. Therefore:

```asm
MOVI R0, 5
SUBI R0, 5
```

produces zero with both Z and C set.

This convention matters when reading subtraction and comparison results.

## CMP: subtract without keeping the result

`CMP` and `CMPI` update FLAGS as if a subtraction had happened, but do not store the subtraction result.

```asm
MOVI R0, 10
CMPI R0, 10
JZ equal
```

R0 remains 10. Z becomes set because the comparison result would have been zero.

This lets a program ask a question about two values without destroying either value.

## Conditional branches

EduCPU ISA v0 provides:

| Instruction | Branch condition |
| --- | --- |
| JZ | Z = 1 |
| JNZ | Z = 0 |
| JC | C = 1 |
| JNC | C = 0 |
| JN | N = 1 |
| JP | N = 0 |

`JMP` is unconditional.

A branch either replaces PC with its encoded target address or allows execution to continue at the next instruction.

## Worked example

```asm
MOVI R0, 3
loop:
    SUBI R0, 1
    JNZ loop
HALT
```

Each subtraction updates Z. While R0 is non-zero, `JNZ` loads the address of `loop` into PC. When R0 reaches zero, Z becomes 1 and the branch is not taken.

The same mechanism implements loops, decisions and eventually high-level `if` and `while`.

## Run and observe

The CI-tested fixture is `course/examples/lesson07-flags-branches.eduasm`.

Predict R0, R1 and FLAGS at each arithmetic or comparison instruction, and predict whether each branch is taken. Then single-step it.

## Unsigned and signed interpretations

The CPU stores only bit patterns. The same byte can be interpreted differently by a programmer.

`0xFF` can represent unsigned 255 or signed -1 in two's-complement interpretation. N simply records whether bit 7 is set. V records signed overflow for arithmetic.

The flags do not declare that a value “is signed” or “is unsigned”. The instruction sequence determines how the program interprets them.

## Exercises

### Understanding

1. What makes Z become 1?
2. What does C mean after EduCPU subtraction?
3. Does CMP modify its register operands?
4. What does JNZ test?
5. Why can `255 + 1` produce zero in an 8-bit register?

### Practice

Write a loop that counts R0 from 4 down to 0. Before running it, predict exactly how many times its conditional branch is taken.

Then write a comparison that chooses between two paths using `CMPI` and `JZ`.

### Explore

Try additions around `0x7F`, `0x80`, `0xFF` and `0x00`. Record Z, N, C and V.

Look for cases where C and V disagree. Explain why they describe different interpretations of the same eight result bits.

## Check your understanding

Complete this chain:

```text
arithmetic → FLAGS → conditional branch → PC → next instruction
```

Which part of that chain makes a high-level decision possible without the CPU understanding the meaning of the program?

## Next

Next we introduce the **stack**: a disciplined use of memory controlled by SP that lets programs temporarily save values and, later, support function calls.
