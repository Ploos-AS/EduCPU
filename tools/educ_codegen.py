"""Pedagogical EduIR -> EduASM backend with explicit stack slots."""
from educ_ir_validate import validate

class CodegenError(ValueError):pass

def generate(program):
 validate(program)
 return "\n".join(_function(f) for f in program.functions)+"\n"

def _function(f):
 if len(f.params)>4:raise CodegenError("ABI v0 supports at most four register parameters")
 names=[]
 for _,n in f.params:names.append(n)
 for x in f.instructions:
  if x.dest and x.dest not in names:names.append(x.dest)
 if len(names)>128:raise CodegenError(f"{f.name}: frame exceeds LOADS/STORES positive offset range")
 slots={n:i for i,n in enumerate(names)};frame=len(names)
 epilogue=f"__{f.name}_return"
 out=[f".export {f.name}",f"{f.name}:"]
 if frame:out.append(f"    ENTER {frame}")
 for i,(_,n) in enumerate(f.params):out.append(f"    STORES [{slots[n]}], R{i}")
 def load(v,r):
  if v not in slots:raise CodegenError(f"{f.name}: value has no stack slot: {v}")
  out.append(f"    LOADS {r}, [{slots[v]}]")
 def store(v,r):
  if v not in slots:raise CodegenError(f"{f.name}: destination has no stack slot: {v}")
  out.append(f"    STORES [{slots[v]}], {r}")
 def boolean_result(dest,jump):
  yes=f"__{f.name}_bool_true_{len(out)}";end=f"__{f.name}_bool_end_{len(out)}"
  out.append(f"    {jump} {yes}");out.append("    MOVI R7, 0");out.append(f"    JMP {end}")
  out.append(f"{yes}:");out.append("    MOVI R7, 1");out.append(f"{end}:");store(dest,"R7")
 for x in f.instructions:
  if x.op=="const":
   out.append(f"    MOVI R7, {x.args[0]}");store(x.dest,"R7")
  elif x.op=="copy":
   load(x.args[0],"R7");store(x.dest,"R7")
  elif x.op in ("add","sub"):
   load(x.args[0],"R7");load(x.args[1],"R6");out.append(f"    {x.op.upper()} R7, R6");store(x.dest,"R7")
  elif x.op=="not":
   load(x.args[0],"R7");out.append("    CMPI R7, 0");boolean_result(x.dest,"JZ")
  elif x.op in ("eq","ne","lt","le","gt","ge"):
   load(x.args[0],"R7");load(x.args[1],"R6");out.append("    CMP R7, R6")
   # Unsigned byte comparisons: C means no borrow (a>=b), Z means equal.
   if x.op=="eq":boolean_result(x.dest,"JZ")
   elif x.op=="ne":boolean_result(x.dest,"JNZ")
   elif x.op=="lt":boolean_result(x.dest,"JNC")
   elif x.op=="ge":boolean_result(x.dest,"JC")
   elif x.op=="le":
    yes=f"__{f.name}_le_true_{len(out)}";end=f"__{f.name}_le_end_{len(out)}"
    out.append(f"    JZ {yes}");out.append(f"    JNC {yes}");out.append("    MOVI R7, 0");out.append(f"    JMP {end}");out.append(f"{yes}:");out.append("    MOVI R7, 1");out.append(f"{end}:");store(x.dest,"R7")
   else:
    no=f"__{f.name}_gt_false_{len(out)}";end=f"__{f.name}_gt_end_{len(out)}"
    out.append(f"    JNC {no}");out.append(f"    JZ {no}");out.append("    MOVI R7, 1");out.append(f"    JMP {end}");out.append(f"{no}:");out.append("    MOVI R7, 0");out.append(f"{end}:");store(x.dest,"R7")
  elif x.op=="label":out.append(f"{x.args[0]}:")
  elif x.op=="jmp":out.append(f"    JMP {x.args[0]}")
  elif x.op=="br":
   load(x.args[0],"R7");out.append("    CMPI R7, 0");out.append(f"    JNZ {x.args[1]}");out.append(f"    JMP {x.args[2]}")
  elif x.op in ("call","callvoid"):
   fn=x.args[0];args=x.args[1:]
   if len(args)>4:raise CodegenError(f"{f.name}: call to {fn} exceeds four ABI register arguments")
   for i,v in enumerate(args):load(v,f"R{i}")
   out.append(f"    CALL {fn}")
   if x.op=="call":store(x.dest,"R0")
  elif x.op=="ret":
   if x.args:load(x.args[0],"R0")
   out.append(f"    JMP {epilogue}")
  else:raise CodegenError(f"{f.name}: IR op not yet supported by backend: {x.op}")
 out.append(f"{epilogue}:")
 if frame:out.append(f"    LEAVE {frame}")
 out.append("    RET")
 return "\n".join(out)
