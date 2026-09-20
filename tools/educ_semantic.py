"""EduC v0 semantic analysis and type checking."""
from __future__ import annotations
from dataclasses import dataclass
from educ import Program,Function,VarDecl,Assign,Return,If,While,ExprStmt,Literal,Name,Call,Unary,Binary

class SemanticError(ValueError):pass
@dataclass(frozen=True)
class FunctionSig:
 return_type:str
 params:tuple[str,...]

def analyze(program:Program):
 functions={}
 for fn in program.functions:
  if fn.name in functions:raise SemanticError(f"duplicate function: {fn.name}")
  functions[fn.name]=FunctionSig(fn.return_type,tuple(t for t,_ in fn.params))
 for fn in program.functions:_function(fn,functions)
 return functions

def _function(fn,functions):
 vars={}
 for typ,name in fn.params:
  if name in vars:raise SemanticError(f"{fn.name}: duplicate parameter/local: {name}")
  vars[name]=typ
 for st in fn.body:_stmt(st,fn,vars,functions)
 if fn.return_type!="void" and not _block_returns(fn.body):
  raise SemanticError(f"{fn.name}: not all paths return {fn.return_type}")

def _stmt(st,fn,vars,functions):
 if isinstance(st,VarDecl):
  if st.name in vars:raise SemanticError(f"{fn.name}: duplicate parameter/local: {st.name}")
  got=_expr(st.value,vars,functions)
  if got!=st.type:raise SemanticError(f"{fn.name}: cannot initialize {st.type} {st.name} with {got}")
  vars[st.name]=st.type
 elif isinstance(st,Assign):
  if st.name not in vars:raise SemanticError(f"{fn.name}: unknown variable: {st.name}")
  got=_expr(st.value,vars,functions)
  if got!=vars[st.name]:raise SemanticError(f"{fn.name}: cannot assign {got} to {vars[st.name]} {st.name}")
 elif isinstance(st,Return):
  if fn.return_type=="void":
   if st.value is not None:raise SemanticError(f"{fn.name}: void function cannot return a value")
  else:
   if st.value is None:raise SemanticError(f"{fn.name}: {fn.return_type} function must return a value")
   got=_expr(st.value,vars,functions)
   if got!=fn.return_type:raise SemanticError(f"{fn.name}: returns {got}, expected {fn.return_type}")
 elif isinstance(st,If):
  if _expr(st.condition,vars,functions)!="bool":raise SemanticError(f"{fn.name}: if condition must be bool")
  for x in st.then_body:_stmt(x,fn,vars,functions)
  if st.else_body is not None:
   for x in st.else_body:_stmt(x,fn,vars,functions)
 elif isinstance(st,While):
  if _expr(st.condition,vars,functions)!="bool":raise SemanticError(f"{fn.name}: while condition must be bool")
  for x in st.body:_stmt(x,fn,vars,functions)
 elif isinstance(st,ExprStmt):
  if isinstance(st.value,Call):_call(st.value,vars,functions,allow_void=True)
  else:_expr(st.value,vars,functions)
 else:raise SemanticError(f"{fn.name}: unsupported statement {type(st).__name__}")

def _expr(x,vars,functions):
 if isinstance(x,Literal):return x.type
 if isinstance(x,Name):
  if x.name not in vars:raise SemanticError(f"unknown variable: {x.name}")
  return vars[x.name]
 if isinstance(x,Call):
  if x.name not in functions:raise SemanticError(f"unknown function: {x.name}")
  sig=functions[x.name]
  if len(x.args)!=len(sig.params):raise SemanticError(f"{x.name}: expected {len(sig.params)} arguments, got {len(x.args)}")
  for i,(arg,want) in enumerate(zip(x.args,sig.params),1):
   got=_expr(arg,vars,functions)
   if got!=want:raise SemanticError(f"{x.name}: argument {i} is {got}, expected {want}")
  if sig.return_type=="void":raise SemanticError(f"void function {x.name} cannot be used as a value")
  return sig.return_type
 if isinstance(x,Unary):
  got=_expr(x.value,vars,functions)
  if x.op=="!" and got=="bool":return "bool"
  raise SemanticError(f"operator {x.op} requires bool")
 if isinstance(x,Binary):
  a,b=_expr(x.left,vars,functions),_expr(x.right,vars,functions)
  if x.op in ("+","-"):
   if a==b=="byte":return "byte"
   raise SemanticError(f"operator {x.op} requires byte operands")
  if x.op in ("<","<=",">",">="):
   if a==b=="byte":return "bool"
   raise SemanticError(f"operator {x.op} requires byte operands")
  if x.op in ("==","!="):
   if a==b and a in ("byte","bool"):return "bool"
   raise SemanticError(f"operator {x.op} requires matching value types")
 raise SemanticError(f"unsupported expression {type(x).__name__}")

def _call(x,vars,functions,allow_void):
 if x.name not in functions:raise SemanticError(f"unknown function: {x.name}")
 sig=functions[x.name]
 if len(x.args)!=len(sig.params):raise SemanticError(f"{x.name}: expected {len(sig.params)} arguments, got {len(x.args)}")
 for i,(arg,want) in enumerate(zip(x.args,sig.params),1):
  got=_expr(arg,vars,functions)
  if got!=want:raise SemanticError(f"{x.name}: argument {i} is {got}, expected {want}")
 if sig.return_type=="void" and not allow_void:raise SemanticError(f"void function {x.name} cannot be used as a value")
 return sig.return_type

def _block_returns(body):
 for st in body:
  if isinstance(st,Return):return True
  if isinstance(st,If) and st.else_body is not None and _block_returns(st.then_body) and _block_returns(st.else_body):return True
 return False
