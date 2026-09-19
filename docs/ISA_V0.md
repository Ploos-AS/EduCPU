# EduCPU ISA v0

Status: M1 architectural baseline.

EduCPU is an 8-bit, byte-addressable educational architecture with a 16-bit address space. The ISA prioritizes visible, regular behavior over density or historical compatibility.

## Programmer-visible state

- R0-R7: eight 8-bit general-purpose registers.
- PC: 16-bit program counter.
- SP: 16-bit stack pointer.
- FLAGS: 8-bit status register.
- MEM: 65536 bytes, addresses 0x0000-0xFFFF.

R0-R7 are architecturally identical. No general register has an implicit special role.

## FLAGS

| Bit | Name | Meaning |
|---|---|---|
| 0 | Z | result is zero |
| 1 | N | result bit 7 is set |
| 2 | C | carry out / no-borrow on subtraction |
| 3 | V | signed overflow |
| 4-7 | - | reserved, read as zero |

Logical operations update Z and N and clear C and V. MOV/LOAD/STORE do not modify flags. ADD/SUB/CMP update Z,N,C,V.

## Byte order

EduCPU is little-endian for 16-bit values: low byte at the lower address.

## Reset state

On RESET:

- R0-R7 = 0
- FLAGS = 0
- SP = 0xFF00
- PC = 0x0000

The top 256 bytes are therefore convenient for the introductory stack while remaining ordinary memory.

## Stack

The stack grows downward.

PUSH byte:
1. SP = SP - 1
2. MEM[SP] = value

POP byte:
1. value = MEM[SP]
2. SP = SP + 1

CALL pushes the 16-bit return PC as two byte pushes in high-byte then low-byte order, so the low byte is at MEM[SP] after the operation. RET reconstructs the address accordingly.

## Instruction encoding

All instructions begin with a one-byte opcode. Operand bytes follow the opcode. Register operands are encoded as one byte containing a register number 0-7. This is intentionally less dense than packing register fields into opcode bits: students can inspect bytes directly.

16-bit addresses are encoded low byte, then high byte.

### Core opcode map

| Opcode | Instruction | Bytes | Meaning |
|---|---|---:|---|
| 00 | NOP | 1 | no operation |
| 01 | HALT | 1 | stop execution |
| 10 | MOV rd,rs | 3 | rd = rs |
| 11 | MOVI rd,imm8 | 3 | rd = imm8 |
| 12 | LOAD rd,[addr16] | 4 | rd = MEM[addr] |
| 13 | STORE [addr16],rs | 4 | MEM[addr] = rs |
| 14 | LOADR rd,[ra] | 3 | rd = MEM[zero-extended ra] |
| 15 | STORER [ra],rs | 3 | MEM[zero-extended ra] = rs |
| 20 | ADD rd,rs | 3 | rd = rd + rs |
| 21 | ADDI rd,imm8 | 3 | rd = rd + imm8 |
| 22 | SUB rd,rs | 3 | rd = rd - rs |
| 23 | SUBI rd,imm8 | 3 | rd = rd - imm8 |
| 24 | CMP ra,rb | 3 | flags from ra - rb |
| 25 | CMPI ra,imm8 | 3 | flags from ra - imm8 |
| 28 | AND rd,rs | 3 | bitwise AND |
| 29 | OR rd,rs | 3 | bitwise OR |
| 2A | XOR rd,rs | 3 | bitwise XOR |
| 2B | NOT rd | 2 | bitwise complement |
| 2C | SHL rd | 2 | shift left, outgoing bit to C |
| 2D | SHR rd | 2 | logical shift right, outgoing bit to C |
| 30 | JMP addr16 | 3 | PC = addr |
| 31 | JZ addr16 | 3 | jump if Z=1 |
| 32 | JNZ addr16 | 3 | jump if Z=0 |
| 33 | JC addr16 | 3 | jump if C=1 |
| 34 | JNC addr16 | 3 | jump if C=0 |
| 35 | JN addr16 | 3 | jump if N=1 |
| 36 | JP addr16 | 3 | jump if N=0 |
| 38 | CALL addr16 | 3 | push return address, jump |
| 39 | RET | 1 | pop return address |
| 40 | PUSH rs | 2 | push register byte |
| 41 | POP rd | 2 | pop byte into register |

Opcodes not listed above are invalid in ISA v0 and trap the reference model with an INVALID_OPCODE result. They do not silently act as NOP.

## Addressing modes

ISA v0 deliberately has only four visible forms:

1. register;
2. immediate 8-bit;
3. absolute 16-bit memory/address;
4. simple register-indirect memory.

The register-indirect form zero-extends an 8-bit register and therefore addresses page zero (0x0000-0x00FF). Full 16-bit pointer/index registers are intentionally deferred: M1 favors conceptual simplicity and explicit absolute addressing. This decision may be revisited before ISA v1 if EduC/ABI teaching demonstrates a clear need.

## PC semantics

PC points to the next opcode to fetch. Normal instructions advance PC by their encoded length. Branches replace PC only when taken. CALL pushes the address immediately following the CALL instruction.

## Arithmetic

All 8-bit arithmetic wraps modulo 256.

For ADD, C is the ninth carry bit. V is set when two operands with the same sign produce a result with the opposite sign.

For SUB/CMP, C=1 means no borrow (unsigned left operand >= right operand). V indicates signed subtraction overflow.

## Machine control

HALT leaves PC pointing immediately after HALT and enters a halted state. RESET clears halted state.

Invalid register operand bytes (>7) produce INVALID_OPERAND.

## Memory-mapped I/O

The CPU itself defines byte reads/writes only. Device semantics are part of the machine model, not the ISA. The top page 0xFF00-0xFFFF is reserved for future teaching-machine I/O/system conventions; M1 reference memory remains deterministic RAM except where a harness explicitly supplies a device.

## Architectural trace

Every reference-model step can be represented as:

- PC before;
- instruction bytes;
- decoded operation;
- register reads;
- memory reads;
- ALU/result;
- memory/register writes;
- flags after;
- PC after;
- halted/trap state.

This trace is the contract later used by simulator, emulator, FPGA testbench, and teaching visualizations.
