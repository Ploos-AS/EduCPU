# 01 — Bits, bytes, binary and hexadecimal

## Learning objectives

After this lesson, you should be able to:

- explain what a bit and a byte are;
- read an 8-bit binary number;
- convert small values between binary, decimal and hexadecimal;
- explain why hexadecimal is useful when working with computers;
- relate an 8-bit value to EduCPU registers and memory.

## What is it?

A computer stores information using **bits**. A bit has only two possible values: `0` or `1`.

Eight bits form a **byte**. EduCPU has an 8-bit datapath and its general-purpose registers R0–R7 each hold one byte. An 8-bit byte can represent 256 different bit patterns, from `00000000` through `11111111`.

The same bit pattern can be written in different number systems. For example:

| Binary | Decimal | Hexadecimal |
| --- | ---: | ---: |
| `00000000` | 0 | `0x00` |
| `00000001` | 1 | `0x01` |
| `00001010` | 10 | `0x0A` |
| `00101010` | 42 | `0x2A` |
| `11111111` | 255 | `0xFF` |

These are not different values. They are different ways to write the same value.

## Why do we need it?

Binary shows the individual bits clearly, but long binary numbers are difficult for humans to read. Decimal is familiar, but it does not line up neatly with groups of bits.

Hexadecimal uses sixteen digits: `0`–`9` and `A`–`F`. One hexadecimal digit represents exactly four bits, so one byte is exactly two hexadecimal digits.

For example:

```text
0010 1010
  2    A
   0x2A
```

That makes hexadecimal especially convenient for machine code, memory addresses and register values.

## How does EduCPU do it?

EduCPU does not know whether you intended a value to be binary, decimal or hexadecimal. Inside the machine it is simply a pattern of bits.

When R0 contains `00101010`, a debugger may display that pattern as decimal `42` or hexadecimal `0x2A`. The bits stored in R0 have not changed.

> **How does EduCPU know?**
>
> It does not know that `42`, `0x2A` and `00101010` are three human representations of the same number. EduCPU only has the eight stored bits. The assembler, simulator and visualizer choose useful representations for us.

## Worked example

Consider the binary byte:

```text
00101010
```

The positions in an 8-bit value represent powers of two:

```text
128 64 32 16  8  4  2  1
 0   0  1  0  1  0  1  0
```

The set bits are therefore:

```text
32 + 8 + 2 = 42
```

Split the same byte into groups of four:

```text
0010 1010
```

`0010` is hexadecimal `2`, and `1010` is hexadecimal `A`. Therefore:

```text
00101010 = 42 = 0x2A
```

## Run and observe

EduASM accepts several number formats. These instructions all load the same value into R0:

```asm
MOVI R0, 42
MOVI R0, 0x2A
MOVI R0, 0b00101010
```

Try each form separately in a tiny program ending with `HALT`. The repository also contains the CI-tested fixture `course/examples/lesson01-number-formats.eduasm`, which loads all three spellings into R0, R1 and R2. Before assembling it, predict what byte value R0 will contain.

Then inspect the assembled bytes and CPU state with the EduCPU tools. The notation in the source changes, but the value loaded into R0 is identical.

## Explain the result

The assembler translates the human-readable literal into an 8-bit value. By the time the CPU executes `MOVI`, the original spelling of the number is gone.

This is our first example of an important course theme: **human-friendly notation is translated into simpler machine information**.

## Exercises

### Understanding

1. How many different values can eight bits represent?
2. Convert `00001111` to decimal and hexadecimal.
3. Convert decimal `42` to binary and hexadecimal.
4. Convert `0xFF` to decimal and binary.
5. Why is hexadecimal convenient when inspecting bytes?

### Practice

Write the following values in binary, decimal and hexadecimal:

- 0
- 1
- 16
- 42
- 127
- 128
- 255

Then write three EduASM `MOVI` instructions that all load decimal 42 into R3, using decimal, hexadecimal and binary notation.

### Explore

Create three minimal EduASM programs that differ only in how the value 42 is written.

Before assembling them, predict:

1. whether R0 will differ after execution;
2. whether the immediate value in the generated machine code will differ.

Assemble and run them. Compare the result with your prediction.

## Check your understanding

1. What is the smallest unit of information introduced in this lesson?
2. How many bits are in an EduCPU general-purpose register?
3. What hexadecimal value represents binary `11110000`?
4. Does the CPU remember whether a value was written as decimal or hexadecimal in the source program?

Solutions are kept separately from the lesson.

## Next

Bits become much more interesting when hardware can **store, combine and transform** them. Next we introduce logic and storage, preparing the pieces we need to understand what a CPU actually is.
