# M7 Qualification — Guided Teaching Environment

## Scope

M7 turns the qualified EduCPU architecture and compiler toolchain into a bilingual, executable teaching course.

## Qualified course surface

- 15 English lessons and 15 parallel Norwegian lessons.
- Markdown is the single source of truth.
- MkDocs generates the published GitHub Pages site.
- The course progresses from bits and logic through CPU state, ISA, EduASM, stack/ABI, compiler construction, linking, complete execution and hardware realization.
- The recurring question “How does EduCPU know?” / “Hvordan vet EduCPU det?” is used to expose the mechanism below each abstraction.
- Course content is licensed CC BY 4.0; software remains MIT; future hardware/HDL is covered separately by CERN-OHL-P-2.0.

## Executable qualification

Course fixtures are exercised by the repository test suite rather than being documentation-only examples.

The tested path includes:

- number representation and basic instructions;
- logic operations;
- machine state and flags;
- instruction encoding and little-endian addresses;
- labels and assembly;
- arithmetic and branches;
- stack behaviour;
- CALL/RET and ABI behaviour;
- EduC compilation;
- AST and semantic analysis;
- EduIR and code generation;
- independent objects, imports/exports and relocations;
- linking and patched CALL targets;
- complete EduC compile trace;
- actual reference-CPU state transitions and final execution.

Lesson 14 explicitly distinguishes compile-time correlation from runtime execution tracing.

## Publication qualification

GitHub Actions at the completion of lessons 01–15:

- CI run **#138**: PASS on commit `a7334f423d61c434133b77cbcf93cba8ad459294`.
- Pages run **#70**: PASS on the same commit.

Both the test suite and generated course site therefore passed before the final M7 documentation cleanup.

## Deliberately deferred

The following are useful extensions but are not required for the course-content qualification:

- a dedicated interactive guided runner;
- deeper one-click simulator/visualizer launch integration;
- separate exercise solution material;
- additional real screenshots and diagrams from the tools.

These can evolve without changing the frozen ISA or invalidating the qualified lessons.

## Result

**M7 course content and publication pipeline: PASS.**

The remaining interactive teaching-environment enhancements are tracked as follow-on work rather than blockers for the 15-lesson course.
