# 13 — Object files, relocations and linking

## Learning objectives

After this lesson, you should be able to explain why separately assembled code cannot always know final addresses, read the important parts of an EduCPU object file, explain an `abs16le` relocation, and describe how the linker resolves an imported symbol.

## The address problem

Suppose one file contains:

```asm
.export main
.import add_two

main:
    MOVI R0, 40
    CALL add_two
    HALT
```

and another contains:

```asm
.export add_two

add_two:
    ADDI R0, 2
    RET
```

The assembler can encode most instructions immediately. But while assembling the first file, it does not yet know where `add_two` will live in the final program.

It must preserve that unresolved question.

## Object files

EduASM can produce an EduCPU object file rather than a final binary.

The v0 object format records information such as:

- encoded data bytes;
- exported symbols;
- local symbols;
- imported symbols;
- relocations.

A simplified object looks like:

```json
{
  "format": "educpu-object-v0",
  "data": "...",
  "exports": {"main": 0},
  "imports": ["add_two"],
  "relocations": [
    {"offset": 4, "type": "abs16le", "symbol": "add_two"}
  ]
}
```

The exact offset depends on the encoded program. The important idea is that the object says:

> these bytes need the final address of `add_two`.

## Exports and imports

An **export** makes a symbol available to other objects.

An **import** declares that this object needs a symbol supplied elsewhere.

The linker matches the two.

```text
main.eo                         math.eo
-------                         -------
imports add_two  ─────────────► exports add_two
exports main
```

This allows files to be assembled independently.

## Relocations

A relocation describes a place that must be patched once the final address is known.

EduCPU v0 supports the relocation type `abs16le` for a 16-bit absolute address stored little-endian.

If the linker finally places `add_two` at address `0x0010`, the relocated address bytes are:

```text
10 00
```

Low byte first, exactly as required by the ISA encoding.

> **How does EduCPU know that these bytes once referred to a symbol named `add_two`?**
>
> It does not. Symbol names and relocations are toolchain concepts. By execution time the linker has replaced the unresolved reference with numeric address bytes. The CPU only sees the final CALL operand.

## What the linker does

For the simple v0 format, the linker:

1. lays object data out in the final image;
2. calculates each object's base address;
3. creates the final symbol addresses;
4. resolves local and imported references;
5. applies relocations;
6. emits final bytes.

After linking, `CALL add_two` contains a concrete 16-bit address.

## Worked example

This lesson uses two CI-tested fixtures:

`course/examples/lesson13-main.eduasm`

```asm
.export main
.import add_two

main:
    MOVI R0, 40
    CALL add_two
    HALT
```

and `course/examples/lesson13-math.eduasm`

```asm
.export add_two

add_two:
    ADDI R0, 2
    RET
```

They are assembled independently into two objects.

The test verifies that the main object contains an unresolved `add_two` import and relocation. It then links both objects, checks the resolved symbol address and executes `main` on the reference CPU.

The final result is 42.

## Before and after linking

Before linking:

```text
CALL add_two
     ^ symbolic reference
```

Object file:

```text
instruction bytes + relocation("add_two")
```

After linking:

```text
CALL 0x....
     ^ numeric address
```

At runtime there is no linker lookup. The CPU follows the already encoded address.

## Why separate compilation matters

Separate objects let larger programs be built from independently translated pieces.

A compiler can generate one object while a library supplies another. Only the linker needs to know how all pieces fit together in the final address space.

EduCPU's format is intentionally small, but it demonstrates the same fundamental problem solved by object formats and linkers on larger systems.

## Exercises

### Understanding

1. Why can the assembler not always know a CALL target's final address?
2. What is the difference between an export and an import?
3. What information does a relocation preserve?
4. What does `abs16le` mean?
5. Does the CPU know symbol names at runtime?

### Practice

Add a second exported function to the math object and call it from the main object.

Before linking, predict which object contains the import and where a new relocation will be needed.

### Explore

Reverse the order of the two objects passed to the linker. Observe how base and symbol addresses change while program behaviour remains the same.

Inspect the final CALL operand bytes and decode the little-endian target address manually.

## Check your understanding

Complete the chain:

```text
symbolic CALL
→ object bytes + ______
→ linker resolves ______
→ numeric address bytes
→ CPU executes CALL
```

Which information exists only during build time?

## Tools

Use the real course fixture: `course/examples/lesson13-main.eduasm + lesson13-math.eduasm`.

**EduGuide:** use the guided PREDICT → OBSERVE → EXPLAIN workflow. Predict important compiler-stage or machine-state changes before running the fixture, then compare them with the observation.

## Next

Next we put everything together and follow **one complete program from EduC source all the way to execution**, correlating source, IR, generated assembly, bytes and CPU state.
