# 06 — EduASM and what an assembler does

## Learning objectives

After this lesson, you should be able to:

- explain why assembly language exists;
- write simple EduASM instructions;
- use registers, literals, comments and labels;
- explain why labels require the assembler to calculate addresses;
- describe the basic idea of a two-pass assembler.

## What is assembly?

Machine code is ideal for the CPU but awkward for humans. Assembly language gives readable names to the operations and operands encoded in those bytes.

Instead of:

```text
11 00 2A
```

we can write:

```asm
MOVI R0, 42
```

EduASM is the assembly language and assembler used by EduCPU.

## Why do we need an assembler?

The CPU still needs machine bytes. An **assembler** translates assembly source into those bytes.

It also solves problems that would otherwise be tedious and error-prone. The most important example is a **label**.

Instead of calculating the address of a loop manually:

```asm
JNZ 0x0006
```

we can give that location a name:

```asm
loop:
    SUBI R0, 1
    JNZ loop
```

The assembler calculates the address for us.

## EduASM basics

### Instructions and registers

```asm
MOVI R0, 42
MOV R1, R0
ADD R0, R1
HALT
```

EduCPU has R0–R7.

### Number formats

EduASM accepts several ways of writing the same value:

```asm
MOVI R0, 42
MOVI R1, 0x2A
MOVI R2, $2A
MOVI R3, 0b00101010
```

All four immediates represent the same byte.

### Comments

Comments can begin with `;` or `#`:

```asm
MOVI R0, 3      ; loop counter
# This is also a comment
```

Comments are for humans. They produce no machine-code bytes.

### Labels

A label names an address:

```asm
again:
    SUBI R0, 1
    JNZ again
```

The name `again` does not exist in the CPU. EduASM replaces it with the correct address when assembling the program.

> **How does EduCPU know?**
>
> It does not know labels, comments or the spelling `R0`. Those are assembly-language conveniences. By the time the CPU receives the program, EduASM has converted them into instruction bytes, register numbers and addresses.

## Why two passes?

Consider:

```asm
JMP later
MOVI R0, 99
later:
HALT
```

When the assembler reads `JMP later`, it has not yet encountered `later:`.

This is called a **forward reference**.

EduASM solves this with two conceptual passes:

1. **Pass 1:** determine instruction sizes and collect label addresses.
2. **Pass 2:** encode instructions now that label addresses are known.

For the example above:

```text
0x0000  JMP later       3 bytes
0x0003  MOVI R0,99      3 bytes
0x0006  later: HALT     1 byte
```

So `later` means address `0x0006`, and the jump can be encoded accordingly.

## Worked example

The lesson fixture contains:

```asm
MOVI R0, 3
loop:
    SUBI R0, 1
    JNZ loop
HALT
```

Before assembling it, calculate:

1. the address of `loop`;
2. the bytes for `MOVI R0,3`;
3. the address encoded by `JNZ loop`;
4. the final value of R0.

Then compare your prediction with EduASM and the reference CPU.

## Run and observe

The CI-tested fixture is:

`course/examples/lesson06-eduasm.eduasm`

The tests verify both the assembled bytes and execution result. This means the lesson's explanation of labels is checked against the real assembler.

EduASM can also produce a listing, which is useful because it shows source instructions together with their addresses and encoded bytes.

## Explain the result

Assembly is a representation for humans that stays close to the machine.

A label is especially revealing:

```text
human idea:     loop
assembler:      calculate address
machine code:   encoded 16-bit address
CPU:            load that address into PC when branch is taken
```

Each layer removes a little convenience until only architectural state and bytes remain.

## Exercises

### Understanding

1. Why is assembly easier for humans than raw machine code?
2. Does a comment create any machine bytes?
3. Does the CPU know the name of a label?
4. What is a forward reference?
5. Why does EduASM use two passes?

### Practice

Write an EduASM program that:

1. puts 5 in R0;
2. subtracts 1 repeatedly;
3. stops when R0 becomes zero;
4. halts.

Predict the label address and assembled branch bytes before running the assembler.

### Explore

Change the number of instructions before a label.

Predict how its address changes, then assemble again and inspect the listing.

Notice that the source-level name stays the same even though its machine address changes.

## Check your understanding

1. What does an assembler produce?
2. Which register names are valid in EduASM?
3. Give three ways to write decimal 42 as a literal.
4. What happens to labels during assembly?
5. Which pass can first know the address of a forward label?

Solutions are kept separately from the lesson.

## Tools

Use the real course fixture: `course/examples/lesson06-eduasm.eduasm`.

**EduVis:** use this tool during the observation step. **EduGuide:** use the guided PREDICT → OBSERVE → EXPLAIN workflow.

Predict important changes before running the fixture, then compare them with the observation.

## Next

Now we can write readable machine-level programs. Next we study **arithmetic, FLAGS and branches**, where the CPU begins making decisions based on previous results.
