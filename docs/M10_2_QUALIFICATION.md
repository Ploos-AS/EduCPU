# M10.2 I/O Qualification Record

Status: **PASS — software/reference/RTL simulation qualification**

Physical UPduino v3.1 qualification is outside this record and remains pending hardware.

## Qualified contract

- capability-gated `experimental.io`;
- separate 8-bit port namespace and 8-bit transfers;
- deterministic unmapped input = `0x00`, unmapped output ignored;
- E0 `IN rd,port8` and E1 `OUT port8,rs` in the experimental profile only;
- FLAGS unchanged by IN/OUT;
- observable software I/O transaction state;
- independent emulator implementation;
- separate RTL I/O bus with valid/ready wait-state handshake;
- frozen ISA v0 remains unchanged and traps on E0/E1.

## Evidence

Software/reference tests cover device registration, byte/port masking, mapped/unmapped behavior, reset semantics, IN/OUT execution and baseline rejection.

The independent emulator is differentially checked against the reference model for architectural state and I/O effects.

RTL qualification includes:
- integrated IN/OUT execution;
- peripheral wait states with stable request signals;
- no early IN commit while `io_ready=0`;
- memory bus inactive during an I/O access;
- mapped input/output and deterministic unmapped input;
- differential final CPU state and I/O transaction sequence against the software reference;
- the existing 20-program ISA-v0 experimental-core differential suite;
- M10.1 IRQ/IRET regression qualification.

The original I/O differential gate qualified at FPGA #233: **PASS** and CI #610: **PASS**. Final M10.2 workflow confirmation at commit `0cd3662` is FPGA #239: **PASS**, CI #660: **PASS**, and Validate PLS #6: **PASS**.

## Boundary

This record proves deterministic architectural equivalence in the reference, emulator and simulated RTL models. It does not prove electrical behavior, timing closure on a physical board, peripheral voltage compatibility, or repeated cold-boot behavior. Those belong to physical FPGA qualification.
