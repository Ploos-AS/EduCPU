"""EduCPU M3 pedagogical simulator/debugger."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from educpu import CPU
from edudis import disassemble
from microcode import MicroStepper,plan
FLAG_NAMES=((CPU.Z,"Z"),(CPU.N,"N"),(CPU.C,"C"),(CPU.V,"V"))
def state(cpu):return {"pc":cpu.pc,"sp":cpu.sp,"flags":cpu.flags,"registers":cpu.r.copy(),"halted":cpu.halted,"trap":cpu.trap}
def flags_text(v):return " ".join(f"{n}={'1' if v&m else '0'}" for m,n in FLAG_NAMES)
def instruction_at(cpu,pc):
 rows=disassemble(bytes(cpu.mem[pc:pc+4]));return rows[0][2] if rows else "?"
def diff(before,after):
 changes=[]
 for i,(a,b) in enumerate(zip(before["registers"],after["registers"])):
  if a!=b:changes.append(f"R{i}: {a:02X}->{b:02X}")
 for k in ("pc","sp","flags"):
  if before[k]!=after[k]:changes.append(f"{k.upper()}: {before[k]:04X}->{after[k]:04X}" if k!="flags" else f"FLAGS: {before[k]:02X}->{after[k]:02X}")
 if before["halted"]!=after["halted"]:changes.append(f"HALT={after['halted']}")
 if before["trap"]!=after["trap"]:changes.append(f"TRAP={after['trap']}")
 return changes
class Simulator:
 def __init__(self,data=b"",debug=None):
  self.cpu=CPU();self.cpu.mem[:len(data)]=data;self.breakpoints=set();self.watch=set();self.last=None;self.microstepper=MicroStepper(self.cpu)
  self.debug=debug or {};self.source_by_addr={x["address"]:x for x in self.debug.get("instructions",[])}
 def source(self,pc=None):
  pc=self.cpu.pc if pc is None else pc;row=self.source_by_addr.get(pc)
  if row:print(f"SOURCE {self.debug.get('source') or '<source>'}:{row['line']}: {row['source'].strip()}")
  else:print(f"SOURCE no mapping for 0x{pc:04X}")
  return row
 def show(self):
  c=self.cpu;regs="  ".join(f"R{i}={v:02X}" for i,v in enumerate(c.r))
  print(f"PC={c.pc:04X} SP={c.sp:04X} FLAGS={c.flags:02X} [{flags_text(c.flags)}]");print(regs);print(f"NEXT: {instruction_at(c,c.pc)}")
  if c.pc in self.source_by_addr:self.source(c.pc)
  if c.halted:print("STATE: HALTED")
  if c.trap:print(f"STATE: TRAP {c.trap}")
 def step(self):
  self.microstepper.cancel();c=self.cpu
  if c.halted or c.trap:self.show();return
  pc=c.pc;ins=instruction_at(c,pc);before=state(c);watched={a:c.mem[a] for a in self.watch}
  if pc in self.source_by_addr:self.source(pc)
  c.step();after=state(c);self.last=(pc,ins,before,after);print(f"{pc:04X}: {ins}");ch=diff(before,after)
  if ch:print("  "+", ".join(ch))
  for a,old in watched.items():
   if c.mem[a]!=old:print(f"  MEM[{a:04X}]: {old:02X}->{c.mem[a]:02X}")
 def microstep(self):
  before=state(self.cpu)
  if not self.microstepper.active and self.cpu.pc in self.source_by_addr:self.source(self.cpu.pc)
  step,committed=self.microstepper.next()
  if step is None:self.show();return
  print(f"{step.phase:<12} {step.text}")
  if committed:
   after=state(self.cpu);ch=diff(before,after);print("COMMIT       architectural instruction completed")
   if ch:print("  "+", ".join(ch))
 def micro(self):
  if self.cpu.pc in self.source_by_addr:self.source(self.cpu.pc)
  for s in plan(self.cpu):print(f"{s.phase:<12} {s.text}")
  print("Use 'microstep'/'ms' to advance one conceptual phase at a time.")
 def run(self,limit=100000):
  self.microstepper.cancel();n=0
  while not self.cpu.halted and not self.cpu.trap and n<limit:
   if n and self.cpu.pc in self.breakpoints:print(f"breakpoint at {self.cpu.pc:04X}");break
   self.step();n+=1
  if n>=limit:print("step limit reached")
 def memory(self,addr,count=64):
  for off in range(0,count,16):
   a=(addr+off)&0xFFFF;vals=[self.cpu.mem[(a+i)&0xFFFF] for i in range(min(16,count-off))]
   print(f"{a:04X}: "+" ".join(f"{x:02X}" for x in vals))
def repl(sim):
 print("EduSim M3 — type 'help'");sim.show()
 while True:
  try:line=input("(edusim) ").strip()
  except EOFError:break
  if not line:continue
  p=line.split();cmd=p[0].lower()
  try:
   if cmd in ("q","quit","exit"):break
   elif cmd in ("s","step"):sim.step()
   elif cmd in ("ms","microstep"):sim.microstep()
   elif cmd in ("r","run"):sim.run(int(p[1],0) if len(p)>1 else 100000)
   elif cmd in ("regs","state"):sim.show()
   elif cmd=="source":sim.source()
   elif cmd=="micro":sim.micro()
   elif cmd in ("m","mem"):sim.memory(int(p[1],0),int(p[2],0) if len(p)>2 else 64)
   elif cmd in ("b","break"):a=int(p[1],0);sim.breakpoints.add(a);print(f"breakpoint {a:04X}")
   elif cmd=="watch":a=int(p[1],0);sim.watch.add(a);print(f"watch {a:04X}")
   elif cmd=="reset":sim.microstepper.cancel();sim.cpu.reset();print("reset");sim.show()
   elif cmd=="help":print("step|s, microstep|ms, micro, run|r [limit], state|regs, source, mem <addr> [count], break <addr>, watch <addr>, reset, quit")
   else:print("unknown command; type help")
  except (ValueError,IndexError) as e:print(f"error: {e}")
def main():
 p=argparse.ArgumentParser(prog="edusim");p.add_argument("binary");p.add_argument("-g","--debug-map");a=p.parse_args();bp=Path(a.binary)
 dbg_path=Path(a.debug_map) if a.debug_map else bp.with_suffix(bp.suffix+".dbg.json");dbg=json.loads(dbg_path.read_text()) if dbg_path.exists() else None
 repl(Simulator(bp.read_bytes(),dbg))
if __name__=="__main__":main()
