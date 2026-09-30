# EduCPU Teaching Manifesto

## Ambition

EduCPU aims to become a classic, enduring course in **what a CPU is and how it works**.

A learner who completes EduCPU should be able to explain how a CPU works from logical building blocks to execution of a compiled program, and should be able to implement, simulate, debug and extend a simple CPU themselves.

The project is not primarily a collection of CPU features. Every architecture, tool and experiment exists to make computation understandable.

## The complete explanatory chain

EduCPU should make every important transition inspectable:

`bits → logic → storage → registers → ALU → datapath/control → machine state → fetch/decode/execute → ISA → memory → stack → CALL/RET → assembly → objects/linking → ABI → C → machine code → interrupts/I/O → RTL → FPGA`

Advanced topics extend that chain only when they explain why real CPUs need them.

## Teaching principles

### Nothing magical
Important mechanisms must not appear as unexplained black boxes. Abstractions are introduced after the learner has enough concrete machinery to understand what they hide.

### See it, predict it, run it, inspect it
For important operations the learner should:
1. see the starting machine state;
2. predict the result;
3. execute the operation;
4. inspect the resulting state;
5. explain why it changed.

### One concept at a time
New complexity must have a reason. Prefer the smallest mechanism that exposes the concept clearly.

### Build the abstraction
The learner should encounter the problem before the abstraction that solves it. Stack frames, assemblers, linkers, ABIs, compilers, interrupts and I/O should feel necessary rather than arbitrary.

### Connect software to hardware
A concept is strongest when it can be followed through source, machine code, architectural state, emulator/reference behavior and RTL.

### Multiple implementations are a teaching asset
Reference CPU, simulator, independent emulator and RTL are not redundant. They expose different views and allow differential qualification of the same architecture.

### Experiments must teach
M10 features are laboratories for understanding real CPU design. A feature is not justified merely because modern processors have it.

## Course design test

Before adding a major feature or lesson, ask:

- What CPU concept does this make easier to understand?
- What prior problem motivates it?
- What state can the learner observe?
- What should the learner predict before running it?
- Can the concept be traced across software and hardware?
- Does it preserve a simpler path for beginners?

If those questions have weak answers, the feature belongs outside the core learning path or should be redesigned.

## End state

The culminating experience should connect the whole course: the learner runs on an FPGA the CPU they have already understood in software, instruction by instruction and state transition by state transition.

The desired reaction is not merely “I programmed a CPU.”

It is:

**“I understand why the CPU works.”**
