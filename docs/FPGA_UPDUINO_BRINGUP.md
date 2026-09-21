# UPduino v3.1 hardware bring-up

This procedure qualifies the first physical EduCPU FPGA target.

## Prerequisites

- UPduino v3.x / v3.1 with iCE40UP5K-SG48
- USB connection to the board programmer
- a bitstream produced by the `upduino-v31-loader-v1` CI/build target
- Python 3 with `pyserial`
- the EduCPU checkout on the same commit as the bitstream

The current wrapper uses the iCE40 UltraPlus internal HF oscillator and therefore
does not require the optional external 12 MHz oscillator jumper for first bring-up.

## Build

From `fpga/rtl`:

```sh
make upduino-v31-loader-v1
```

The canonical physical-qualification bitstream is:

```text
educpu_upduino_v31_loader_v1.bin
```

The simpler `make upduino-v31` bring-up image remains useful for the LED-only smoke test, but protocol-v1 is the canonical qualification path because it exercises host → UART → loader → memory → CPU → UART → host.

## Programming

Program `educpu_upduino_v31_loader_v1.bin` with the UPduino-supported programmer/toolchain. Record the exact programming command and tool version in the qualification record. Programming remains separate from CI: CI proves the bitstream can be generated, while hardware qualification proves that the generated image works on a real board.

## Canonical load → run → readback test

Install the host dependency:

```sh
python -m pip install pyserial
```

Create a minimal HALT program, for example `/tmp/educpu-hw.eduasm`:

```text
MOVI R0, 42
HALT
```

Find the UPduino serial port after programming, then run from the repository root:

```sh
PYTHONPATH=reference python tools/eduload.py /tmp/educpu-hw.eduasm \
  --port /dev/ttyUSB0 --baud 115200 --protocol v1
```

Use the actual device name on the host (for example `/dev/ttyUSB0`, `/dev/ttyACM0` or a Windows `COMn` port).

A successful protocol-v1 transaction must print both:

```text
loader ACK
CPU HALT
```

This is the canonical end-to-end hardware gate. It verifies the host frame, UART receive, CRC/protocol acceptance, SPRAM loading, CPU execution and UART status return. A NACK, timeout, TRAP or unexpected status is a qualification failure and must not be recorded as PASS.

## Status LEDs

The on-board RGB LED is active-low electrically; the board wrapper owns that
polarity conversion.

Bring-up semantics:

- green: EduCPU is running
- blue: EduCPU reached HALT
- red: EduCPU trapped

## Physical qualification

A physical qualification is PASS only when all of the following are observed and
recorded:

1. the protocol-v1 qualified bitstream programs successfully
2. the board starts without the external 12 MHz clock jumper
3. reset/power-up is deterministic
4. `eduload.py --protocol v1` receives loader ACK
5. the uploaded test program reaches HALT and the host receives `CPU HALT`
6. no NACK, TRAP or unexpected status is observed
7. the RGB LED indicates HALT, not TRAP
8. at least five cold power-cycle/load/run repetitions give the same result

Record board revision, bitstream commit/SHA, tool/programmer version and the
observed LED state.

## Current boundary

Synthesis, place-and-route and bitstream generation are qualified in CI. Physical
UPduino execution is intentionally not marked PASS until it has been observed on
real hardware.

## M0.14 simulated bring-up gate

FPGA CI #105 validates the exact power-on bring-up program before physical testing:

- boot ROM execution: PASS (`EduCPU UPduino bring-up program PASS`)
- expected path: MOVI → MOVI → CMP → JNZ(not taken) → HALT
- UPduino bitstream synthesis/place-and-route: PASS
- logic: 1061 / 5280 ICESTORM_LC (20%)
- SPRAM: 2 / 4 blocks (50%)
- timing: 20.61 MHz achieved, PASS at 12 MHz
- bitstream artifact: PASS
- full RTL/reference differential suite: 20 programs PASS

This closes the simulated/bitstream portion of M0.14. The physical-board gate remains open until the same bitstream is programmed and observed on an actual UPduino.


## Qualification record template

Record the following in the eventual M9 physical qualification document:

| Field | Value |
| --- | --- |
| Board | UPduino v3.1 |
| FPGA | Lattice iCE40UP5K-SG48 |
| EduCPU commit | `<git SHA>` |
| Bitstream | `educpu_upduino_v31_loader_v1.bin` |
| Programmer/tool version | `<version>` |
| Host OS | `<OS/version>` |
| Serial device | `<device>` |
| Baud/protocol | 115200 8N1 / v1 |
| Loader result | ACK / FAIL |
| CPU result | HALT / TRAP / timeout |
| Cold-cycle repetitions | 5/5 required |
| Final result | PASS / FAIL |
