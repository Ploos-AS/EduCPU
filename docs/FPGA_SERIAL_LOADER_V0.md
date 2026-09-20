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
