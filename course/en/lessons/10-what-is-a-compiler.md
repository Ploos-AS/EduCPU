# 10 — What is a compiler?

## Learning objectives

After this lesson, you should be able to explain why a compiler exists, distinguish source language from machine language, name the major EduC compilation stages, and follow a small expression from EduC toward EduCPU instructions.

## A translation problem

Humans usually prefer to write:

```c
byte add(byte a, byte b) {
    return a + b;
}
```

EduCPU cannot execute that text. It executes bytes defined by its ISA.

A **compiler** translates a program expressed in one language into a lower-level representation while preserving the program's intended behaviour.

For EduCPU, the complete teaching path is:

```text
EduC source
    ↓ parse
AST
    ↓ semantic analysis
checked program
    ↓ lower
EduIR
    ↓ code generation
EduASM
    ↓ assemble
object file
    ↓ link
machine-code bytes
    ↓ execute
EduCPU state changes
```

The intermediate stages are intentional. They let us inspect what each tool has learned and what information it adds or removes.

> **How does EduCPU know what the EduC program means?**
>
> It does not. The CPU never sees EduC, an AST or EduIR. Compiler and assembler stages progressively translate the program until only ISA-defined bytes remain. The CPU only executes those bytes.

## Parsing: structure from text

A parser turns source text into a structured representation called an **Abstract Syntax Tree (AST)**.

For:

```c
return a + b;
```

the important structure is roughly:

```text
Return
└── Add
    ├── Name a
    └── Name b
```

The AST records relationships that are only implicit in the source characters.

## Semantic analysis: is it meaningful?

Syntactically valid text can still violate language rules.

Semantic analysis checks facts such as:

- names must exist;
- function calls must match declared functions;
- argument types must match;
- return values must match the function type;
- duplicate local names are rejected.

This stage answers language-level questions before machine code exists.

## EduIR: make operations explicit

EduCPU uses a small pedagogical intermediate representation called **EduIR**.

A high-level expression such as:

```c
byte answer = add(20, 22);
```

can be lowered into explicit operations involving constants, calls and copies.

EduIR is deliberately not machine assembly. It has temporary values and source-level concepts without forcing the compiler to choose physical registers immediately.

## Code generation

The backend turns EduIR into EduASM that obeys the EduCPU ISA and ABI.

For example, arguments must ultimately be placed where ABI v0 requires them — R0, R1, R2 and R3 — before CALL.

Compiler-generated values may also need stack slots. This is where the stack and ABI from the previous lessons become practical compiler machinery.

## Assembly and linking are separate jobs

The compiler does not need to solve everything itself.

EduASM converts assembly into object data and relocation information. The linker combines objects and resolves addresses between them. Only then do we have the final machine-code image.

Keeping these stages separate makes the toolchain easier to inspect and teaches why real systems use assemblers, object files and linkers.

## Worked example

The CI-tested fixture is `course/examples/lesson10-compiler.educ`:

```c
byte add(byte a, byte b) {
    return a + b;
}

byte main() {
    return add(20, 22);
}
```

The test sends this same source through the real EduC compiler pipeline and executes the resulting bytes on the reference CPU.

The expected result is 42.

The interesting part is not merely that 42 appears. Follow where the meaning changes representation:

```text
20 + 22
→ source expression
→ AST nodes
→ EduIR operations
→ generated EduASM
→ encoded bytes
→ register/stack operations
→ R0 = 42
```

## Compiler versus CPU

A compiler reasons about language structure and translates it ahead of execution.

The CPU performs the much smaller repeated job we already know:

```text
fetch → decode → execute → continue
```

This separation is fundamental. A sophisticated source language can run on a simple CPU because software performs the translation.

## Exercises

### Understanding

1. Why can EduCPU not execute EduC source directly?
2. What does an AST represent?
3. What kind of errors belong to semantic analysis?
4. Why is EduIR useful?
5. Which tool finally turns symbolic assembly into encoded instruction bytes?

### Practice

Change the constants in the fixture from 20 and 22 to two other values whose sum fits in a byte. Predict the return value before compiling.

Then change the function call so an argument has the wrong type. Which compilation stage should reject it?

### Explore

Run the compiler with its AST, IR, assembly and compile-trace outputs. Compare the same operation at each stage.

Find one fact that exists in EduC but disappears before machine code, and one low-level detail that appears only during code generation.

## Check your understanding

Explain this sentence:

> The compiler understands EduC structure; the CPU understands only its ISA.

Where, precisely, does the connection between those two worlds get created?

## Next

Next we inspect the first stages in detail: **EduC, the AST and semantic analysis**.
