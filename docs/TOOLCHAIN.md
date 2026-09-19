# EduCPU Toolchain Architecture

EduCPU tools are teaching instruments.

- **eduasm** — EduASM assembler with symbols, diagnostics and optional source-to-byte teaching traces.
- **edudis** — annotated disassembler.
- **edusim** — deterministic canonical executable CPU/reference model with stepping, snapshots and machine-readable traces.
- **edudbg** — debugger with breakpoints, watchpoints, register/flag/memory/stack views and instruction/micro-operation stepping.
- **educc** — EduC compiler exposing source → tokens → AST → simple IR → EduASM → machine code.

Optimization should initially be absent or minimal so generated code remains understandable.

Long term, opcode metadata should have one machine-readable source of truth usable to check/generate assembler, disassembler, documentation and validation tables. Human-readable ISA semantics remain authoritative.

M0 deliberately does not freeze the host implementation language. M1 should choose it for readability, testing, deterministic behavior, distribution, and suitability for later interactive/browser teaching tools. Host-language convenience must not leak into ISA design.
