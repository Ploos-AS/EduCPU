# M10 experimental extension policy

EduCPU M10 explores advanced CPU concepts without destabilizing the qualified ISA v0 teaching platform.

## Baseline rule

ISA v0 is frozen. The default reference CPU, assembler, compiler, emulator, simulator and FPGA profile must continue to implement the qualified ISA v0 behaviour.

An M10 experiment must never silently change baseline instruction semantics, register behaviour, flags, memory behaviour, traps, ABI behaviour or machine-code interpretation.

## Opt-in experiments

Experimental features are disabled by default and selected explicitly through a named machine/profile or capability flag.

A program requiring an experiment must be able to declare that requirement. Baseline tools must reject unsupported experimental requirements rather than reinterpret them.

Experimental opcode space, if introduced, must be isolated from ISA v0 and documented before implementation.

## Capability discovery

Each experimental machine profile exposes a stable set of symbolic capabilities. Capabilities describe mechanisms, not implementation accidents. Initial naming uses the `experimental.*` namespace.

Examples:

- `experimental.interrupts`
- `experimental.io`
- `experimental.microcode`
- `experimental.privilege`
- `experimental.vm`
- `experimental.pipeline`
- `experimental.cache`

No capability is implied by another unless the architecture document explicitly says so.

## Qualification gates

Every experiment must include:

1. baseline ISA v0 regression tests;
2. tests with the feature disabled;
3. focused tests with the feature enabled;
4. documentation of architectural state and observable behaviour;
5. reference-model behaviour before emulator/RTL qualification is claimed.

The normal CI baseline must remain green. Experimental failures must not be hidden by weakening ISA v0 tests.

## Lifecycle

An experiment has one of four states:

- **proposal** — architecture/design only;
- **experimental** — implemented behind explicit opt-in;
- **graduated** — retained as a documented optional extension after qualification;
- **removed** — deleted without compatibility promises beyond documented experimental releases.

Graduation does not modify ISA v0. A future base ISA revision requires its own explicit architecture/versioning process.

### Graduation gate

An experiment may become a graduated optional extension only when its architecture is frozen and documented, reference-model tests are complete, baseline ISA v0 regression remains green, supported emulator/simulator implementations agree with the reference model, tooling requirements are explicit, and any claimed FPGA support has its own qualification evidence. Graduation requires an explicit roadmap/release change; implementation alone is not graduation.

### Removal gate

Proposal-stage features may be removed freely. Experimental features may be removed after their capability/profile is deleted, tests and documentation are updated, and release notes identify the removal. Removed experimental machine-code compatibility is not promised. A removed experiment must never cause its old encodings to acquire different silent meanings in the ISA v0 baseline.

### Compatibility rule

Graduated extensions remain optional and capability-gated. Software that requires one must declare it; software targeting ISA v0 must not acquire an extension dependency implicitly.

## Teaching principle

Experiments exist to expose concepts such as interrupts, privilege, pipelines and caches. Implementations should favor observability and understandable state transitions over performance or complexity.

## Hardware

M10 work may be simulated and synthesized without physical FPGA hardware. Physical qualification is tracked separately. The pending M9 UPduino v3.1 hardware gate therefore does not block M10 experiments.
