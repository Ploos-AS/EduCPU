# 15 — How a CPU is built

## Learning objectives

After this lesson, you should be able to explain the roles of registers, the ALU, datapath and control logic, describe how an instruction causes data to move through a CPU, distinguish architectural behaviour from one hardware implementation, and connect the EduCPU model to a future FPGA realization.

## Before reading further: predict the datapath

Consider:

```asm
MOVI R0, 20
MOVI R1, 22
ADD R0, R1
```

Before reading the hardware section, draw a minimal datapath on paper.

Mark:

- where the instruction is fetched;
- where the immediate value goes;
- where R0 and R1 are read;
- where the ALU result goes;
- how FLAGS receive information;
- how PC advances.

You do not need to draw every multiplexer. The goal is to form a first hypothesis about **which information must be able to move where**.

After the walkthrough, compare your drawing with the conceptual datapath below. Correct only what was actually wrong.

## We have reached the hardware boundary

So far we have treated EduCPU as an architecture:

- registers R0–R7;
- PC and SP;
- FLAGS;
- memory;
- instructions such as MOVI, ADD, LOAD, CALL and RET;
- precise rules for how every instruction changes machine state.

The reference CPU implements those rules in software.

But a CPU can also be built as digital hardware.

The important idea is:

> The ISA defines **what** the machine must do. The hardware design decides **how** signals, storage and logic make it happen.

## What is real and what is provisional?

This lesson describes the **architecture**, not a finished FPGA netlist or a claimed physical schematic.

What is already concrete and testable is:

- ISA v0 and its instruction encoding;
- the reference CPU;
- the independent emulator;
- differential/conformance tests;
- compiler and toolchain results.

The FPGA datapath is the next implementation layer. For that reason, this lesson deliberately uses a conceptual datapath rather than pretending it is the final circuit design.

When the HDL implementation exists, this lesson can be upgraded with an actual EduCPU block diagram and identify which parts are architectural requirements versus concrete FPGA design choices.

## Registers: small pieces of state

A register stores bits.

EduCPU has eight 8-bit general-purpose registers, plus architectural state such as PC, SP and FLAGS.

At the hardware level a register needs mechanisms to:

1. hold its current value;
2. present that value to other logic;
3. accept a new value when control logic tells it to load.

Without storage, a circuit can calculate a result but cannot remember machine state from one step to the next.

## The ALU: calculate

The **Arithmetic Logic Unit** performs operations such as:

```text
ADD
SUB
AND
OR
XOR
NOT
SHL
SHR
compare-related arithmetic
```

Conceptually it receives input values, receives a selected operation, and produces a result plus information used to update FLAGS.

For:

```asm
ADD R0, R1
```

a hardware implementation must somehow:

```text
read R0 ─┐
         ├→ ALU(add) → result → R0
read R1 ─┘              └────→ FLAGS
```

The ISA says what the final R0 and flags must be. It does not require one particular internal circuit arrangement.

## The datapath: where values can travel

Registers and an ALU are not enough. Values need routes between components.

The **datapath** is the collection of storage, buses, multiplexers and connections that let values move through the processor.

A conceptual EduCPU datapath might include routes among:

```text
             ┌──────────┐
Memory ─────►│ Decode / │
             │ Control  │
             └────┬─────┘
                  │
PC ───────────────┤
                  ▼
Registers ◄──────► ALU ─────► FLAGS
    ▲              │
    └──────────────┴────────► Memory
```

This is a teaching diagram, not yet the final FPGA schematic.

## Control: make the right thing happen

The datapath provides possibilities. **Control logic** selects which possibilities happen for the current instruction.

For an ADD, control may need to arrange that:

- the selected source registers are read;
- the ALU operation is ADD;
- the result is written to the destination register;
- FLAGS are updated;
- PC advances correctly.

For STORE, the choices are different. For JMP, PC receives a target address instead of simply advancing.

The instruction decoder and control logic turn opcode bits into these control decisions.

> **How does the hardware know that opcode 0x20 means ADD?**
>
> Because the control logic is designed so that the bit pattern assigned to ADD selects the datapath actions required by the ISA. The meaning is created by the architecture specification and realized by logic.

