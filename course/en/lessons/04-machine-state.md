# 04 — Machine state

## Learning objectives

After this lesson, you should be able to:

- explain what **machine state** means;
- identify the roles of R0–R7, PC, SP, FLAGS and memory;
- describe how one instruction changes state into a new state;
- distinguish CPU registers from memory;
- inspect an EduCPU program at an exact point in its execution.

## What is it?

At any instant, a CPU has information that describes where it is and what it currently contains. We call this its **state**.

For EduCPU, the important architectural state includes:

- **R0–R7** — eight general-purpose 8-bit registers;
- **PC** — the 16-bit program counter;
- **SP** — the 16-bit stack pointer;
- **FLAGS** — an 8-bit status register;
- **memory** — 65,536 byte locations;
- whether the CPU is **halted** or has entered a **trap**.

If we know the complete state and the machine's rules, we can reason about what the next instruction will do.

## Why do we need it?

Programs work by changing state.

Consider:

```asm
MOVI R0, 10
ADDI R0, 5
HALT
```

The source describes operations, but execution is a sequence of state changes:

```text
R0 = 0
   ↓ MOVI R0,10
R0 = 10
   ↓ ADDI R0,5
R0 = 15
   ↓ HALT
halted = true
```

Debugging becomes much easier when we stop thinking only in source lines and ask:

**What was the machine state before this instruction, and what changed afterward?**

## How does EduCPU do it?

### R0–R7

These are general-purpose 8-bit registers. Each stores one byte.

They can hold numbers, temporary results, addresses used by some instructions, function arguments or any other 8-bit pattern required by the program.

### PC — program counter

PC is 16 bits wide and identifies where instruction fetching continues.

Normal instruction fetching advances PC as instruction and operand bytes are read. Branches, jumps, calls and returns can deliberately change it.

### SP — stack pointer

SP is 16 bits wide. After reset:

```text
SP = 0xFF00
```

The stack grows downward toward lower addresses. We will study the stack in detail later.

### FLAGS

The low four EduCPU flag bits are:

| Bit | Name | Meaning |
| ---: | --- | --- |
| 0 | Z | zero |
| 1 | N | negative/high bit set |
| 2 | C | carry / no-borrow for subtraction |
| 3 | V | signed overflow |

Bits 4–7 are reserved and read as zero in ISA v0.

Not every instruction changes FLAGS. For example, `MOVI` leaves them unchanged, while arithmetic instructions update them.

### Memory

EduCPU has a flat 16-bit address space:

```text
0x0000 ... 0xFFFF
```

That is 65,536 byte-addressable locations.

Program bytes and data can both exist in this address space. The range `0xFF00–0xFFFF` is reserved for future I/O/system use, and reset initializes SP to `0xFF00`.

> **How does EduCPU know?**
>
> It does not maintain a human description such as “R0 is the answer”. It has architectural storage locations containing bit patterns. Instructions define which locations are read, which are written and how PC and FLAGS change.

## Worked example

Take:

```asm
MOVI R0, 10
MOVI R1, 20
ADD R0, R1
HALT
```

Immediately after reset, before execution:

```text
R0 = 0
R1 = 0
PC = 0x0000
SP = 0xFF00
FLAGS = 0
halted = false
```

After `MOVI R0,10`:

```text
R0 = 10
PC = 0x0003
```

After `MOVI R1,20`:

```text
R1 = 20
PC = 0x0006
```

After `ADD R0,R1`:

```text
R0 = 30
R1 = 20
PC = 0x0009
FLAGS = 0
```

After `HALT`:

```text
PC = 0x000A
halted = true
```

The program can therefore be understood as a sequence of precisely defined state transitions.

## Run and observe

The CI-tested fixture is:

`course/examples/lesson04-machine-state.eduasm`

It deliberately produces several visible state changes, including a zero result so that the Z flag becomes set.

Before running it, make a table with one row per instruction and columns for R0, R1, PC, SP and FLAGS.

Fill in your prediction first. Then single-step the program in the EduCPU simulator and compare each state.

## Explain the result

The CPU does not execute a whole program in one conceptual action. Each instruction transforms the current architectural state into the next architectural state.

This gives us a powerful way to understand computers:

```text
current state + instruction → next state
```

Later, when we study branches, stacks, functions and compilers, the machine becomes more complex — but this principle remains the same.

## Exercises

### Understanding

1. How many general-purpose registers does EduCPU have?
2. How many bits wide is PC?
3. What is SP after reset?
4. Which flag indicates a zero result?
5. Does `MOVI` change FLAGS?

### Practice

For:

```asm
MOVI R0, 5
MOVI R1, 5
SUB R0, R1
HALT
```

predict R0, R1, PC, SP and FLAGS after every instruction.

Then run it one instruction at a time.

### Explore

Run a small program and stop after each instruction.

Record only the pieces of state that changed. Then repeat the exercise while recording the complete architectural state.

Which representation is easier for spotting changes? Which is better for reconstructing an exact point in execution?

## Check your understanding

1. What do we mean by machine state?
2. Why is PC part of the state?
3. Are registers and memory the same thing?
4. What state change does `HALT` cause?
5. Complete the idea: current state + instruction → ______.

Solutions are kept separately from the lesson.

## Next

Now that we can describe the machine at an exact instant, we can look at what the CPU actually reads from memory. Next: **instructions and machine code**.
