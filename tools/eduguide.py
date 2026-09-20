"""Guided EduCPU lesson runner.

Runs EduASM or EduC lesson examples against the real reference CPU and emits
small, deterministic state transitions for the predict -> step -> observe ->
explain teaching loop.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from educpu import CPU
from eduasm import assemble_text
from educ import compile_source
from edudis import disassemble
from edusim import state, diff, flags_text

def decode_at(cpu, pc):
    rows = disassemble(bytes(cpu.mem[pc:pc+4]))
    return rows[0][2] if rows else "?"

def prepare(path):
    text = path.read_text()
    if path.suffix == ".eduasm":
        data, symbols, _ = assemble_text(text)
        return data, symbols, 0, None
    if path.suffix == ".educ":
        _, _, _, _, data, symbols = compile_source(text, str(path))
        if "main" not in symbols:
            raise ValueError("EduC guided examples require an exported main function")
        halt = len(data)
        if halt >= 0xFEFE:
            raise ValueError("program is too large for guided runner return setup")
        return data, symbols, symbols["main"], halt
    raise ValueError("guided runner accepts .eduasm or .educ files")

def create_cpu(path):
    data, symbols, entry, synthetic_halt = prepare(path)
    cpu = CPU()
    cpu.mem[:len(data)] = data
    cpu.pc = entry
    if synthetic_halt is not None:
        cpu.mem[synthetic_halt] = 0x01
        cpu.sp -= 1
        cpu.mem[cpu.sp] = (synthetic_halt >> 8) & 0xFF
        cpu.sp -= 1
        cpu.mem[cpu.sp] = synthetic_halt & 0xFF
    return cpu, symbols

def guided_steps(path, limit=1000):
    cpu, symbols = create_cpu(path)
    steps = []
    n = 0
    while not cpu.halted and cpu.trap is None and n < limit:
        pc = cpu.pc
        ins = decode_at(cpu, pc)
        before = state(cpu)
        cpu.step()
        after = state(cpu)
        steps.append({"number": n + 1, "pc": pc, "instruction": ins,
                      "before": before, "after": after,
                      "changes": diff(before, after)})
        n += 1
    if n >= limit and not cpu.halted and cpu.trap is None:
        raise RuntimeError("guided runner step limit reached")
    return cpu, symbols, steps

def print_step(item):
    before, after = item["before"], item["after"]
    print(f"STEP {item['number']:02d}  PC={item['pc']:04X}  {item['instruction']}")
    print("  PREDICT  What will change?")
    print("  OBSERVE  " + (", ".join(item["changes"]) if item["changes"] else "no architectural state change"))
    print(f"  STATE    PC={after['pc']:04X} SP={after['sp']:04X} FLAGS={after['flags']:02X} [{flags_text(after['flags'])}]")
    print("           " + " ".join(f"R{i}={v:02X}" for i, v in enumerate(after["registers"])))
    print("  EXPLAIN  Which ISA rule caused the observed change?")

def main():
    p = argparse.ArgumentParser(prog="eduguide")
    p.add_argument("source", type=Path)
    p.add_argument("--limit", type=int, default=1000)
    p.add_argument("--summary", action="store_true", help="show only final state")
    a = p.parse_args()
    cpu, symbols, steps = guided_steps(a.source, a.limit)
    if not a.summary:
        for item in steps:
            print_step(item)
            print()
    print(f"FINAL steps={len(steps)} PC={cpu.pc:04X} SP={cpu.sp:04X} halted={cpu.halted} trap={cpu.trap}")
    print("      " + " ".join(f"R{i}={v:02X}" for i, v in enumerate(cpu.r)))
    if symbols:
        print("SYMBOLS " + " ".join(f"{k}={v:04X}" for k, v in sorted(symbols.items())))

if __name__ == "__main__":
    main()