## Clock and state transitions

Synchronous digital hardware commonly uses a clock to coordinate when stored state changes.

A useful simplified model is:

```text
current state
    ↓
combinational logic calculates next values
    ↓
clock edge
    ↓
registers capture next state
    ↓
new current state
```

This connects directly to the simulator idea of deterministic state transitions, although the simulator's conceptual microsteps are **not a promise of exact FPGA timing**.

That distinction matters.

## Fetch, decode and execute in hardware

Our familiar cycle can now be viewed as datapath and control activity.

### Fetch

Use PC to address memory and obtain the opcode. Advance or otherwise prepare PC according to the instruction encoding.

### Decode

Interpret opcode bits and determine instruction form and required operands.

### Execute

Select ALU, memory, register, stack or control-flow actions and commit the architectural result.

A simple implementation may use several clock cycles for one architectural instruction. A different implementation could organize the work differently and still implement exactly the same ISA.

## Architecture versus implementation

This is one of the most important distinctions in the course.

**Architecture** includes observable rules such as:

- instruction encodings;
- register behaviour;
- flag semantics;
- memory-visible effects;
- CALL/RET stack convention;
- reset state.

**Implementation** includes internal choices such as:

- number of internal cycles;
- bus structure;
- multiplexers;
- control-state encoding;
- FPGA block RAM use;
- whether some operations share hardware.

Software should depend on the architecture, not accidental internal details.

## Why an FPGA?

An **FPGA** is programmable digital hardware. Instead of writing software that simulates EduCPU instructions, we can describe logic that physically realizes registers, ALU operations, control and datapath inside the FPGA fabric.

The progression is:

```text
ISA specification
      ↓
reference software CPU
      ↓
tests / qualification
      ↓
HDL implementation
      ↓
simulation
      ↓
FPGA synthesis
      ↓
hardware execution
```

The reference model becomes extremely valuable here: the FPGA implementation can be tested against already-defined architectural behaviour.

## Same program, different realization

Imagine the same machine-code program running on:

1. the Python reference CPU;
2. the EduCPU emulator;
3. a future FPGA EduCPU.

If all three correctly implement the ISA, the program should observe the same architectural results.

Internally they may be completely different.

This is why we froze ISA v0 before building later layers: compiler, emulator and hardware need a stable contract.

## From ADD to hardware thinking

Take:

```asm
MOVI R0, 20
MOVI R1, 22
ADD R0, R1
HALT
```

For ADD, answer:

1. Where are the two input values stored?
2. Which datapath routes carry them to the ALU?
3. Which ALU operation is selected?
4. Where is the result written?
5. Which flags are updated?
6. What happens to PC?
7. Which of these behaviours are required by the ISA, and which depend on implementation?

That last question is the key to moving from programmer to CPU designer.

## Exercises

### Understanding

1. What is the difference between a register and an ALU?
2. What is a datapath?
3. What does control logic do?
4. Why does opcode 0x20 cause ADD behaviour?
5. Can two different hardware designs implement the same ISA?

### Practice

Choose MOVI, LOAD, STORE and JMP. For each instruction, draw only the components that need to participate and arrows showing the important data movement.

### Explore

Design a conceptual control sequence for CALL.

Remember the architectural requirements already established by EduCPU:

- save the return PC;
- push its high byte then low byte;
- leave the low byte at MEM[SP];
- load PC with the target.

Do not worry yet about the exact number of FPGA clock cycles.

## Check your understanding

Explain this sentence:

> A CPU is not an instruction list. It is state plus logic and controlled movement of information that realizes the instruction list.

Then explain why the Python reference CPU and a future FPGA can both be “EduCPU”.

## Where we go next

You now have the complete conceptual journey:

```text
bits
→ logic and storage
→ CPU state
→ instructions
→ machine code
→ assembly
→ stack and ABI
→ compiler
→ IR and code generation
→ objects and linking
→ execution
→ datapath and control
→ hardware realization
```

The next project milestone takes this foundation toward the **EduCPU emulator**, followed later by the **FPGA CPU implementation**. The ISA and qualification tests remain the contract that all realizations must obey.
