# EduCPU ISA Direction — M0

This is the design envelope, not the frozen opcode specification.

## Fundamental model

- 8-bit data path
- 16-bit address space (64 KiB)
- flat, byte-addressable memory
- memory-mapped I/O
- small general-purpose register set
- explicit PC and SP
- simple integer ALU
- deterministic sequential architectural execution

## Candidate programmer-visible state

M1 should evaluate eight 8-bit general registers R0-R7, a 16-bit PC, 16-bit SP, FLAGS, and 64 KiB memory. The exact register count is not frozen in M0.

Candidate flags are Z (zero), N (negative/sign), C (carry/borrow), and V (signed overflow).

## Instruction families

Target roughly 30-40 conceptual operations: data movement, arithmetic, logic, compare/test, shifts, load/store, stack, branches, call/return, and machine control. Friendly pseudo-instructions need not expand the real ISA.

## Addressing modes

Candidates are register, immediate, absolute memory, register-indirect, and—only if pedagogically worthwhile—a small indexed/displacement form.

## Encoding goals

The mapping between mnemonic/opcode, register/register field, literal/immediate bytes, addresses, and instruction length should be easy to inspect. Uniformity is more important than density.

## Stack and calls

Function calls are a core learning objective. The architecture must make push/pop, return addresses, CALL/RET, parameters, locals, stack frames, and recursion clear.

## Interrupts

Interrupts are valuable but should be introduced after ordinary fetch/decode/execute, branches, calls, and stack behavior are stable.

## Conceptual micro-operations

EduCPU may expose an explanatory trace such as FETCH address from PC → FETCH instruction → DECODE → READ operands → ALU → WRITE → FLAGS → PC. This is an explanatory model unless a specific microarchitecture is later formalized.

## M1 decisions

M1 must freeze register semantics, FLAGS layout, endianness, encoding, opcode allocation, addressing modes, arithmetic/flags, branches, stack growth and byte order, reset state, invalid-opcode behavior, and executable conformance vectors.
