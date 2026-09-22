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

- [x] RTL elaborates
- [ ] lint passes — dedicated lint gate still pending (Yosys `check` passes)
- [x] reset test passes — architectural state initialized and smoke-tested
- [x] NOP/HALT passes — RTL fetch loop and sticky HALT qualified
- [x] arithmetic/logic/flags passes — ADD/SUB/CMP, immediate forms, AND/OR/XOR/NOT and SHL/SHR with ISA v0 Z/N/C/V semantics
- [x] memory passes — absolute, register-indirect and signed SP-relative forms are smoke- and differential-tested
- [x] branches pass — JMP/JZ/JNZ/JC/JNC/JN/JP covered by differential programs
- [x] stack/CALL/RET passes — PUSH/POP, CALL/RET and ENTER/LEAVE covered
- [x] full ISA conformance passes — 20 reference↔RTL differential programs cover every frozen ISA v0 opcode, invalid-opcode and invalid-register traps, architectural state, and full-memory signatures

M0.2 also verifies invalid opcodes enter the architectural trap state and that execution remains stable after HALT/trap.
- [x] synthesis passes for selected target — Yosys + nextpnr iCE40UP5K SG48: 932/5280 logic cells (17%), 20.68 MHz estimated max clock, PASS at 12 MHz; board-neutral core only, external memory not included
- [ ] physical FPGA bring-up passes

The RTL must be checked against the already-qualified reference CPU and emulator. Shared machine-code fixtures should be reused wherever practical.

## License

HDL/gateware uses CERN-OHL-P-2.0 under the EduCPU hardware licensing policy.

## M0.12 explicit UP5K SPRAM qualification

FPGA CI #84 qualifies the physical 64 KiB memory backend on iCE40UP5K.

- complete core + SPRAM machine place-and-route: PASS
- ICESTORM_LC: 981 / 5280 (18%)
- ICESTORM_SPRAM: 2 / 4 (50%)
- SB_IO: 4 / 96 (4%) for the unconstrained machine wrapper
- SB_GB: 5 / 8 (62%)
- timing: 22.59 MHz achieved, PASS at the 12 MHz target
- RTL/reference differential conformance: PASS (20 programs)

The physical backend therefore provides the full 64 KiB EduCPU address space using half of the UP5K SPRAM capacity while preserving the qualified ISA-visible behaviour.

## M0.13 UPduino v3.1 bitstream qualification

FPGA CI #92 qualifies the first concrete development-board target.

- UPduino v3.1 wrapper synthesis/place-and-route: PASS
- explicit 64 KiB SPRAM backend: 2 / 4 blocks (50%)
- logic: 981 / 5280 ICESTORM_LC (18%)
- timing: 21.33 MHz achieved, PASS at the 12 MHz target
- IceStorm bitstream generation: PASS
- output: `educpu_upduino_v31.bin`
- RTL/reference differential conformance: PASS (20 programs)

The remaining board gate is physical execution on an actual UPduino. See `FPGA_UPDUINO_BRINGUP.md`; do not mark physical bring-up PASS from CI alone.


## M0.15 secondary iCEBreaker portability qualification

FPGA CI qualifies the secondary iCEBreaker-class iCE40UP5K wrapper by synthesis alongside the canonical UPduino target.

- board-neutral EduCPU core reuse: PASS
- iCE40UP5K SPRAM backend reuse: PASS
- 12 MHz external-clock wrapper synthesis: PASS
- FPGA CI on commit `9076c7f`: PASS
- no board pin constraints are guessed; physical iCEBreaker qualification requires a verified board revision and official pinout

This target demonstrates that the M9 implementation is not coupled to the UPduino wrapper. UPduino v3.1 remains the canonical physical reference hardware.
