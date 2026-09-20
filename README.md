# EduCPU

EduCPU is a pedagogy-first virtual CPU and teaching toolchain. Its purpose is
to make the complete path from bits and machine state to assembly, compilation
and program execution small enough to inspect and understand.

The project deliberately separates the educational architecture from its
implementations. The executable reference CPU defines ISA behaviour; the
simulator and visualizer expose that behaviour for learning; a later emulator
provides faithful machine execution; and the planned FPGA implementation
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
- executable examples and qualification tests;
- EduGuide guided lesson runner for predict → step → observe → explain exercises.

The software path is intentionally inspectable:

`EduC -> AST -> semantic analysis -> EduIR -> EduASM -> object -> linker -> machine code -> EduCPU state`

The hardware-learning path builds upward:

`bits -> logic -> storage -> registers -> ALU -> datapath/control -> CPU -> ISA`

## Status

M0–M6 established and qualified the architecture, assembler/object pipeline,
simulator/debugger, ABI and EduC compiler backend. M7 provides the qualified
bilingual guided course, executable fixtures and EduGuide lesson runner. Later
roadmap milestones include the emulator and FPGA realization.

See [ROADMAP.md](ROADMAP.md) for milestone details.

## Licensing

EduCPU is a mixed software/hardware-design project.

Software, reference models, tools and project documentation default to the **MIT License**.

The EduCPU educational course material defaults to **CC BY 4.0**; executable course source-code examples remain MIT-licensed software unless explicitly stated otherwise.

FPGA/HDL/gateware and any physical hardware design sources default to **CERN-OHL-P-2.0**.

See [docs/LICENSING.md](docs/LICENSING.md) for the repository licence
boundaries and full licence files.
