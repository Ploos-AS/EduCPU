# Exercise solutions

These solutions are companions to the lessons, not replacements for prediction and experimentation. Try each exercise first, then compare your reasoning.

## 01 — Bits, bytes and hexadecimal

42 is `00101010₂`, `0x2A`, and decimal 42. One byte has 256 possible patterns, from 0 through 255 when interpreted as an unsigned EduCPU byte.

## 02 — Logic and storing information

For `0xCC` and `0xAA`: AND = `0x88`, OR = `0xEE`, XOR = `0x66`; NOT `0xCC` = `0x33`. Logic computes values; registers or memory preserve state.

## 03 — What is a CPU?

A CPU needs stored state, a way to obtain instructions, decoding/control, and mechanisms such as an ALU and datapath to perform the required state transitions. Fetch/decode/execute describes the architectural process without requiring one internal hardware design.

## 04 — Machine state

After subtracting equal unsigned bytes, the result is zero, so Z=1. EduCPU's subtraction convention sets C=1 when no borrow is required. PC identifies the next instruction; SP identifies the stack position.

## 05 — Instructions and machine code

An opcode identifies the operation; operand bytes identify registers, immediate values or addresses. EduCPU 16-bit encoded addresses are little-endian: `0x1234` is stored as `34 12`.

## 06 — EduASM

Labels are assembler conveniences, not CPU state. A forward label requires its address to be discovered before its reference can be fully encoded, which is why the simple EduASM model uses two passes.

A countdown can be:

```asm
MOVI R0, 5
loop:
    SUBI R0, 1
    JNZ loop
HALT
```

## 07 — Arithmetic, FLAGS and branches

`255 + 1` wraps to 0 in an 8-bit register. Z is set because the result is zero and C records the carry. CMP updates flags without storing the subtraction result. JZ tests Z; JC tests C.

## 08 — The stack

The stack grows downward. PUSH first decrements SP and then writes. POP reads and then increments SP. Popping does not erase the old memory byte; it changes which part of memory is considered active stack state.

## 09 — Functions, CALL/RET and ABI

R0–R3 carry the first four byte arguments and R0 carries the primary byte return value. CALL saves its return PC on the stack; RET restores it. A correctly balanced function restores SP to its entry value.

## 10 — What is a compiler?

The compiler translates EduC through checked representations toward EduASM and object code. The assembler converts EduASM into encoded bytes/object data; the linker combines objects and resolves addresses. The CPU never executes EduC source.

## 11 — EduC, AST and semantic analysis

Parsing answers whether source has valid grammatical structure. Semantic analysis answers questions such as whether a variable exists, types match, a call has the right arguments, and a non-void function returns correctly.

## 12 — EduIR and code generation

EduIR makes compiler operations explicit without prematurely exposing machine registers and stack offsets. Code generation then maps values to stack-backed slots and ABI registers and emits concrete EduASM.

## 13 — Objects, relocations and linking

An export supplies a symbol; an import requests one. A relocation marks bytes that cannot receive their final value until link time. `abs16le` means a final absolute 16-bit address is written low byte first. The CPU sees only the patched numeric address.

## 14 — From EduC to execution

The downward chain is:

```text
source → AST → semantics → IR → assembly → object
→ relocation/link → bytes → CPU state transitions
```

A source call becomes an IR call during lowering, a CALL instruction during code generation, and a final numeric CALL target during linking. Only the final machine bytes are consumed by the CPU.

## 15 — How a CPU is built

Registers store state. The ALU computes. The datapath provides routes for values. Control logic selects the required routes and operations for the current instruction. Two implementations can use different internal circuits or timing while implementing the same ISA-visible behaviour.

For CALL, a conceptual implementation must save the return PC according to the defined high-byte/low-byte stack convention and then load PC with the target. The exact internal clock sequence is an implementation choice.
