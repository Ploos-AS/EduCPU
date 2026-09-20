# 14 — From EduC to execution

## Learning objectives

Follow one program through the complete EduCPU toolchain and correlate source, IR, assembly, bytes and CPU state.

## One program, all the way down

```c
byte add(byte a, byte b) { return a + b; }
byte main() { byte answer = add(20, 22); return answer; }
```

The complete path is:

```text
EduC → AST → semantic analysis → EduIR → EduASM
→ object + relocations → linker → machine bytes
→ fetch/decode/execute → CPU state
```

At source level we see functions, parameters, a local variable and returns. The AST makes grammatical structure explicit. Semantic analysis verifies names, types, calls and returns. EduIR makes operations and temporary values explicit. Code generation chooses stack slots, registers and ABI mechanisms. The assembler encodes instructions and preserves unresolved addresses as relocations. The linker gives symbols final numeric addresses.

> **How does EduCPU know which source function to call?**
>
> It does not know source functions. By runtime, compiler, assembler and linker have reduced that idea to a CALL opcode followed by a numeric address.

## Execution: bytes become state transitions

The CPU repeatedly fetches the opcode at PC, decodes operands and applies ISA-defined state changes. During this program we can observe PC moving through instructions and CALL/RET, SP moving for return addresses and frames, arguments reaching ABI registers, values moving through stack slots, ADD producing 42, and R0 carrying the final result.

## Compile trace

EduC can produce an `educpu-compile-trace-v0` artifact correlating source, AST, EduIR, generated assembly, machine bytes, symbols and instruction addresses. This is a **compile-time trace**, not a runtime execution trace. In this lesson we combine it with actual step-by-step execution on the reference CPU.

The CI-tested fixture is `course/examples/lesson14-end-to-end.educ`. The test verifies the real compile trace and compiled image, then executes that image and records actual state transitions until the program returns 42 with a balanced stack.

## Run with EduGuide

From the repository root, run the real lesson fixture through the guided runner:

```bash
PYTHONPATH=tools:reference python tools/eduguide.py course/examples/lesson14-end-to-end.educ
```

For each architectural instruction EduGuide prints the current instruction, asks you to **PREDICT**, shows the actual state changes under **OBSERVE**, prints the resulting PC/SP/FLAGS/register state, and asks you to **EXPLAIN** which ISA rule caused it.

To verify only the final result:

```bash
PYTHONPATH=tools:reference python tools/eduguide.py course/examples/lesson14-end-to-end.educ --summary
```

EduGuide uses the same compiler and reference CPU as the qualification tests; it is not a separate teaching-only CPU model.

## Follow one instruction

Pick an instruction from the trace. Record its address, generated assembly and encoded bytes. Predict the opcode, operands, state change and next PC. Run one CPU step and compare.

```text
predict → step → observe → explain
```

## Follow the function call

Find the generated CALL to `add`. Before stepping it, record PC and SP. Afterwards inspect the new PC, new SP and return-address bytes in memory. Continue through `add` and RET and verify that execution resumes after CALL.

This connects an EduC function call to concrete bytes and stack state.

## Exercises

1. At which stage does an EduC call become an IR call, a CALL instruction, and finally a numeric target address?
2. Which representations exist only at build time?
3. Change 20 and 22 to 19 and 23. Predict what changes and what stays structurally the same.
4. Add `byte inc(byte x) { return x + 1; }`, call it, and draw the CALL/RET stack states.

## Check your understanding

Explain every arrow without skipping a layer:

```text
source → AST → semantics → IR → assembly → object
→ relocation/link → bytes → fetch/decode/execute → state
```

For each arrow ask: **what information was added, removed or made more concrete?**

## Next

Next we go below the architectural level: **how can a CPU be built from an ALU, registers, datapath and control logic, and how does that lead toward an FPGA implementation?**
