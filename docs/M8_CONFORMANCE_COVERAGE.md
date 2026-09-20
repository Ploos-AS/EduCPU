# M8 ISA v0 Conformance Coverage

This report tracks the independent emulator against the frozen ISA v0 opcode map in
`docs/ISA_V0.md`.

| Opcode | Instruction | Emulator | Differential test |
|---|---|---|---|
| 00 | NOP | PASS | PASS |
| 01 | HALT | PASS | PASS |
| 10 | MOV | PASS | PASS |
| 11 | MOVI | PASS | PASS |
| 12 | LOAD | PASS | PASS |
| 13 | STORE | PASS | PASS |
| 14 | LOADR | PASS | PASS |
| 15 | STORER | PASS | PASS |
| 16 | LOADS | PASS | PASS |
| 17 | STORES | PASS | PASS |
| 18 | ENTER | PASS | PASS |
| 19 | LEAVE | PASS | PASS |
| 20 | ADD | PASS | PASS |
| 21 | ADDI | PASS | PASS |
| 22 | SUB | PASS | PASS |
| 23 | SUBI | PASS | PASS |
| 24 | CMP | PASS | PASS |
| 25 | CMPI | PASS | PASS |
| 28 | AND | PASS | PASS |
| 29 | OR | PASS | PASS |
| 2A | XOR | PASS | PASS |
| 2B | NOT | PASS | PASS |
| 2C | SHL | PASS | PASS |
| 2D | SHR | PASS | PASS |
| 30 | JMP | PASS | PASS |
| 31 | JZ | PASS | PASS |
| 32 | JNZ | PASS | PASS |
| 33 | JC | PASS | PASS |
| 34 | JNC | PASS | PASS |
| 35 | JN | PASS | PASS |
| 36 | JP | PASS | PASS |
| 38 | CALL | PASS | PASS |
| 39 | RET | PASS | PASS |
| 40 | PUSH | PASS | PASS |
| 41 | POP | PASS | PASS |

## Cross-layer qualification

- Reset state is differential-tested.
- Invalid opcodes are differential-tested.
- Invalid register operands are differential-tested.
- Absolute, register-indirect and SP-relative memory are differential-tested.
- Arithmetic and logical flag behavior is differential-tested.
- Branch taken/not-taken behavior and little-endian addresses are differential-tested.
- Stack, CALL/RET and ENTER/LEAVE behavior are differential-tested.
- Compiler-generated EduC programs are differential-tested against the reference CPU.
- Deterministic memory-mapped device behavior has dedicated emulator tests.
- Debugger hooks, snapshots, bounded execution and deterministic traces have dedicated tests.

## Status

The opcode implementation and current differential suite cover every opcode listed by
ISA v0. Final M8 qualification still requires a clean CI run after the final cleanup,
plus explicit EduASM differential fixtures and any remaining machine-layer qualification
gates.
