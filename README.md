# EduCPU

EduCPU is a pedagogy-first virtual CPU and teaching toolchain. Its purpose is
to make the complete path from bits and machine state to assembly, compilation
and program execution small enough to inspect and understand.

The project deliberately separates the educational architecture from its
implementations. The executable reference CPU defines ISA behaviour; the
simulator and visualizer expose that behaviour for learning; the independent
emulator provides faithful machine execution; and the FPGA implementation
realizes the architecture in hardware.

## Learning path

The guided course is bilingual (English/Norwegian), uses Markdown as its
single source of truth and is published as generated HTML through GitHub
Pages. Start in [course/](course/README.md).

The recurring question is: **How does EduCPU know?** The course removes
abstractions layer by layer rather than treating the CPU, assembler or
compiler as magic.

## Toolchain

The repository includes:

- the EduCPU ISA v0 reference model;
- EduASM assembler and disassembler;
- EduLink object linker;
- EduSim and the conceptual micro-step model;
- EduVis browser visualization;
- EduC front end, semantic analysis, EduIR and compiler backend;
- an independent EduCPU emulator;
- synthesizable FPGA/RTL implementation and qualification;
- executable examples and qualification tests;
- EduGuide guided lesson runner for predict → step → observe → explain exercises.

The software path is intentionally inspectable:

`EduC -> AST -> semantic analysis -> EduIR -> EduASM -> object -> linker -> machine code -> EduCPU state`

The hardware-learning path builds upward:

`bits -> logic -> storage -> registers -> ALU -> datapath/control -> CPU -> ISA`

## Reference hardware

**UPduino v3.1 (Lattice iCE40UP5K) is the canonical EduCPU FPGA hardware target.**

EduCPU does not require physical hardware: the simulator and emulator remain
fully supported teaching and development environments. UPduino v3.1 is the
primary supported board for physical FPGA qualification, examples, pin
assignments, bitstreams and UART-based workflows.

Additional compatible FPGA development boards may be supported as secondary
targets. A dedicated EduCPU PCB is an optional future goal, not a requirement
for EduCPU completion or releases.

## Status

M0–M7 established and qualified the architecture, assembler/object pipeline,
simulator/debugger, ABI, EduC compiler backend and bilingual guided course.
M8 provides the independently implemented and qualified emulator. M9 is the
FPGA realization and physical UPduino v3.1 qualification.

See [ROADMAP.md](ROADMAP.md) for milestone details.

## Licensing

EduCPU is a mixed software/hardware-design project.

Software, reference models, tools and project documentation default to the **MIT License**.

The EduCPU educational course material defaults to **CC BY 4.0**; executable course source-code examples remain MIT-licensed software unless explicitly stated otherwise.

FPGA/HDL/gateware and any physical hardware design sources default to **CERN-OHL-P-2.0**.

See [docs/LICENSING.md](docs/LICENSING.md) for the repository licence
boundaries and full licence files.
