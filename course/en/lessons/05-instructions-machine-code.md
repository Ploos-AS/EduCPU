# 05 — Instructions and machine code

## Learning objectives

After this lesson, you should be able to:

- distinguish an assembly instruction from its machine-code bytes;
- identify opcodes and operands in simple EduCPU instructions;
- explain why EduCPU instructions have different lengths;
- decode simple instruction bytes using the ISA;
- explain how EduCPU stores a 16-bit address in little-endian order.

## What is it?

The CPU does not execute assembly text. It executes **machine code**: bytes whose bit patterns have meanings defined by the instruction set architecture, or ISA.

Assembly gives humans readable names for those instructions.

For example:

```asm
MOVI R0, 42
```

is encoded by EduASM as:

```text
11 00 2A
```

The first byte is the **opcode**. It selects the operation. The following bytes are **operands** encoded in the format required by that opcode.

## Why do we need it?

A CPU needs an unambiguous representation that can be stored in memory and fetched as bytes.

Humans prefer:

```asm
ADD R0, R1
```

EduCPU executes:

```text
20 00 01
```

The assembler is the bridge between those two representations.

Understanding that bridge removes an important layer of apparent magic: an assembly program is not directly understood by the CPU.

## How does EduCPU do it?

EduCPU ISA v0 uses a one-byte opcode followed by zero or more operand bytes.

Examples:

| Assembly | Bytes | Length |
| --- | --- | ---: |
| `NOP` | `00` | 1 |
| `HALT` | `01` | 1 |
| `MOVI R0,42` | `11 00 2A` | 3 |
| `ADD R0,R1` | `20 00 01` | 3 |
| `NOT R3` | `2B 03` | 2 |
| `JMP 0x1234` | `30 34 12` | 3 |

Register operands use a full byte. R0 through R7 are encoded as `00` through `07`.

### 16-bit addresses and little endian

EduCPU addresses are 16 bits. Address operands are stored **low byte first, then high byte**.

For address:

```text
0x1234
```

the two address bytes are:

```text
34 12
```

Therefore:

```asm
JMP 0x1234
```

becomes:

```text
30 34 12
```

This byte order is called **little endian**.

> **How does EduCPU know?**
>
> It does not guess where an instruction ends. The opcode determines the instruction format. Once the decoder sees `0x11`, the ISA says that a register byte and an 8-bit immediate byte follow. Once it sees `0x01`, it knows HALT has no operands.

## Worked example

Consider:

```asm
MOVI R0, 42
MOVI R1, 1
ADD R0, R1
HALT
```

The bytes are:

```text
Address   Bytes       Meaning
0000      11 00 2A    MOVI R0,42
0003      11 01 01    MOVI R1,1
0006      20 00 01    ADD R0,R1
0009      01          HALT
```

Notice how instruction addresses follow from instruction lengths.

After fetching all three bytes of the first instruction, PC has advanced from `0x0000` to `0x0003`.

Machine code is therefore both **data stored in memory** and **a sequence interpreted according to the ISA**.

## Run and observe

The CI-tested fixture is:

`course/examples/lesson05-machine-code.eduasm`

Its test checks the exact assembled byte sequence, not merely the final CPU result.

Before assembling it, write down the bytes you expect. Then compare your prediction with the EduASM output.

## Explain the result

Names such as `MOVI`, `R0` and `JMP` exist for programmers. At runtime, the CPU sees encoded fields.

For a valid program, both sides agree because the assembler and CPU implement the same ISA specification.

This is why the ISA is a contract: it defines what each encoded pattern means.

## Exercises

### Understanding

1. What is an opcode?
2. Does EduCPU execute the text `ADD`?
3. How is R5 encoded as a register operand?
4. Why can two instructions have different lengths?
5. What does little endian mean for a 16-bit EduCPU address?

### Practice

Encode these by hand using the ISA documentation:

```asm
HALT
MOVI R3, 0x7F
NOT R3
ADD R2, R5
JMP 0x1234
```

Then assemble them and compare the bytes.

### Explore

Take a valid assembled program and identify the instruction boundaries using only the machine bytes and ISA table.

Then change one opcode byte. Decode the new byte sequence before executing it.

Be careful: changing an opcode can also change how following bytes are interpreted.

## Check your understanding

1. What connects assembly syntax to machine-code bytes?
2. What byte encodes EduCPU `HALT`?
3. How many bytes does `MOVI R0,42` occupy?
4. How is address `0x1234` stored in an address operand?
5. How does the decoder know how many operand bytes to read?

Solutions are kept separately from the lesson.

## Tools

Use the real course fixture: `course/examples/lesson05-machine-code.eduasm`.

**EduVis:** use this tool during the observation step. **EduGuide:** use the guided PREDICT → OBSERVE → EXPLAIN workflow.

Predict important changes before running the fixture, then compare them with the observation.

## Next

Machine code is precise, but inconvenient for humans. Next we move back one layer and study **EduASM and what an assembler does**.
