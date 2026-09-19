# EduC v0 language specification

EduC is a deliberately small C-like language for learning how source code becomes machine code on EduCPU. It is not a C subset and does not promise C compatibility.

## Design rules

1. Source constructs must map visibly to the EduCPU/ABI.
2. The whole v0 language should fit in a beginner's mental model.
3. No implicit conversions that hide machine behavior.
4. Deterministic, useful diagnostics are part of the language experience.
5. Features are added because they teach something, not because C has them.

## Types

v0 has two value types:

- `byte`: unsigned 8-bit value, 0..255.
- `bool`: logical value, represented as 0 or 1.

`void` is allowed only as a function return type.

No pointers, arrays, structs, signed integers, strings, heap allocation or implicit widening exist in v0.

## Program structure

A program contains function definitions.

```c
byte add(byte a, byte b) {
    return a + b;
}

byte main() {
    return add(20, 22);
}
```

A function has a return type, name, zero to four byte/bool parameters, and a block. The four-parameter limit deliberately matches ABI v0 register arguments R0-R3.

## Statements

v0 statements are:

```c
byte x = expression;
bool flag = expression;
x = expression;
return expression;
return;
if (expression) { ... }
if (expression) { ... } else { ... }
while (expression) { ... }
expression;
```

Local variables are function-scoped in v0 even when declared inside a nested block. Shadowing is rejected.

## Expressions

Primary expressions:

- decimal integer literal: `0`..`255`
- `true`, `false`
- variable name
- function call
- parenthesized expression

Operators, highest precedence first:

1. unary `!`
2. `+`, `-`
3. `==`, `!=`, `<`, `<=`, `>`, `>=`

Arithmetic on `byte` wraps modulo 256, matching EduCPU. Comparisons and `!` produce `bool`.

No short-circuit `&&`/`||` in v0; they are deferred until control-flow lowering is taught.

## Control flow

`if` and `while` accept `bool`. EduC does not silently treat arbitrary byte values as booleans.

## Functions

- at most four parameters;
- arguments are evaluated left-to-right;
- recursion is allowed;
- `byte`/`bool` functions must return a value;
- `void` functions use `return;`;
- no overloading or variadic functions.

## Grammar sketch

```text
program      := function*
function     := type IDENT "(" params? ")" block
type         := "byte" | "bool" | "void"
params       := param ("," param)*
param        := value_type IDENT
block        := "{" statement* "}"
statement    := var_decl | assignment | return_stmt | if_stmt | while_stmt | expr_stmt
var_decl     := value_type IDENT "=" expression ";"
assignment   := IDENT "=" expression ";"
return_stmt  := "return" expression? ";"
if_stmt      := "if" "(" expression ")" block ("else" block)?
while_stmt   := "while" "(" expression ")" block
expr_stmt    := expression ";"
expression   := comparison
comparison   := additive (("=="|"!="|"<"|"<="|">"|">=") additive)*
additive     := unary (("+"|"-") unary)*
unary        := "!" unary | primary
primary      := NUMBER | "true" | "false" | IDENT | call | "(" expression ")"
call         := IDENT "(" arguments? ")"
arguments    := expression ("," expression)*
```

The executable parser is the normative syntax check during M5; this document explains the teaching contract.
