# M10 experimental RTL integration

The qualified ISA v0 RTL in `educpu_core.sv` remains frozen.

M10 experiments use a separate integration boundary rather than adding
interrupt ports or opcode semantics to that module.

## Components

- `educpu_experimental_irq.sv` owns pending/enabled/in-interrupt control.
- `educpu_experimental_cpu_if.sv` defines the architectural handshake.
- A future experimental CPU implementation will satisfy that interface and may
  implement experimental opcode 0xF0 (IRET).

## IRQ entry handshake

At an instruction boundary, the IRQ controller may pulse `irq_accept` with
`irq_vector`. The experimental CPU must then perform the reference-model
entry semantics before executing another normal instruction:

1. clear HALT if necessary;
2. save current PC;
3. save FLAGS;
4. transfer PC to the accepted vector.

The controller prevents another IRQ from being accepted until IRET completes.

## IRET handshake

Experimental opcode 0xF0 restores FLAGS and PC according to the M10.1
reference model. Once state is restored, the CPU pulses `iret_complete` so
the controller can leave interrupt context and re-enable acceptance.

## Compatibility rule

No signal or behavior in this document is part of frozen ISA v0. Baseline
`educpu_core.sv`, its opcode decoder, and existing M9 FPGA targets remain
unchanged. Experimental RTL must be built and qualified as a separate target.
