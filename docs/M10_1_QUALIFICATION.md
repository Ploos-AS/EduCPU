# M10.1 Interrupt Qualification

Status: **RTL architecture qualified in CI; experimental CPU integration remains open**

M10.1 is an opt-in experiment. It does not change the frozen ISA v0 CPU, opcode map, assembler, emulator baseline, or M9 FPGA targets.

## Qualified software semantics

The experimental reference machine and independent emulator cover:

- IRQ acceptance only at an instruction boundary;
- pending IRQ state and disabled acceptance;
- HALT wake-up;
- trapped-CPU rejection;
- single-level interrupt context;
- deferred nested requests;
- CALL-compatible PC save plus FLAGS save;
- experimental `IRET` opcode `0xF0`;
- restoration of PC, FLAGS, SP and interrupt-enable state;
- baseline ISA v0 continuing to trap on `0xF0`.

These behaviors are exercised by the Python regression suite, including
`tests/test_machine_profiles.py` and `tests/test_experimental_emulator.py`.

## Qualified RTL boundary

The RTL experiment is deliberately separate from `educpu_core.sv`.

`educpu_experimental_irq.sv` qualifies the control boundary:

- pending request capture and coalescing;
- instruction-boundary acceptance;
- trap rejection;
- nested-request deferral;
- vector capture;
- re-enable after IRET completion.

`educpu_experimental_irq_entry.sv` qualifies the architectural stack sequencer:

- PC high byte, PC low byte and FLAGS are pushed in the documented order;
- SP changes from the supplied CPU state to the interrupt frame;
- control transfers to the accepted vector;
- IRET pops FLAGS and PC and restores SP;
- memory operations use an explicit valid/ready handshake.

Both RTL tests run in the FPGA GitHub Actions workflow.

## Compatibility gate

The qualified ISA v0 RTL remains `fpga/rtl/educpu_core.sv`. M10.1 does not add ports or opcode semantics to that module. The existing ISA-v0 RTL/reference differential suite remains the regression gate for the frozen baseline.

## Remaining M10.1 gate

M10.1 is **not yet marked complete**. The remaining engineering gate is a complete experimental CPU integration target that joins the IRQ controller and entry/IRET sequencer to an execution core and then cross-checks architectural IRQ results against the software model.

Physical UPduino v3.1 bring-up is an independent M9 hardware gate and does not block this experimental work.
