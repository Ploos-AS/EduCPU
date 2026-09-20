# EduCPU FPGA M0

## Goal

Create the first synthesizable RTL realization of frozen EduCPU ISA v0. The FPGA core is board-neutral at M0.

## Conceptual architecture

```text
instruction memory -> fetch/decode/control -> register file <-> ALU
                                      |             |
                                      +-- PC/SP/FLAGS
                                      |
                                 data memory
```

## Implementation order

1. module boundaries
2.1 M0.1 reset and architectural-state skeleton (8-bit R0-R7, 16-bit PC/SP, 8-bit FLAGS)
2. clock/reset
3. register file and architectural state
4. instruction fetch
5. decode
6. ALU and FLAGS
7. memory operations
8. branches
9. stack/CALL/RET/ENTER/LEAVE
10. HALT and invalid-opcode traps

## Qualification gates

- [ ] RTL elaborates
- [ ] lint passes
- [x] reset test passes — architectural state initialized and smoke-tested
- [x] NOP/HALT passes — RTL fetch loop and sticky HALT qualified
- [ ] arithmetic/logic/flags passes
- [ ] memory passes
- [ ] branches pass
- [ ] stack/CALL/RET passes
- [ ] full ISA conformance passes

M0.2 also verifies invalid opcodes enter the architectural trap state and that execution remains stable after HALT/trap.
- [ ] synthesis passes for selected target
- [ ] physical FPGA bring-up passes

The RTL must be checked against the already-qualified reference CPU and emulator. Shared machine-code fixtures should be reused wherever practical.

## License

HDL/gateware uses CERN-OHL-P-2.0 under the EduCPU hardware licensing policy.
