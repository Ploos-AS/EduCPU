# EduCPU Course

**Learn how a computer works, one understandable layer at a time.**

EduCPU is a deliberately small teaching computer.

## Before you begin

The course is designed for beginners. You do not need prior knowledge of CPU design, assembly or programming. Basic arithmetic is useful, but the required concepts are introduced as you go. The course works for both self-study and classroom/lab use.

Allow roughly **30–60 minutes per lesson** for the reading and basic exercises. Lessons 10–15 may take **60–120 minutes** when you complete the practical exercises and follow the full toolchain.

## Terminology we use consistently

- **bit / byte** — one bit is 0 or 1; one byte is 8 bits.
- **register** — a small, named storage location inside the CPU.
- **machine state** — the values in registers, PC, SP, FLAGS and other relevant architectural state.
- **instruction** — an architectural operation the CPU is required to perform.
- **opcode** — the bit pattern identifying an instruction's operation.
- **ISA** — the contract describing instructions, encoding and observable behaviour.
- **reference CPU** — the authoritative software model used to define and check architectural behaviour.
- **emulator** — a separate implementation that emulates EduCPU and can be compared with the reference CPU.
- **datapath** — the hardware structure that moves and processes values.
- **control logic** — the logic that selects which datapath actions occur.
- **implementation** — a concrete realization of the ISA, such as software or FPGA logic.

**Architecture and implementation are kept separate throughout the course.** EduCPU is a standalone project and teaching system. External CPU or hardware projects are not part of the EduCPU architecture or roadmap.

## Course map

```text
bits → logic → CPU state → ISA → assembly → stack/ABI
                                      ↓
                         compiler → IR → object/linking
                                      ↓
                             machine code → CPU
                                      ↓
                         datapath/control → FPGA
```

You do not need to understand the whole map beforehand. The course builds it layer by layer.

**Tools from lesson 3 onward:** EduVis lets you inspect CPU state step by step in a browser. EduGuide supports the course's **PREDICT → OBSERVE → EXPLAIN** workflow. This course starts with bits and builds toward a complete understanding of how an EduC program becomes machine instructions and observable CPU state changes.

## The journey

1. Bits, bytes and hexadecimal
2. Logic and storing information
3. What is a CPU?
4. Registers, memory and machine state
5. Instructions and machine code
6. Assembly and what an assembler does
7. Arithmetic, flags and branches
8. The stack
9. Functions, CALL/RET and the ABI
10. What is a compiler?
11. EduC, AST and semantic analysis
12. EduIR and code generation
13. Objects, relocations and linking
14. Following a complete program from EduC to execution
15. How a CPU can be built: ALU, datapath, control and the road to FPGA

Throughout the course we repeatedly ask: **How does EduCPU know?**

## Further reading

If you want a companion book for the same kind of bottom-up exploration, J. Clark Scott's *But How Do It Know? — The Basic Principles of Computers for Everyone* is recommended further reading. It develops the ideas from simple digital logic toward a working CPU, while EduCPU remains an independent project and course.

**Book link:** coming soon. When a purchase link is an affiliate link, it will be clearly identified; Ploos AS may receive a commission at no additional cost to you.


## Continue learning

After EduCPU, **EduAVR** is a natural next step: move from the deliberately small teaching CPU to a real AVR microcontroller, real embedded tooling and physical hardware. EduCPU explains the mechanisms first; EduAVR lets you apply the same ideas on a practical microcontroller platform.

Continue with [EduAVR](https://ploos-as.github.io/EduAVR/).
