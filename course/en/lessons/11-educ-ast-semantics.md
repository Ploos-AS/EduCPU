# 11 — EduC, AST and semantic analysis

## Learning objectives

After this lesson, you should be able to distinguish tokens, syntax and semantics, read a small EduC AST, explain what the parser does, and identify errors that semantic analysis catches after parsing.

## From characters to structure

Consider:

```c
byte main() {
    byte x = 40;
    return x + 2;
}
```

To us, this already looks structured. To the compiler it begins as characters.

The front end gradually gives those characters meaning:

```text
source characters
      ↓ lexer
tokens
      ↓ parser
AST
      ↓ semantic analysis
checked AST/program
```

Each stage answers a different question.

## Tokens

The lexer recognizes useful pieces of text.

For part of the example, tokens include concepts such as:

```text
byte   main   (   )   {   byte   x   =   40   ;
return x      +   2   ;   }
```

A token says what kind of lexical item was found. It does not yet describe the complete program structure.

## The AST

The parser consumes tokens according to EduC grammar and builds an **Abstract Syntax Tree**.

A simplified view of the example is:

```text
Program
└── Function main : byte
    ├── VarDecl x : byte
    │   └── Literal 40
    └── Return
        └── Add
            ├── Name x
            └── Literal 2
```

The tree is *abstract* because punctuation needed to write the source does not have to become a node. What matters is the program structure.

> **How does EduCPU know that `x + 2` is an addition?**
>
> It does not. The parser recognizes the source-language structure. Much later, lowering and code generation translate that structure into operations that eventually become an ADD instruction or equivalent machine-code sequence.

## Syntax versus semantics

A parser answers roughly:

> Is this text shaped like an EduC program?

Semantic analysis asks:

> Do the names, types, calls and returns make sense according to EduC rules?

For example:

```c
byte main() {
    return missing + 2;
}
```

can have valid grammatical structure while still referring to an unknown name. That is a semantic error.

## What EduC semantic analysis checks

EduC v0 checks rules including:

- function names must not be duplicated;
- local names must not be duplicated in their allowed scope;
- referenced names must exist;
- calls must target declared functions;
- argument count and types must match;
- assignments must respect types;
- return expressions must match the function return type;
- non-void functions must conservatively return on all paths.

The important lesson is that **valid syntax is not the same as a valid program**.

## Types in EduC v0

EduC deliberately has a small type system:

- `byte`: unsigned 8-bit value;
- `bool`: logical value represented as 0 or 1;
- `void`: function return type only.

The small language keeps the compiler inspectable. We can learn the complete rules instead of hiding complexity behind a large production language.

## Worked example

The CI-tested source is `course/examples/lesson11-ast-semantics.educ`:

```c
byte add(byte a, byte b) {
    return a + b;
}

byte main() {
    byte answer = add(20, 22);
    return answer;
}
```

The course test parses this exact file, checks semantic validity and inspects its AST structure.

It also creates an intentionally invalid variant using an unknown name and verifies that semantic analysis rejects it.

This matters: the lesson is tested against the real front end rather than a hand-written picture that could drift away from the implementation.

## Observe the real compiler

Use the EduC CLI to inspect stages separately:

```text
tokens → AST → semantic check
```

Compare the source with the AST. Find:

1. punctuation that disappears from the AST;
2. names that remain;
3. expression nesting;
4. function and return types.

Then introduce one error at a time and identify which stage rejects it.

## Exercises

### Understanding

1. What does the lexer produce?
2. What does the parser produce?
3. Why is the tree called abstract?
4. Give an example of syntactically valid but semantically invalid EduC.
5. Why does type checking happen before machine code exists?

### Practice

Modify the fixture so `main` declares a `bool` and returns it from a `byte` function. Predict whether parsing succeeds and whether semantic analysis succeeds.

Then call `add` with one argument instead of two.

### Explore

Take a nested expression such as:

```c
return a + b - 1;
```

Predict the AST shape before asking the compiler to display it.

Change the parentheses and observe how the tree changes.

## Check your understanding

Complete the questions:

```text
lexer:    what ______ are present?
parser:   how are they ______?
semantic: does that structure ______ according to the language rules?
```

Why is it useful to keep these jobs separate?

## Prediction exercise

Before displaying the AST, draw your own tree for:

```c
return a + b - 1;
```

First decide how the expression groups. Then run the parser and compare the tree.

For semantics, create one syntactically valid but semantically invalid variant. **Predict which stage should reject it before running the compiler.**

## Tools

Use the real course fixture: `course/examples/lesson11-ast-semantics.educ`.

**EduGuide:** use the guided PREDICT → OBSERVE → EXPLAIN workflow. Predict important compiler-stage or machine-state changes before running the fixture, then compare them with the observation.

## Next

Next we lower the checked program into **EduIR** and see how high-level expressions become explicit, machine-independent operations ready for code generation.
