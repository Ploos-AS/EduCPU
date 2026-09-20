#!/usr/bin/env python3
"""Run deterministic programs through reference CPU and RTL, compare architectural state."""
from pathlib import Path
import subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from reference.educpu import CPU
from fpga.conformance.reference_vectors import CASES

def memhash(mem):
 h=0x811c9dc5
 for b in mem:
  h=((h ^ b) * 0x01000193) & 0xffffffff
 return h

def ref(program):
 c=CPU(); c.mem[:len(program)]=program; c.run(1000)
 return (c.pc,c.sp,c.flags,int(c.halted),int(c.trap is not None),tuple(c.r),memhash(c.mem))

def rtl(program,sim):
 with tempfile.NamedTemporaryFile("w",suffix=".hex",delete=False) as f:
  f.write("\n".join(f"{b:02x}" for b in program)+"\n"); name=f.name
 try:
  lines=subprocess.check_output(["vvp",str(sim),f"+IMAGE={name}"],text=True).strip().splitlines()
  out=next((line for line in reversed(lines) if line.startswith("pc=")), None)
  if out is None:
    raise RuntimeError("RTL harness produced no architectural-state line: "+repr(lines))
 finally: Path(name).unlink(missing_ok=True)
 fields=out.split(" regs="); h=dict(x.split("=") for x in fields[0].split())
 regpart,hashpart=fields[1].split(" memhash=")
 regs=tuple(int(x,16) for x in regpart.split())
 return (int(h["pc"],16),int(h["sp"],16),int(h["flags"],16),int(h["halted"]),int(h["trap"]),regs,int(hashpart,16))

def main():
 sim=ROOT/"fpga/conformance/diff_simv"
 subprocess.run(["iverilog","-g2012","-o",str(sim),str(ROOT/"fpga/rtl/educpu_core.sv"),str(ROOT/"fpga/conformance/tb_differential.sv")],check=True)
 try:
  for name,program in CASES.items():
   a,b=ref(program),rtl(program,sim)
   if a!=b:
    print(f"FAIL {name}\n reference={a}\n rtl={b}"); return 1
   print(f"PASS {name}")
 finally: sim.unlink(missing_ok=True)
 print(f"EduCPU FPGA differential conformance PASS ({len(CASES)} programs)")
 return 0
if __name__=="__main__": raise SystemExit(main())
