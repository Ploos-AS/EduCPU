# FPGA M0.15 — Program loader

M0.15 replaces the fixed bring-up-only execution path with a host-loadable EduCPU
machine while keeping the M0.14 ROM self-test available as a qualification mode.

## Goals

- load arbitrary EduCPU machine-code bytes into the 64 KiB SPRAM
- hold the CPU in reset while loading
- start execution deterministically at PC=0 after a successful load
- use a simple transport-independent loader handshake
- keep the board wrapper separate from the architectural CPU core
- preserve the qualified 64 KiB byte-addressable memory semantics
- add a UPduino USB/serial transport after the loader core is qualified

## Loader interface

The board-neutral loader writes bytes through a dedicated memory-loader port:

- `load_mode`: CPU held in reset; loader owns memory
- `load_valid`: one byte request is present
- `load_addr[15:0]`: destination address
- `load_data[7:0]`: byte
- `load_ready`: byte has been accepted
- `run`: release CPU after loading

The first implementation deliberately does not define a serial framing protocol.
That keeps memory ownership and CPU reset semantics testable independently of
FTDI/UART details.

## Qualification gates

1. loader can write bytes into SPRAM while CPU is held reset
2. CPU cannot issue memory transactions during load mode
3. loaded program survives hand-off to CPU
4. PC starts at 0
5. loaded deterministic test program reaches HALT without TRAP
6. existing 20-program RTL/reference differential suite remains PASS
7. UP5K synthesis/place-and-route remains PASS at 12 MHz
8. UPduino bitstream remains buildable

Physical USB/serial loading is a later gate and must not be marked PASS from RTL
simulation alone.

## Qualification status

FPGA CI #119 (commit `5c98ba8`) establishes the loader layers through the byte-protocol boundary:

- board-neutral loader hand-off simulation: PASS
- serial loader protocol parser: PASS
- M0.14 bring-up regression: PASS
- ISA/reference differential suite: 20 programs PASS
- UP5K/UPduino timing regression: PASS at 12 MHz

The next gate is end-to-end serial transport: UART waveform → UART RX → protocol parser → loader mux → SPRAM → CPU execution → HALT. Physical USB/FTDI loading remains unqualified until observed on hardware.
