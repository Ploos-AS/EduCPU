#!/usr/bin/env python3
"""Generate deterministic EduCPU ISA v0 conformance vectors from the reference CPU."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from reference.educpu import CPU

CASES={
 "nop_halt": bytes([0x00,0x01]),
 "mov_alu": bytes([0x11,0,0x7f,0x21,0,1,0x23,0,0x80,0x01]),
 "logic_shift": bytes([0x11,0,0x80,0x2c,0,0x2d,0,0x01]),
 "branch": bytes([0x11,0,0,0x25,0,0,0x31,10,0,0xff,0x01]),
 "stack": bytes([0x11,0,0x5a,0x40,0,0x41,1,0x01]),
 "call_ret": bytes([0x38,8,0,0x01,0,0,0,0,0x11,2,0x33,0x39]),
}

def run(name,program):
 c=CPU(); c.mem[:len(program)]=program; c.run(100)
 regs=" ".join(f"{x:02x}" for x in c.r)
 trap=0 if c.trap is None else 1
 return f"{name} pc={c.pc:04x} sp={c.sp:04x} flags={c.flags:02x} halted={int(c.halted)} trap={trap} regs={regs}"

if __name__=="__main__":
 for name,program in CASES.items(): print(run(name,program))
