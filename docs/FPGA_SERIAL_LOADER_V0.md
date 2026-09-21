# EduCPU serial loader protocol v0

The first UPduino transport uses the FTDI-to-FPGA serial RX connection and a deliberately tiny binary protocol.

Default line format: **115200 baud, 8 data bits, no parity, 1 stop bit (8N1)**.

A loader session is:

```text
55 AA <length-lo> <length-hi> <program bytes...>
```

- `55 AA`: synchronization marker
- length: unsigned 16-bit little-endian byte count
- payload is written sequentially starting at address `0x0000`
- after the final accepted byte, the loader releases CPU reset and EduCPU starts at `PC=0`
- zero length is invalid
- v0 has no checksum; checksum/CRC and explicit status responses are later hardening gates

The protocol is intentionally independent of EduASM/EduC. Host tooling will compile/assemble first and send the resulting machine-code image.

## Host tool

`tools/eduload.py` constructs protocol-v0 frames and sends a raw EduCPU machine-code image over an 8N1 serial port. It requires Python 3 and pyserial for actual serial I/O.

Example:

```sh
python -m pip install pyserial
python tools/eduload.py program.bin --port /dev/ttyUSB0
```

On Windows, use the assigned COM port, for example `--port COM4`. The default baud rate is 115200.

The host tool intentionally sends raw machine code. Assembly/compiler integration remains upstream: EduASM/EduC produce the image, then `eduload.py` transports it.

## Protocol v1 roadmap: integrity and status

Protocol v0 is intentionally the smallest bring-up transport. The next revision must not silently start a corrupted image.

Proposed v1 frame:

```text
55 AA 01 <length-lo> <length-hi> <payload...> <crc-lo> <crc-hi>
```

The CRC is CRC-16/CCITT-FALSE over `version || length-lo || length-hi || payload` (poly 0x1021, init 0xffff, refin=false, refout=false, xorout=0x0000). The CPU remains in reset until the complete frame and CRC have been accepted.

FPGA-to-host status bytes over TX:

- `0x06` ACK: image accepted and CPU released
- `0x15` NACK: framing, length, or CRC failure; CPU remains in reset
- `0x48` HALT: loaded program reached HALT
- `0x54` TRAP: loaded program trapped

Protocol v0 remains supported for M0.15 physical bring-up. V1 is a separate hardening step so the already-qualified v0 path is not silently changed before physical validation.

### V1 CRC RTL qualification

FPGA CI #132 (commit `8c61d9b`) qualifies the first v1 integrity gate:

- valid CRC frame accepted: PASS
- corrupted CRC frame rejected: PASS
- rejected frame does not release the loader/CPU: PASS
- existing UART-to-CPU v0 end-to-end test: PASS
- existing 20-program ISA differential conformance: PASS

ACK/NACK/HALT/TRAP transmission over UART TX remains the next v1 implementation step.
