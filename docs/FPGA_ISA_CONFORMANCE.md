# FPGA ISA v0 differential coverage

This matrix maps every frozen EduCPU ISA v0 opcode to at least one reference↔RTL differential program. Differential comparison includes PC, SP, FLAGS, R0-R7, HALT/trap state, and a signature of the complete 64 KiB memory image.

| Opcode | Instruction | Differential vector |
|---|---|---|
| 00 | NOP | nop_halt |
| 01 | HALT | nop_halt |
| 10 | MOV | mov |
| 11 | MOVI | mov, mov_alu, others |
| 12 | LOAD | memory_abs |
| 13 | STORE | memory_abs |
| 14 | LOADR | memory_reg |
| 15 | STORER | memory_reg |
| 16 | LOADS | memory_sp |
| 17 | STORES | memory_sp |
| 18 | ENTER | frame |
| 19 | LEAVE | frame |
| 20 | ADD | add_reg |
| 21 | ADDI | mov_alu, branches_flags |
| 22 | SUB | sub_cmp |
| 23 | SUBI | mov_alu, subi |
| 24 | CMP | sub_cmp |
| 25 | CMPI | branch, sub_cmp, jnz |
| 28 | AND | logic_full |
| 29 | OR | logic_full |
| 2A | XOR | logic_full |
| 2B | NOT | logic_full |
| 2C | SHL | logic_shift |
| 2D | SHR | logic_shift |
| 30 | JMP | jmp |
| 31 | JZ | branch |
| 32 | JNZ | jnz |
| 33 | JC | branches_flags |
| 34 | JNC | branches_flags |
| 35 | JN | branches_flags |
| 36 | JP | branches_flags |
| 38 | CALL | call_ret |
| 39 | RET | call_ret |
| 40 | PUSH | stack |
| 41 | POP | stack |

## Trap coverage

- Invalid opcode: `invalid_opcode`
- Invalid register operand: `invalid_register`

## Closing gate

Full ISA v0 differential conformance is complete: every frozen opcode has an executed differential vector, with invalid-opcode and invalid-register trap coverage. The matrix remains in source control as the explicit coverage record.
