# 02 — Logic and storing information

## Learning objectives

After this lesson, you should be able to:

- explain the basic ideas behind NOT, AND, OR and XOR;
- distinguish combinational logic from stored state;
- explain why a CPU needs registers and memory;
- use EduCPU logical instructions and observe their results;
- describe why a bit pattern only gains meaning through how it is used.

## What is it?

Bits become useful when a machine can **transform** and **remember** them.

Logic operations transform bit patterns. Four important operations are:

| A | B | A AND B | A OR B | A XOR B |
| - | - | ------- | ------ | ------- |
| 0 | 0 | 0 | 0 | 0 |
| 0 | 1 | 0 | 1 | 1 |
| 1 | 0 | 0 | 1 | 1 |
| 1 | 1 | 1 | 1 | 0 |

**NOT** uses one input and flips it: 0 becomes 1 and 1 becomes 0.

These rules operate independently on every bit of a byte.

A machine also needs **state**: information that remains available after the current operation. Registers and memory provide state.

## Why do we need it?

A circuit that only computes a result from its current inputs cannot remember what happened before. A useful computer must keep instructions, data and intermediate results.

This gives us two important ideas:

- **logic** changes information;
- **storage** keeps information.

A CPU combines both.

## How does EduCPU do it?

EduCPU has eight general-purpose 8-bit registers, R0–R7, and 64 KiB of byte-addressable memory.

Its ISA includes `AND`, `OR`, `XOR` and `NOT`. For the two-register operations, the result replaces the first register.

For example:

```asm
MOVI R0, 0b11001100
MOVI R1, 0b10101010
AND R0, R1
HALT
```

After `AND`, R0 contains `10001000`.

> **How does EduCPU know?**
>
> It does not know that the bits represent a number, a mask, characters or anything else. The instruction decoder tells the CPU which operation to perform. The ALU applies that operation to the bit patterns, and a register stores the result.

## Worked example

Take:

```text
R0 = 11001100
R1 = 10101010
```

For AND, a result bit is 1 only where both input bits are 1:

```text
  11001100
& 10101010
----------
  10001000
```

The same inputs produce different results with different operations:

```text
AND = 10001000 = 0x88
 OR = 11101110 = 0xEE
XOR = 01100110 = 0x66
```

And:

```text
NOT 11001100 = 00110011 = 0x33
```

## Run and observe

The repository contains the CI-tested fixture:

`course/examples/lesson02-logic.eduasm`

It calculates AND, OR, XOR and NOT using real EduCPU instructions. Before running it, calculate the expected register values yourself.

Then assemble and execute it with the EduCPU tools and compare the machine state with your prediction.

## Explain the result

The values placed in the registers remain there until another instruction changes them. That persistence is **state**.

The logical instruction itself does not permanently remember its inputs. It computes a new bit pattern. A destination register stores that result.

This distinction between **doing** and **remembering** is one of the foundations we need before constructing a mental model of a CPU.

## Exercises

### Understanding

1. What is `1 AND 0`?
2. What is `1 OR 0`?
3. What is `1 XOR 1`?
4. What does NOT do to a bit?
5. Why is storage necessary for a computer?

### Practice

Calculate these without running the simulator:

1. `10101010 AND 11110000`
2. `10101010 OR 00001111`
3. `10101010 XOR 11111111`
4. `NOT 00001111`

Then write EduASM that performs each operation.

### Explore

Choose two byte values and place them in R0 and R1.

Predict the results of AND, OR and XOR. Run each operation and compare your prediction with the observed state.

Then ask a different question: can you tell from the final bits alone whether they were intended as a number or as a bit mask?

## Check your understanding

1. What is the difference between logic and state?
2. Where can EduCPU keep an 8-bit intermediate value?
3. Which operation produces 1 when its two input bits are different?
4. Does an ALU need to understand the human meaning of the bits it processes?

Solutions are kept separately from the lesson.

## Next

We now have bits, operations on bits and places that can remember bits. Next we combine these ideas and answer a central question: **What is a CPU?**
