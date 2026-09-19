# EduVis — graphical datapath teaching view

EduVis is the graphical layer of the M3 pedagogical simulator. It runs locally in a browser using only the Python standard library.

It visualizes the **teaching datapath**, not a promise about the future FPGA's gates or clock cycles.

## Run

```sh
python tools/eduasm.py examples/sum.eduasm -o sum.bin -g
PYTHONPATH=reference:tools python tools/eduvis.py sum.bin
```

Open the local address printed by EduVis.

The page shows PC, memory, decode/IR, R0-R7, ALU, FLAGS, SP, current instruction, correlated EduASM source and current conceptual micro-step. During micro-stepping the participating datapath components are highlighted.

EduVis consumes the same reference CPU, disassembler, source metadata and MicroStepper as terminal EduSim. It does not implement a second CPU.

```text
EduASM source
    ↓
machine bytes
    ↓
reference CPU
    ↓
pedagogical micro-step model
    ↓
EduSim / EduVis
```

A later FPGA-specific view can visualize the concrete RTL microarchitecture once that architecture exists.
