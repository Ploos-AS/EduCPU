# UPduino v3.1 physical qualification record

This record is the evidence template for the final mandatory EduCPU M9 hardware gate.

Do **not** mark M9 physical bring-up PASS until every required field and test below has been completed on a real UPduino v3.1.

## Test identity

- Date:
- Tester:
- Board: UPduino v3.1
- FPGA: Lattice iCE40UP5K
- Board revision / markings:
- EduCPU commit:
- Bitstream SHA-256:
- Host OS:
- Programmer/tool and version:
- Exact programming command:
- Serial device:
- Serial settings: 115200 8N1
- Loader protocol: v1

## Required procedure

Follow [FPGA_UPDUINO_BRINGUP.md](FPGA_UPDUINO_BRINGUP.md).

Build the canonical loader-v1 image from the recorded commit, program the board, then load and execute the documented `MOVI R0, 42; HALT` qualification program with `tools/eduload.py`.

## Evidence

Expected loader result: `loader ACK`

Expected CPU result: `CPU HALT`

Expected board state: HALT indication, no TRAP indication.

| Cold cycle | Programming | Loader ACK | CPU HALT | No TRAP | Result |
|---|---|---|---|---|---|
| 1 |  |  |  |  |  |
| 2 |  |  |  |  |  |
| 3 |  |  |  |  |  |
| 4 |  |  |  |  |  |
| 5 |  |  |  |  |  |

Console/log evidence:

```text
Paste the complete qualification output here.
```

## Final result

- Cold-cycle result: __ / 5 PASS
- Final qualification: **PENDING**
- Notes:

A final **PASS** requires 5/5 successful cold power-cycle/program/load/run repetitions with ACK, HALT, and no protocol/TRAP error. CI synthesis, simulation, or place-and-route results are supporting evidence but cannot replace this physical test.
