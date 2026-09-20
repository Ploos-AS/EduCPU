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

## Publication and teaching-tool qualification

Final M7 qualification includes the original course-content qualification plus the completed teaching and ebook extensions:

- CI run **#175**: PASS on commit `f547b21e571c30eef26ea4044718df49145b4465`.
- Pages run **#86**: PASS after the bilingual Lesson 03 EduVis integration.
- Ebooks run **#8**: PASS after the same course update.
- The bilingual EPUB workflow generates English and Norwegian editions from the Markdown source, includes deterministic covers and publication metadata, and validates both editions with `epubcheck`.
- Kindle distribution is documented as a release workflow using the validated EPUB as input; Amazon conversion/preview remains a manual release gate.
- `tools/eduguide.py` provides deterministic PREDICT → STEP → OBSERVE → EXPLAIN execution using the reference CPU.
- `tools/eduvis.py` can open course `.eduasm` files directly, creates source/debug mapping, and provides browser instruction/micro-step visualization.
- EduVis reset restores the complete initial memory image; this behavior and direct course-source loading are covered by automated tests.
- Separate English and Norwegian exercise solutions are published outside the lesson bodies.
- The course landing pages point learners onward to EduAVR.

## Deliberately deferred

The following remain optional future improvements and do not block M7:

- additional real screenshots and diagrams derived from the tools;
- further visual polish and accessibility work;
- release-time Kindle preview on Amazon's conversion tooling.

These can evolve without changing the frozen ISA or invalidating the qualified lessons.

## Result

**M7 Guided Teaching Environment: PASS.**

All M7 roadmap requirements are complete: bilingual course content, executable fixtures, guided execution, simulator/visualizer integration, web publication, exercise solutions and bilingual validated EPUB generation. M8 may proceed without carrying an M7 functional blocker.
