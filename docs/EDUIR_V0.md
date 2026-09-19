# EduIR v0

EduIR is the deliberately simple intermediate representation between the EduC AST and EduCPU assembly. It exists to make compiler decisions visible.

## Model

- one function at a time;
- named source variables remain named;
- compiler temporaries are written `%t0`, `%t1`, ...;
- every operation has at most one result;
- control flow uses explicit labels and jumps;
- values retain EduC type: `byte` or `bool`;
- no registers, stack offsets or machine opcodes appear in IR.

Example:

```text
func byte add(byte a, byte b)
  %t0:byte = add a, b
  ret %t0
end

func byte main()
  %t0:byte = const 20
  %t1:byte = const 22
  %t2:byte = call add, %t0, %t1
  answer:byte = copy %t2
  %t3:byte = const 42
  %t4:bool = eq answer, %t3
  br %t4, if_then_0, if_else_1
if_then_0:
  ret answer
if_else_1:
  %t5:byte = const 0
  ret %t5
end
```

## Instructions

Value operations:
- `dst:type = const N`
- `dst:type = copy src`
- `dst:byte = add a, b`
- `dst:byte = sub a, b`
- `dst:bool = not a`
- `dst:bool = eq|ne|lt|le|gt|ge a, b`
- `dst:type = call name, args...`

Control:
- `label:`
- `jmp label`
- `br condition, true_label, false_label`
- `ret value`
- `ret`
- `callvoid name, args...`

EduIR is not SSA: named locals can be assigned repeatedly. Temporaries are single-definition by convention. This keeps the first compiler easy to inspect before introducing advanced compiler concepts.

## Lowering rules

Expressions are evaluated left-to-right. Each intermediate expression gets a temporary. `if` and `while` become explicit labels/branches. Function parameters and locals keep their source names. Register allocation and stack placement belong to M6, not EduIR.

The textual form is a teaching/debug representation. The in-memory representation is structured and validated independently.
