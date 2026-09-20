# UPduino v3.1 hardware bring-up

This procedure qualifies the first physical EduCPU FPGA target.

## Prerequisites

- UPduino v3.x / v3.1 with iCE40UP5K-SG48
- USB connection to the board programmer
- a bitstream produced by the `upduino-v31` CI/build target

The current wrapper uses the iCE40 UltraPlus internal HF oscillator and therefore
does not require the optional external 12 MHz oscillator jumper for first bring-up.

## Build

From `fpga/rtl`:

```sh
make upduino-v31
```

The final file is:

```text
educpu_upduino_v31.bin
```

CI also publishes this file as the `educpu-upduino-v31-bitstream` artifact.

## Programming

Use the programming method supported by the installed UPduino toolchain. Keep
programming separate from the build/qualification gate: CI proves that a valid
bitstream can be generated, while physical-board qualification must be recorded
from a real board.

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

1. the qualified bitstream programs successfully
2. the board starts without the external 12 MHz clock jumper
3. reset/power-up is deterministic
4. the expected test program reaches HALT
5. the RGB LED indicates HALT, not TRAP
6. repeated power cycles give the same result

Record board revision, bitstream commit/SHA, tool/programmer version and the
observed LED state.

## Current boundary

Synthesis, place-and-route and bitstream generation are qualified in CI. Physical
UPduino execution is intentionally not marked PASS until it has been observed on
real hardware.
