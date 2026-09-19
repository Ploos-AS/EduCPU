# EduSim — pedagogical simulator/debugger

EduSim is the teaching-oriented execution environment for EduCPU. It is intentionally distinct from the later emulator.

## Purpose

The simulator answers **why and how did the machine state change?** rather than merely running a binary quickly.

Current terminal interface supports:

- instruction stepping;
- continuous run with a safety limit;
- register, PC, SP and FLAGS view;
- decoded next instruction;
- per-step state-change reporting;
- memory inspection;
- breakpoints;
- memory watchpoints;
- reset;
- conceptual fetch/decode/execute micro-operation explanation.

Run:

```sh
PYTHONPATH=reference:tools python tools/edusim.py examples/sum.bin
```

Typical commands:

```text
step
state
micro
mem 0xffe0 32
break 0x0006
watch 0x0100
run
reset
quit
```

## Simulator versus emulator

EduSim may deliberately expose idealized conceptual stages. These are pedagogical views and are not claims that a future FPGA implementation has exactly those internal cycles.

The M8 emulator instead focuses on faithfully behaving like the architectural machine.

## M3 visual model

For each instruction, the learner should ultimately be able to correlate:

```text
source / EduASM
       ↓
instruction bytes
       ↓
FETCH
       ↓
DECODE
       ↓
operand reads
       ↓
ALU / memory / control action
       ↓
writeback + flags
       ↓
new architectural state
```

The terminal debugger establishes the deterministic state/trace semantics. Rich graphical datapath visualization can be built on the same model rather than inventing separate execution behavior.
