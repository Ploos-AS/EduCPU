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


## Teaching purpose

The motivating question is: **How can a CPU affect or observe anything that is not ordinary memory?**

The learner should first know LOAD/STORE and memory state. I/O is introduced as a new boundary between CPU state and external devices, not as a list of peripheral APIs.

### Observable model

Every introductory I/O exercise should expose:

- the selected 8-bit port address;
- transfer direction (input or output);
- the byte transferred;
- whether a device is mapped to that port;
- device-visible state before and after the transfer;
- CPU-visible result after an input.

The initial model is synchronous so one transfer has one unambiguous architectural result. Ready/wait states can be introduced later as the problem that motivates bus timing and handshaking.

### Predict → run → inspect

The first exercises should make the learner predict:

1. what an unmapped input returns;
2. whether an unmapped output changes architectural state;
3. which device receives a mapped output;
4. which byte the CPU observes from a mapped input;
5. what happens when addresses or values exceed eight bits.

Only after these semantics are understood should instruction encoding expose I/O to EduCPU programs.

## Why separate port I/O first?

EduCPU deliberately begins with a separate I/O namespace rather than memory-mapped I/O. This makes the conceptual boundary visible: memory stores program/data state while ports represent communication with devices.

Memory-mapped I/O remains an important later comparison experiment. Once both models can be understood, learners can compare their trade-offs instead of being told that one model is simply normal.

## Device progression

The intended teaching progression is:

1. deterministic single-byte teaching device;
2. output latch / LED-like GPIO;
3. input switch / GPIO;
4. UART-like byte stream;
5. timer/status device;
6. optional ready/wait-state bus experiment.

Host terminals and real hardware must be adapters around deterministic device semantics, not the definition of those semantics.
