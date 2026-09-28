# M10.2 Experimental I/O Architecture

M10.2 explores explicit CPU I/O without changing frozen ISA v0 memory semantics.

## Capability

The feature is gated by `experimental.io`. Baseline ISA v0 has no port-I/O instructions and remains unchanged.

## Model

EduCPU experimental I/O uses a separate 8-bit port namespace:

- port address: 8 bits (0x00–0xFF);
- data width: 8 bits;
- reads and writes are explicit operations, not memory aliases;
- devices own port behavior; the CPU does not prescribe peripherals;
- unimplemented input ports deterministically return 0x00;
- writes to unimplemented ports are ignored;
- operations complete synchronously in the reference model.

The first software interface is intentionally small:

- `in_port(port) -> byte`
- `out_port(port, value)`

A device may register read/write callbacks for one or more ports. This keeps UART, GPIO, timers and teaching devices outside the CPU architecture.

## Qualification order

1. capability-gated reference-machine API;
2. deterministic port/device tests;
3. independent emulator support;
4. freeze software semantics;
5. only then define RTL bus/instructions.

No I/O opcode allocation is frozen at this stage.
