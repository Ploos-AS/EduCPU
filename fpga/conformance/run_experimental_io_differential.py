#!/usr/bin/env python3
"""Compare experimental I/O architectural results between reference machine and RTL."""
from pathlib import Path
import subprocess,sys,re
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"reference"))
from machine import experimental_machine

PROGRAM=bytes([0xe0,2,0x10,0xe1,0x20,2,0xe0,3,0x77,0x01])

def reference():
 m=experimental_machine(); c=m.cpu; c.mem[:len(PROGRAM)]=PROGRAM
 events=[]
 def read10(): return 0xa5
 def write20(v): pass
 m.register_io(0x10,read=read10);m.register_io(0x20,write=write20)
 while not c.halted and c.trap is None:
  m.last_io=None;m.step()
  if m.last_io: events.append((m.last_io["port"],m.last_io["value"]))
 return (c.pc,c.sp,c.flags,c.r[2],c.r[3],int(c.halted),int(c.trap is not None),tuple(events))

def rtl():
 sim=ROOT/"fpga/conformance/experimental_io_diff_simv"
 subprocess.run(["iverilog","-g2012","-o",str(sim),str(ROOT/"fpga/rtl/educpu_experimental_core.sv"),str(ROOT/"fpga/conformance/tb_experimental_io_differential.sv")],check=True)
 try: out=subprocess.check_output(["vvp",str(sim)],text=True)
 finally: sim.unlink(missing_ok=True)
 line=next(x for x in out.splitlines() if x.startswith("pc="))
 pat=r"pc=([0-9a-f]+) sp=([0-9a-f]+) flags=([0-9a-f]+) r2=([0-9a-f]+) r3=([0-9a-f]+) halted=(\d) trap=(\d) tx=(\d) p0=([0-9a-f]+) v0=([0-9a-f]+) p1=([0-9a-f]+) v1=([0-9a-f]+) p2=([0-9a-f]+) v2=([0-9a-f]+)"
 g=re.match(pat,line,re.I).groups()
 head=tuple(int(x,16) for x in g[:5])+(int(g[5]),int(g[6]))
 events=((int(g[8],16),int(g[9],16)),(int(g[10],16),int(g[11],16)),(int(g[12],16),int(g[13],16)))
 if int(g[7])!=3: raise SystemExit("FAIL RTL transaction count")
 return head+(events,)

a,b=reference(),rtl()
if a!=b:
 print("FAIL experimental IO differential\n reference=",a,"\n rtl=",b);raise SystemExit(1)
print("PASS experimental IO differential",a)
