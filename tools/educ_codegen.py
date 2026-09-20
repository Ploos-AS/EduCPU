"""Pedagogical EduIR -> EduASM backend with explicit stack slots."""
from educ_ir_validate import validate

class CodegenError(ValueError):pass

def generate(program):
 validate(program)
 return "\n".join(_function(f) for f in program.functions)+"\n"

def _function(f):
 if len(f.params)>4:raise CodegenError("ABI v0 supports at most four register parameters")
 # Every IR value gets a visible one-byte frame slot. This is intentionally
 # simple rather than optimized: students can inspect where each value lives.
 names=[]
 for _,n in f.params:names.append(n)
 for x in f.instructions:
  if x.dest and x.dest not in names:names.append(x.dest)
 if len(names)>128:raise CodegenError(f"{f.name}: frame exceeds LOADS/STORES positive offset range")
 slots={n:i for i,n in enumerate(names)}
 frame=len(names)
 out=[f".export {f.name}",f"{f.name}:"]
 if frame:out.append(f"    ENTER {frame}")
 # Preserve ABI parameter values into their frame slots before R0-R3 become scratch.
 for i,(_,n) in enumerate(f.params):out.append(f"    STORES [{slots[n]}], R{i}")
 def load(v,r):
  if v not in slots:raise CodegenError(f"{f.name}: value has no stack slot: {v}")
  out.append(f"    LOADS {r}, [{slots[v]}]")
 def store(v,r):
  if v not in slots:raise CodegenError(f"{f.name}: destination has no stack slot: {v}")
  out.append(f"    STORES [{slots[v]}], {r}")
 for x in f.instructions:
  if x.op=="const":
   out.append(f"    MOVI R7, {x.args[0]}");store(x.dest,"R7")
  elif x.op=="copy":
   load(x.args[0],"R7");store(x.dest,"R7")
  elif x.op in ("add","sub"):
   load(x.args[0],"R7");load(x.args[1],"R6")
   out.append(f"    {x.op.upper()} R7, R6");store(x.dest,"R7")
  elif x.op=="ret":
   if x.args:load(x.args[0],"R0")
   if frame:out.append(f"    LEAVE {frame}")
   out.append("    RET")
  else:raise CodegenError(f"{f.name}: IR op not yet supported by backend: {x.op}")
 return "\n".join(out)
