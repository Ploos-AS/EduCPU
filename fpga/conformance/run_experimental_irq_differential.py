#!/usr/bin/env python3
"""Compare experimental IRQ architectural result between reference machine and RTL."""
from pathlib import Path
import subprocess,sys,re
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"reference"))
from machine import experimental_machine

def reference():
 m=experimental_machine(); c=m.cpu
 c.mem[0:2]=bytes([0x00,0x01]); c.mem[0x8000]=0xf0
 c.step(); m.irq_vector=0x8000; m.request_irq(); m.run(30)
 return (c.pc,c.sp,c.flags,int(c.halted),int(c.trap is not None),tuple(c.mem[x] for x in (0xfeff,0xfefe,0xfefd)))

def rtl():
 sim=ROOT/"fpga/conformance/experimental_irq_diff_simv"
 subprocess.run(["iverilog","-g2012","-o",str(sim),str(ROOT/"fpga/rtl/educpu_experimental_core.sv"),str(ROOT/"fpga/conformance/tb_experimental_irq_differential.sv")],check=True)
 try: out=subprocess.check_output(["vvp",str(sim)],text=True)
 finally: sim.unlink(missing_ok=True)
 line=next(x for x in out.splitlines() if x.startswith("pc="))
 m=re.match(r"pc=([0-9a-f]+) sp=([0-9a-f]+) flags=([0-9a-f]+) halted=(\d) trap=(\d) frame=([0-9a-f]+),([0-9a-f]+),([0-9a-f]+)",line,re.I)
 return tuple(int(x,16) if i not in (3,4) else int(x) for i,x in enumerate(m.groups()[:5]))+(tuple(int(x,16) for x in m.groups()[5:]),)

a,b=reference(),rtl()
if a!=b:
 print("FAIL experimental IRQ differential\n reference=",a,"\n rtl=",b);raise SystemExit(1)
print("PASS experimental IRQ differential",a)
