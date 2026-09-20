#!/usr/bin/env python3
"""Build one linear Markdown manuscript per EduCPU course language.

Pandoc consumes these generated manuscripts to create EPUB. The Markdown course
remains the single source of truth.
"""
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "course"

LESSONS = {
    "en": [
        "01-bits-bytes-hex.md","02-logic-and-storage.md","03-what-is-a-cpu.md",
        "04-machine-state.md","05-instructions-machine-code.md","06-eduasm.md",
        "07-arithmetic-flags-branches.md","08-stack.md","09-functions-call-ret-abi.md",
        "10-what-is-a-compiler.md","11-educ-ast-semantics.md","12-eduir-codegen.md",
        "13-objects-relocations-linking.md","14-educ-to-execution.md",
        "15-how-a-cpu-is-built.md",
    ],
    "no": [
        "01-bits-bytes-hex.md","02-logikk-og-lagring.md","03-hva-er-en-cpu.md",
        "04-maskintilstand.md","05-instruksjoner-maskinkode.md","06-eduasm.md",
        "07-aritmetikk-flags-hopp.md","08-stacken.md","09-funksjoner-call-ret-abi.md",
        "10-hva-er-en-compiler.md","11-educ-ast-semantikk.md","12-eduir-kodegenerering.md",
        "13-objektfiler-relocations-linking.md","14-educ-til-kjoring.md",
        "15-hvordan-en-cpu-bygges.md",
    ],
}

def build(language: str) -> str:
    index = COURSE / language / "index.md"
    solutions = COURSE / language / ("solutions.md" if language == "en" else "losninger.md")
    paths = [index] + [COURSE / language / "lessons" / name for name in LESSONS[language]] + [solutions]
    missing = [str(p.relative_to(ROOT)) for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError("missing ebook sources: " + ", ".join(missing))
    return "\n\n\\newpage\n\n".join(p.read_text().rstrip() for p in paths) + "\n"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("language", choices=sorted(LESSONS))
    p.add_argument("output", type=Path)
    a=p.parse_args()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(build(a.language))

if __name__ == "__main__":
    main()
