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

The software semantics and experimental E0/E1 instruction encodings are now frozen for M10.2 qualification; they remain outside baseline ISA v0.


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


## Frozen software semantics

The M10.2 software I/O contract is now frozen for instruction/RTL design:

- capability: `experimental.io`;
- 256 ports, addressed by an 8-bit port number;
- 8-bit transfer data;
- port space is architecturally separate from the 16-bit memory space;
- unmapped input returns `0x00`;
- unmapped output has no effect;
- input/output do not modify FLAGS;
- device callbacks define device-visible side effects;
- the initial architectural transfer is synchronous and completes as one instruction-level event;
- reset resets CPU state but does not implicitly destroy the machine's attached device topology.

## Experimental instruction proposal

The first instruction form deliberately exposes every operand as a byte:

| Opcode | Instruction | Bytes | Meaning |
|---|---|---:|---|
| E0 | IN rd,port8 | 3 | rd = IO[port8] |
| E1 | OUT port8,rs | 3 | IO[port8] = rs |

These opcodes belong only to an experimental M10 profile. Frozen ISA v0 continues to trap on E0/E1.

The symmetric three-byte encoding is intentionally easy to inspect:

- `E0 02 10` means input port `0x10` into R2;
- `E1 10 02` means output R2 to port `0x10`.

IN and OUT do not alter FLAGS. This keeps the first I/O lesson focused on communication rather than introducing implicit condition-code behavior.

### Architectural trace extension

An experimental I/O instruction trace must expose `io_direction`, `io_port`, `io_value`, and whether the port was mapped. This is the bridge from an instruction the learner can decode by eye to the later RTL bus transaction.


## RTL bus and wait states

The experimental RTL core exposes a bus separate from memory: `io_port[7:0]`, `io_wdata[7:0]`, `io_rdata[7:0]`, `io_we`, `io_valid`, and `io_ready`.

A transfer commits when `io_valid && io_ready`. While a peripheral holds `io_ready=0`, the core keeps the port, direction and output data stable and does not commit an IN result. The memory bus is inactive during the I/O access. This turns the simple synchronous architectural operation into an observable hardware lesson about peripheral latency and handshaking without changing its architectural result.

The reference model's mapped/unmapped status is a device-topology concept. At RTL level the external I/O fabric supplies the corresponding ready/read-data behavior; an unmapped input is represented by read data `0x00`, and an unmapped output is ignored by that fabric.

The conceptual micro-operation plans used by the experimental teaching simulator are explanatory phases, not claims about exact RTL clock cycles.

## M10.2 qualification

M10.2 is CI-qualified across four independent layers:

1. reference-machine semantics and focused tests;
2. independent emulator semantics and software differential tests;
3. integrated RTL wait-state/handshake simulation;
4. RTL/reference differential execution covering mapped IN, mapped OUT and unmapped IN while also checking CPU architectural state.

Baseline ISA v0 continues to trap on E0/E1, and the frozen `fpga/rtl/educpu_core.sv` is unchanged. M10.2 qualification is simulation/reference qualification; it does **not** claim physical UPduino v3.1 qualification.


## Frozen software semantics

The M10.2 software I/O contract is frozen before instruction encoding or RTL work:

- 256 independent 8-bit ports, addressed modulo 256;
- input and output directions may be registered independently;
- unmapped reads return `0x00`;
- unmapped writes have no effect;
- read results and written values are masked to 8 bits;
- device registration belongs to the machine/emulator environment and survives CPU reset;
- software devices are deterministic callbacks and must not implicitly depend on host timing or host I/O.

Reference-machine and independent-emulator implementations are qualified by CI (#576 and #578 respectively). Any later opcode or RTL design must preserve this contract.


## Experimental instruction encoding

The first M10.2 instruction encoding is:

- `IN Rd, port8` = `E0 rd port`: read one byte from the 8-bit port into register `Rd`.
- `OUT port8, Rs` = `E1 port rs`: write register `Rs` to the 8-bit port.

Both instructions are three bytes long. Register operands are 0–7; invalid register operands trap. I/O does not modify arithmetic flags.

Opcodes `0xE0` and `0xE1` belong only to the experimental profile. Frozen ISA v0 continues to treat both as invalid opcodes.

## Experimental RTL bus

The experimental core exposes a separate byte-wide port bus: `io_port[7:0]`, `io_wdata[7:0]`, `io_rdata[7:0]`, `io_we`, `io_valid`, and `io_ready`. A transaction is requested with `io_valid` and completes when `io_ready` is asserted. Memory and I/O remain separate architectural spaces.
