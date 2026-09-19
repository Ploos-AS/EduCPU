# EduCPU Project Charter

## Mission

EduCPU exists to teach how a computer executes programs by providing a complete, intentionally understandable virtual CPU and software toolchain.

A learner should be able to start with a high-level expression and trace it all the way down to individual CPU state changes.

## Scope

EduCPU includes a custom educational ISA, EduASM, assembler/disassembler, executable reference CPU model, interactive simulator, debugger, a simple object/link model when useful for teaching, EduC, an inspectable compiler, visualizations, and course material.

## Non-goals

EduCPU is not intended to compete with production CPUs, maximize performance or code density, preserve compatibility with an existing ISA, model every modern CPU complexity, require physical hardware, or hide complexity behind opaque tooling.

## Core learning outcomes

A learner should eventually be able to explain machine code and instruction encoding; fetch/decode/execute; registers, ALU, flags, memory, PC and stack; assembly translation; functions and stack frames; assemblers and linking; lexer/parser/AST/IR; compiler lowering; and how a program ultimately changes CPU and memory state.

## Architecture rule

When educational clarity conflicts with historical convention, implementation convenience, code density, or speed, educational clarity wins unless doing so would teach a materially false model.

Simplification is encouraged. Misrepresentation is not.

## Relationship to physical hardware

EduCPU is virtual by design. FPGA, hardware, or gate-level implementations may be explored later, but must adapt to the educational architecture rather than constrain it.

## Relationship to EduK8

EduCPU and EduK8 are independent projects. Compatibility is neither a goal nor a requirement.
