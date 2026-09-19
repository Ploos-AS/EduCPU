"""EduC AST to pedagogical EduIR v0 lowering."""
from __future__ import annotations
from dataclasses import dataclass,field
from educ import *
from educ_semantic import analyze

@dataclass
class IRInstr:
 op:str; dest:str|None=None; type:str|None=None; args:list=field(default_factory=list)
@dataclass
class IRFunction:
 name:str; return_type:str; params:list; instructions:list
@dataclass
class IRProgram:
 functions:list

class Lower:
 def __init__(self,program):
  self.program=program;self.sigs=analyze(program);self.temp=0;self.label=0;self.out=[];self.types={}
 def newtemp(self,typ):
  n=f"%t{self.temp}";self.temp+=1;return n
 def newlabel(self,prefix):
  n=f"{prefix}_{self.label}";self.label+=1;return n
 def emit(self,op,dest=None,typ=None,*args):self.out.append(IRInstr(op,dest,typ,list(args)))
 def expr(self,x):
  if isinstance(x,Literal):
   d=self.newtemp(x.type);self.emit("const",d,x.type,x.value);return d,x.type
  if isinstance(x,Name):return x.name,self.types[x.name]
  if isinstance(x,Unary):
   a,_=self.expr(x.value);d=self.newtemp("bool");self.emit("not",d,"bool",a);return d,"bool"
  if isinstance(x,Binary):
   a,at=self.expr(x.left);b,_=self.expr(x.right);op={"+":"add","-":"sub","==":"eq","!=":"ne","<":"lt","<=":"le",">":"gt",">=":"ge"}[x.op]
   typ="byte" if op in ("add","sub") else "bool";d=self.newtemp(typ);self.emit(op,d,typ,a,b);return d,typ
  if isinstance(x,Call):
   vals=[]
   for a in x.args:vals.append(self.expr(a)[0])
   typ=self.sigs[x.name].return_type
   if typ=="void":self.emit("callvoid",None,None,x.name,*vals);return None,"void"
   d=self.newtemp(typ);self.emit("call",d,typ,x.name,*vals);return d,typ
  raise TypeError(type(x).__name__)
 def stmt(self,s):
  if isinstance(s,VarDecl):
   v,_=self.expr(s.value);self.types[s.name]=s.type;self.emit("copy",s.name,s.type,v)
  elif isinstance(s,Assign):
   v,_=self.expr(s.value);self.emit("copy",s.name,self.types[s.name],v)
  elif isinstance(s,Return):
   if s.value is None:self.emit("ret")
   else:self.emit("ret",None,None,self.expr(s.value)[0])
  elif isinstance(s,ExprStmt):self.expr(s.value)
  elif isinstance(s,If):
   cond,_=self.expr(s.condition);yes=self.newlabel("if_then");no=self.newlabel("if_else");end=self.newlabel("if_end")
   self.emit("br",None,None,cond,yes,no);self.emit("label",None,None,yes)
   for x in s.then_body:self.stmt(x)
   self.emit("jmp",None,None,end);self.emit("label",None,None,no)
   for x in s.else_body or []:self.stmt(x)
   self.emit("label",None,None,end)
  elif isinstance(s,While):
   head=self.newlabel("while_head");body=self.newlabel("while_body");end=self.newlabel("while_end")
   self.emit("label",None,None,head);cond,_=self.expr(s.condition);self.emit("br",None,None,cond,body,end);self.emit("label",None,None,body)
   for x in s.body:self.stmt(x)
   self.emit("jmp",None,None,head);self.emit("label",None,None,end)
  else:raise TypeError(type(s).__name__)
 def function(self,fn):
  self.temp=0;self.label=0;self.out=[];self.types={name:typ for typ,name in fn.params}
  for s in fn.body:self.stmt(s)
  return IRFunction(fn.name,fn.return_type,list(fn.params),self.out.copy())
 def run(self):return IRProgram([self.function(f) for f in self.program.functions])

def lower(program):return Lower(program).run()
def format_ir(p):
 lines=[]
 for f in p.functions:
  ps=", ".join(f"{t} {n}" for t,n in f.params);lines.append(f"func {f.return_type} {f.name}({ps})")
  for i in f.instructions:
   if i.op=="label":lines.append(f"{i.args[0]}:");continue
   rhs=i.op+(" "+", ".join(map(str,i.args)) if i.args else "")
   lines.append(("  "+f"{i.dest}:{i.type} = " if i.dest else "  ")+rhs)
  lines.append("end")
 return "\n".join(lines)+"\n"
