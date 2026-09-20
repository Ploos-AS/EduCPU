"""Initial pedagogical EduIR -> EduASM backend."""
from educ_ir_validate import validate

class CodegenError(ValueError):pass

def generate(program):
 validate(program)
 return "\n".join(_function(f) for f in program.functions)+"\n"

def _function(f):
 if len(f.params)>4:raise CodegenError("ABI v0 supports at most four register parameters")
 regs={name:f"R{i}" for i,(_,name) in enumerate(f.params)}
 free=["R7","R6","R5","R4"]
 out=[f".export {f.name}",f"{f.name}:"]
 def src(v):
  if v not in regs:raise CodegenError(f"{f.name}: value has no register: {v}")
  return regs[v]
 def dest(v):
  if v in regs:return regs[v]
  if not free:raise CodegenError(f"{f.name}: initial backend register capacity exceeded")
  regs[v]=free.pop(0);return regs[v]
 for x in f.instructions:
  if x.op=="const":
   out.append(f"    MOVI {dest(x.dest)}, {x.args[0]}")
  elif x.op=="copy":
   s=src(x.args[0]);d=dest(x.dest)
   if s!=d:out.append(f"    MOV {d}, {s}")
  elif x.op in ("add","sub"):
   a,b=map(src,x.args);d=dest(x.dest)
   if d!=a:out.append(f"    MOV {d}, {a}")
   out.append(f"    {x.op.upper()} {d}, {b}")
  elif x.op=="ret":
   if x.args:
    s=src(x.args[0])
    if s!="R0":out.append(f"    MOV R0, {s}")
   out.append("    RET")
  else:raise CodegenError(f"{f.name}: IR op not in initial backend slice: {x.op}")
 return "\n".join(out)
