# 12 — EduIR and code generation

## Learning objectives

After this lesson, you should be able to explain why a compiler uses an intermediate representation, read simple EduIR, distinguish lowering from code generation, and trace EduIR values into stack slots, registers and EduASM.

## Why add another representation?

After parsing and semantic analysis, the compiler has a checked high-level program. It could try to generate machine instructions immediately, but that would mix several jobs together.

EduCPU instead lowers the program to **EduIR**.

EduIR is a small, pedagogical, non-SSA intermediate representation. It makes operations explicit while remaining independent of physical EduCPU registers and instruction encodings.

The path is:

```text
checked EduC AST
      ↓ lowering
EduIR
      ↓ code generation
EduASM
```

This separation lets us inspect *what the program does* before deciding *how EduCPU will do it*.

## Source variables and temporary values

Consider:

```c
byte main() {
    byte x = 40;
    return x + 2;
}
```

A simplified EduIR-style view is:

```text
const %t0, 40
copy x, %t0
const %t1, 2
add %t2, x, %t1
ret %t2
```

Temporary names such as `%t0` are compiler-created values. `x` is a source-level variable.

The exact IR emitted by the tool is authoritative; this simplified view is for learning the roles of the operations.

> **How does EduCPU know what `%t2` means?**
>
> It never does. EduIR exists only inside the compiler. Code generation must choose concrete storage and instructions before the CPU sees anything.

## Control flow becomes explicit

High-level constructs also become explicit.

An EduC `if` can lower into labels, a conditional branch and jumps. A `while` becomes labels and a backwards control-flow edge.

This is useful because the backend no longer needs to understand the full syntax of an EduC `while`. It only needs to translate a small set of IR operations.

## Code generation chooses machine resources

The EduCPU v0 backend uses a deliberately simple strategy: parameters, source variables and compiler temporaries receive one-byte stack slots.

The generated function therefore has a frame:

```asm
ENTER n
...
LEAVE n
RET
```

Values are moved between stack slots and scratch registers as operations are performed.

This is not intended to be an optimizing register allocator. It is intended to be predictable and teachable.

## From an IR add to EduASM

Suppose EduIR needs to add two values.

The backend may need to:

1. load one value from its stack slot;
2. load the other into another register;
3. execute `ADD`;
4. store the result into the destination slot.

So one conceptual IR operation can require several machine instructions.

That is an important compiler lesson:

```text
one source operation ≠ one IR operation ≠ one machine instruction
```

## Function calls meet the ABI

For a call, code generation must turn abstract arguments into the ABI rules from Lesson 09.

Arguments are loaded into R0–R3, `CALL` transfers control, and the return value arrives in R0. If the IR needs that result later, the backend stores it into the stack slot assigned to the destination value.

The ABI is therefore the contract between compiler-generated caller and callee code.

## Worked example

The CI-tested source is `course/examples/lesson12-ir-codegen.educ`:

```c
byte add_two(byte x) {
    byte y = x + 2;
    return y;
}

byte main() {
    return add_two(40);
}
```

The course test runs the real pipeline through:

```text
parse → semantic analysis → EduIR → EduASM → object → link → execute
```

It checks that EduIR contains the functions and arithmetic/call operations, that generated assembly contains frame and call machinery, and that the final program returns 42.

## Inspect the stages

For the fixture, compare:

### EduC

Names and structured expressions are convenient for humans.

### EduIR

Operations, values and control flow are explicit, but there are no physical stack addresses or encoded opcodes.

### EduASM

The ABI, registers, stack-frame instructions and concrete control transfers are visible.

### Machine code

Names such as `x`, `%t0` and `add_two` no longer need to exist as source-language concepts.

Each stage answers a different engineering question.

## Exercises

### Understanding

1. Why not generate machine code directly from the AST?
2. What is the difference between a source variable and an EduIR temporary?
3. Does EduCPU ever execute EduIR?
4. Why can one IR operation require several instructions?
5. Where does the ABI first become concrete in this pipeline?

### Practice

Change `x + 2` to `x + 3`. Predict which high-level stages remain structurally similar and which emitted constant byte must change.

Add another local variable. Inspect how the generated stack frame changes.

### Explore

Write an EduC `if` or `while`. Compare its structured AST with its explicit EduIR labels and branches, then compare those with EduASM branch instructions.

Find one compiler-created temporary and follow it from EduIR to the stack slot used by generated code.

## Check your understanding

Explain the boundary:

```text
EduIR: what operations and values are needed
EduASM: how EduCPU resources perform them
```

Why is that boundary useful both for compiler design and for teaching?

## Next

Next we follow generated assembly into **object files, relocations and linking**, where separately translated pieces finally receive concrete addresses.
