# M6 Qualification — EduC compiler back end

Status: **PASS**

Qualified commit: `52fbca668dbf20fd1e6c00c9b51a148a22e53cb2`  
GitHub Actions CI run: **#34** (`35488299045`)

## Scope

M6 qualifies the first complete EduC compiler back end and executable pipeline:

`EduC -> AST -> EduIR -> EduASM -> object -> EduLink -> EduCPU executable`

The back end implements the frozen ISA/ABI v0 model established in M4.

## Qualified capabilities

- EduIR validation before code generation.
- ABI v0 register parameters R0-R3 and R0 return values.
- Stack-backed parameters, locals and compiler temporaries.
- ENTER/LEAVE stack frames with balanced SP.
- byte constants, copies, addition and subtraction.
- bool NOT and unsigned byte comparisons.
- if/else and while control flow.
- function-local generated labels.
- ordinary, nested and void function calls.
- recursive calls.
- object assembly, relocations and linking.
- complete EduC CLI compilation to executable bytes.
- inspectable compile trace covering source, AST, EduIR, generated EduASM, symbols, instruction addresses and final machine bytes.

The compile trace is stage-level correlation. It does **not** claim precise EduC source-line-to-machine-instruction mapping; AST/IR source spans are not yet propagated.

## Automated qualification

CI run #34 executed the complete pytest suite on Python 3.11, 3.12 and 3.13. All three matrix jobs passed.

The suite contained **82 tests** and passed on all three jobs.

The tests include generated-program execution on the EduCPU reference CPU, including arithmetic, comparisons, control flow, calls, nested calls, recursion, stack restoration, void calls, object/link execution and the complete compiler/trace pipeline.

## Result

**M6 PASS.**

EduCPU now has a qualified pedagogical compiler path from EduC source to executable EduCPU machine code. M7 may build the guided teaching environment on this pipeline.

## Deferred improvements

These are useful follow-up work but are not M6 blockers:

- precise EduC source spans propagated through AST, EduIR and machine-code debug information;
- CLI mutual-exclusion/diagnostic hardening;
- packaging/installability cleanup;
- richer language features beyond EduC v0.
