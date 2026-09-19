# EduASM v0

EduASM is the deliberately small assembly language for EduCPU.

## Syntax

- one instruction per line;
- labels end in `:`;
- operands are comma-separated;
- registers are `R0` through `R7`;
- hexadecimal numbers use `0x` or `$`;
- binary numbers use `0b`;
- decimal numbers need no prefix;
- `;` and `#` begin comments;
- brackets may be used around memory/address operands for readability.

Example:

```asm
start:
    MOVI R0, 10
    MOVI R1, 0

loop:
    ADD  R1, R0
    SUBI R0, 1
    CMPI R0, 0
    JNZ  loop
    HALT
```

EduASM intentionally maps closely to real ISA instructions. Convenience pseudo-instructions are deferred until their teaching effect is understood.

## Assembly

```sh
python tools/eduasm.py examples/sum.eduasm -o sum.bin --listing
```

The listing is an educational output: source, address and exact bytes are shown together.

## Disassembly

```sh
PYTHONPATH=tools python tools/edudis.py sum.bin
```

The disassembler uses the same instruction metadata as the assembler so opcode drift is minimized.

## Labels

Labels resolve to absolute 16-bit addresses. M2 does not yet define object files, relocations, sections or linking; those belong to M4.

## Errors

The assembler rejects unknown instructions, wrong operand counts, invalid registers, duplicate/bad labels, out-of-range immediates and out-of-range addresses.

The goal is that errors explain the learner's mistake rather than merely reporting parser failure.
