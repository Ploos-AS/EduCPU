"""EduCPU M3 pedagogical simulator/debugger (terminal UI)."""
from __future__ import annotations
import argparse
from pathlib import Path
from educpu import CPU
from edudis import disassemble

FLAG_NAMES=((CPU.Z,"Z"),(CPU.N,"N"),(CPU.C,"C"),(CPU.V,"V"))

def state(cpu):
    return {
        "pc":cpu.pc,"sp":cpu.sp,"flags":cpu.flags,"registers":cpu.r.copy(),
        "halted":cpu.halted,"trap":cpu.trap,
    }

def flags_text(v):
    return " ".join(f"{n}={'1' if v&m else '0'}" for m,n in FLAG_NAMES)

def instruction_at(cpu,pc):
    rows=disassemble(bytes(cpu.mem[pc:pc+4]))
    return rows[0][2] if rows else "?"

def diff(before,after):
    changes=[]
    for i,(a,b) in enumerate(zip(before["registers"],after["registers"])):
        if a!=b: changes.append(f"R{i}: {a:02X}->{b:02X}")
    for k in ("pc","sp","flags"):
        if before[k]!=after[k]:changes.append(f"{k.upper()}: {before[k]:04X}->{after[k]:04X}" if k!="flags" else f"FLAGS: {before[k]:02X}->{after[k]:02X}")
    if before["halted"]!=after["halted"]:changes.append(f"HALT={after['halted']}")
    if before["trap"]!=after["trap"]:changes.append(f"TRAP={after['trap']}")
    return changes

class Simulator:
    def __init__(self,data=b""):
        self.cpu=CPU();self.cpu.mem[:len(data)]=data
        self.breakpoints=set();self.watch=set();self.last=None

    def show(self):
        c=self.cpu
        regs="  ".join(f"R{i}={v:02X}" for i,v in enumerate(c.r))
        print(f"PC={c.pc:04X} SP={c.sp:04X} FLAGS={c.flags:02X} [{flags_text(c.flags)}]")
        print(regs)
        print(f"NEXT: {instruction_at(c,c.pc)}")
        if c.halted:print("STATE: HALTED")
        if c.trap:print(f"STATE: TRAP {c.trap}")

    def step(self):
        c=self.cpu
        if c.halted or c.trap:self.show();return
        pc=c.pc; ins=instruction_at(c,pc); before=state(c)
        watched={a:c.mem[a] for a in self.watch}
        c.step();after=state(c);self.last=(pc,ins,before,after)
        print(f"{pc:04X}: {ins}")
        ch=diff(before,after)
        if ch:print("  "+", ".join(ch))
        for a,old in watched.items():
            if c.mem[a]!=old:print(f"  MEM[{a:04X}]: {old:02X}->{c.mem[a]:02X}")

    def run(self,limit=100000):
        n=0
        while not self.cpu.halted and not self.cpu.trap and n<limit:
            if n and self.cpu.pc in self.breakpoints:
                print(f"breakpoint at {self.cpu.pc:04X}");break
            self.step();n+=1
        if n>=limit:print("step limit reached")

    def memory(self,addr,count=64):
        for off in range(0,count,16):
            a=(addr+off)&0xFFFF
            vals=[self.cpu.mem[(a+i)&0xFFFF] for i in range(min(16,count-off))]
            print(f"{a:04X}: "+" ".join(f"{x:02X}" for x in vals))

    def micro(self):
        c=self.cpu;pc=c.pc;ins=instruction_at(c,pc);op=c.mem[pc]
        print(f"FETCH  address <- PC (0x{pc:04X})")
        print(f"FETCH  opcode <- MEM[0x{pc:04X}] = 0x{op:02X}")
        print(f"DECODE opcode 0x{op:02X} -> {ins}")
        print("READ   operands required by instruction")
        print("EXEC   perform ALU/data/control operation")
        print("WRITE  destination/memory if required")
        print("FLAGS  update only as specified by ISA")
        print("PC     advance or replace for control flow")
        print("Note: this is the pedagogical conceptual sequence, not a frozen hardware microarchitecture.")

def repl(sim):
    print("EduSim M3 — type 'help'")
    sim.show()
    while True:
        try:line=input("(edusim) ").strip()
        except EOFError:break
        if not line:continue
        p=line.split();cmd=p[0].lower()
        try:
            if cmd in ("q","quit","exit"):break
            elif cmd in ("s","step"):sim.step()
            elif cmd in ("r","run"):sim.run(int(p[1],0) if len(p)>1 else 100000)
            elif cmd in ("regs","state"):sim.show()
            elif cmd=="micro":sim.micro()
            elif cmd in ("m","mem"):sim.memory(int(p[1],0),int(p[2],0) if len(p)>2 else 64)
            elif cmd in ("b","break"):
                a=int(p[1],0);sim.breakpoints.add(a);print(f"breakpoint {a:04X}")
            elif cmd=="watch":
                a=int(p[1],0);sim.watch.add(a);print(f"watch {a:04X}")
            elif cmd=="reset":sim.cpu.reset();print("reset");sim.show()
            elif cmd=="help":print("step|s, run|r [limit], state|regs, micro, mem <addr> [count], break <addr>, watch <addr>, reset, quit")
            else:print("unknown command; type help")
        except (ValueError,IndexError) as e:print(f"error: {e}")

def main():
    p=argparse.ArgumentParser(prog="edusim");p.add_argument("binary");a=p.parse_args()
    repl(Simulator(Path(a.binary).read_bytes()))
if __name__=="__main__":main()
