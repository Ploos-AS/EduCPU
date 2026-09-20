# 03 — What is a CPU?

## Learning objectives

After this lesson, you should be able to:

- explain the basic job of a CPU;
- identify registers, ALU, program counter, memory interface and control logic;
- describe the fetch–decode–execute cycle;
- explain how the program counter selects the next instruction;
- follow one simple EduCPU instruction through the machine.

## What is it?

A **CPU** — central processing unit — is the part of a computer that repeatedly reads instructions and carries out the operations they describe.

A useful first model of a CPU contains a few cooperating parts:

- **registers** hold small values close to the processing logic;
- the **ALU** performs arithmetic and logical operations;
- the **program counter (PC)** identifies the next instruction;
- **FLAGS** remember selected properties of results;
- the **memory interface** moves instruction and data bytes between CPU and memory;
- **control logic** interprets an instruction and coordinates what the other parts do.

The CPU is not one magical component that “understands programs”. It is a system of simpler mechanisms working together.

## Why do we need it?

In the previous lessons we learned that bits can be stored and transformed. A programmable computer needs something that can choose **which transformation happens next** according to instructions stored in memory.

That is the CPU's central job.

Instead of wiring one circuit to perform one permanent sequence of operations, we store a sequence of instruction bytes in memory. The CPU repeatedly fetches and executes them.

## How does EduCPU do it?

EduCPU has:

- eight 8-bit general-purpose registers: R0–R7;
- a 16-bit PC;
- a 16-bit SP;
- an 8-bit FLAGS register;
- a 64 KiB byte-addressable memory space;
- instructions such as `MOVI`, `ADD`, `AND`, `JMP` and `HALT`.

A simplified view is:

```text
                    +------------------+
                    |   Control logic  |
                    +---------+--------+
                              |
                              v
+---------+     +----------+  |  +---------+
| Memory  |<--->| PC /     |--+->| Decode  |
|         |     | fetch     |     +----+----+
+---------+     +----------+          |
                                      v
                               +------+------+
                               | Registers   |
                               | R0 ... R7   |
                               +------+------+
                                      |
                                      v
                               +------+------+
                               |    ALU      |
                               +------+------+
                                      |
                                +-----+-----+
                                |   FLAGS   |
                                +-----------+
```

This is a teaching model of information flow, not a claim about FPGA clock-cycle timing.

## Fetch, decode, execute

A CPU repeatedly performs a cycle that we can describe conceptually as:

1. **Fetch** — use PC to read the next instruction byte from memory.
2. **Decode** — determine which instruction that byte represents and which operands it needs.
3. **Execute** — perform the required operation.
4. **Continue** — PC identifies the next instruction, unless an instruction deliberately changes control flow.

Real implementations may divide or overlap these actions differently. For EduCPU teaching, this sequence gives us a clear mental model.

> **How does EduCPU know?**
>
> The CPU does not read the word `MOVI`. The assembler has already converted it into an opcode byte. The instruction decoder recognizes that bit pattern and the control logic causes the required operand bytes to be fetched and the destination register to be written.

## Worked example

Consider:

```asm
MOVI R0, 42
HALT
```

EduASM encodes the first instruction as three bytes:

```text
11 00 2A
```

They mean:

```text
11  -> MOVI opcode
00  -> R0
2A  -> immediate value 42
```

At reset, PC is `0x0000`.

Conceptually, EduCPU:

1. fetches `0x11` from address `0x0000`;
2. decodes it as `MOVI`;
3. fetches `0x00` and identifies R0;
4. fetches `0x2A`;
5. writes `0x2A` into R0;
6. now has PC = `0x0003`;
7. fetches `0x01`, the `HALT` opcode;
8. enters the halted state.

Nothing in this sequence requires the CPU to understand the source text.

## Run and observe

The repository contains:

`course/examples/lesson03-cpu-cycle.eduasm`

Before running it, predict:

- the final values of R0 and R1;
- the value of PC after `HALT`;
- whether FLAGS changes.

Then assemble and execute the program using the EduCPU tools.

The automated course test runs the same fixture against the executable reference CPU.

## Explain the result

The important idea is not merely that an instruction produced a value. The CPU was able to **select an instruction from memory, identify its operation, obtain its operands, change machine state and move on to the next instruction**.

A program is therefore not something separate from the machine. At execution time it is bytes in memory whose patterns cause specific state transitions.

## Exercises

### Understanding

1. What is the purpose of the PC?
2. What does the ALU do?
3. Why does a CPU need control logic?
4. Where are instructions stored before the CPU executes them?
5. What is the difference between an assembly mnemonic and an opcode?

### Practice

For this program:

```asm
MOVI R0, 10
MOVI R1, 20
ADD R0, R1
HALT
```

predict the final values of R0, R1 and PC.

Then run it and compare your prediction.

### Explore

Change one byte of an assembled program rather than changing its assembly source.

Before running the modified binary, use the ISA documentation to predict what the changed byte will do.

This is an important transition: you are beginning to look at the program from the CPU's point of view.

## Check your understanding

1. What three words summarize the basic instruction cycle used in this lesson?
2. Does EduCPU fetch assembly text from memory?
3. Which register identifies the next instruction?
4. Which part performs arithmetic and logical transformations?
5. Why is the CPU better understood as cooperating mechanisms than as a component that “knows” the program?

Solutions are kept separately from the lesson.

## Next

We now have a complete first mental model of a CPU. Next we look more closely at **machine state**: PC, SP, FLAGS, R0–R7 and memory, and learn how to describe an exact instant in an EduCPU program.
