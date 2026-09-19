"""Independent structural/type validator for EduIR v0."""
from educ_ir import IRProgram
class IRValidationError(ValueError):pass

def validate(p:IRProgram):
 funcs={f.name:f for f in p.functions}
 if len(funcs)!=len(p.functions):raise IRValidationError("duplicate IR function")
 sigs={n:(f.return_type,[t for t,_ in f.params]) for n,f in funcs.items()}
 for f in p.functions:_function(f,sigs)
 return True

def _function(f,sigs):
 vals={n:t for t,n in f.params};labels={}
 for i,x in enumerate(f.instructions):
  if x.op=="label":
   n=x.args[0]
   if n in labels:raise IRValidationError(f"{f.name}: duplicate label {n}")
   labels[n]=i
 for x in f.instructions:
  op=x.op
  if x.dest:
   if x.dest.startswith("%") and x.dest in vals:raise IRValidationError(f"{f.name}: temporary redefined {x.dest}")
   if x.dest in vals and x.dest.startswith("%"):raise IRValidationError(f"{f.name}: duplicate value {x.dest}")
  def value(n):
   if n not in vals:raise IRValidationError(f"{f.name}: undefined value {n}")
   return vals[n]
  if op=="const":
   if x.type not in ("byte","bool"):raise IRValidationError(f"{f.name}: bad const type")
   n=x.args[0]
   if x.type=="byte" and not 0<=n<=255:raise IRValidationError(f"{f.name}: byte const out of range")
   if x.type=="bool" and n not in (0,1):raise IRValidationError(f"{f.name}: bool const must be 0 or 1")
  elif op=="copy":
   if value(x.args[0])!=x.type:raise IRValidationError(f"{f.name}: copy type mismatch")
  elif op in ("add","sub"):
   if x.type!="byte" or any(value(a)!="byte" for a in x.args):raise IRValidationError(f"{f.name}: {op} requires byte")
  elif op=="not":
   if x.type!="bool" or value(x.args[0])!="bool":raise IRValidationError(f"{f.name}: not requires bool")
  elif op in ("lt","le","gt","ge"):
   if x.type!="bool" or any(value(a)!="byte" for a in x.args):raise IRValidationError(f"{f.name}: {op} requires byte")
  elif op in ("eq","ne"):
   a,b=map(value,x.args)
   if x.type!="bool" or a!=b:raise IRValidationError(f"{f.name}: {op} requires matching types")
  elif op in ("call","callvoid"):
   name=x.args[0]
   if name not in sigs:raise IRValidationError(f"{f.name}: unknown callee {name}")
   ret,params=sigs[name];args=x.args[1:]
   if len(args)!=len(params):raise IRValidationError(f"{f.name}: bad call arity for {name}")
   if [value(a) for a in args]!=params:raise IRValidationError(f"{f.name}: bad call types for {name}")
   if op=="call" and (ret=="void" or x.type!=ret):raise IRValidationError(f"{f.name}: bad call result type")
   if op=="callvoid" and ret!="void":raise IRValidationError(f"{f.name}: callvoid requires void callee")
  elif op=="br":
   if value(x.args[0])!="bool":raise IRValidationError(f"{f.name}: branch condition must be bool")
   for lab in x.args[1:]:
    if lab not in labels:raise IRValidationError(f"{f.name}: unknown label {lab}")
  elif op=="jmp":
   if x.args[0] not in labels:raise IRValidationError(f"{f.name}: unknown label {x.args[0]}")
  elif op=="ret":
   if f.return_type=="void":
    if x.args:raise IRValidationError(f"{f.name}: void return has value")
   elif len(x.args)!=1 or value(x.args[0])!=f.return_type:raise IRValidationError(f"{f.name}: return type mismatch")
  elif op=="label":pass
  else:raise IRValidationError(f"{f.name}: unknown IR op {op}")
  if x.dest:vals[x.dest]=x.type
