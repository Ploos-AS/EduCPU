"""EduC v0 lexer, parser and AST."""
from __future__ import annotations
from dataclasses import dataclass,asdict
import argparse,json,re
from pathlib import Path

@dataclass
class Token: kind:str; value:str; line:int; col:int
@dataclass
class Program: functions:list
@dataclass
class Function: return_type:str; name:str; params:list; body:list
@dataclass
class VarDecl: type:str; name:str; value:object
@dataclass
class Assign: name:str; value:object
@dataclass
class Return: value:object|None
@dataclass
class If: condition:object; then_body:list; else_body:list|None
@dataclass
class While: condition:object; body:list
@dataclass
class ExprStmt: value:object
@dataclass
class Literal: value:int; type:str
@dataclass
class Name: name:str
@dataclass
class Call: name:str; args:list
@dataclass
class Unary: op:str; value:object
@dataclass
class Binary: op:str; left:object; right:object

TOKEN_RE=re.compile(r'(?P<WS>[ \t]+)|(?P<NL>\n)|(?P<COMMENT>//[^\n]*)|(?P<NUMBER>\d+)|(?P<ID>[A-Za-z_][A-Za-z0-9_]*)|(?P<OP>==|!=|<=|>=|[+\-!<>=(),;{}])')
KEYWORDS={"byte","bool","void","return","if","else","while","true","false"}
def lex(text):
 out=[];pos=0;line=1;start=0
 while pos<len(text):
  m=TOKEN_RE.match(text,pos)
  if not m:raise SyntaxError(f"line {line}:{pos-start+1}: unexpected character {text[pos]!r}")
  k=m.lastgroup;v=m.group()
  if k=="NL":line+=1;start=m.end()
  elif k not in ("WS","COMMENT"):out.append(Token(v if k=="OP" else (v if v in KEYWORDS else k),v,line,m.start()-start+1))
  pos=m.end()
 out.append(Token("EOF","",line,pos-start+1));return out

class Parser:
 def __init__(self,tokens):self.t=tokens;self.i=0
 def cur(self):return self.t[self.i]
 def take(self,k):
  t=self.cur()
  if t.kind!=k:raise SyntaxError(f"line {t.line}:{t.col}: expected {k}, got {t.value or t.kind}")
  self.i+=1;return t
 def maybe(self,k):
  if self.cur().kind==k:self.i+=1;return True
  return False
 def type(self,allow_void=True):
  k=self.cur().kind
  if k not in (("byte","bool","void") if allow_void else ("byte","bool")):self.take("TYPE")
  self.i+=1;return k
 def program(self):
  fs=[]
  while self.cur().kind!="EOF":fs.append(self.function())
  return Program(fs)
 def function(self):
  typ=self.type();name=self.take("ID").value;self.take("(");params=[]
  if self.cur().kind!=")":
   while True:
    pt=self.type(False);pn=self.take("ID").value;params.append((pt,pn))
    if not self.maybe(","):break
  self.take(")")
  if len(params)>4:raise SyntaxError("EduC v0 functions support at most four parameters")
  return Function(typ,name,params,self.block())
 def block(self):
  self.take("{");out=[]
  while self.cur().kind!="}":out.append(self.statement())
  self.take("}");return out
 def statement(self):
  k=self.cur().kind
  if k in ("byte","bool"):
   typ=self.type(False);name=self.take("ID").value;self.take("=");v=self.expr();self.take(";");return VarDecl(typ,name,v)
  if k=="return":
   self.take("return");v=None if self.cur().kind==";" else self.expr();self.take(";");return Return(v)
  if k=="if":
   self.take("if");self.take("(");cond=self.expr();self.take(")");yes=self.block();no=self.block() if self.maybe("else") else None;return If(cond,yes,no)
  if k=="while":
   self.take("while");self.take("(");cond=self.expr();self.take(")");return While(cond,self.block())
  if k=="ID" and self.t[self.i+1].kind=="=":
   name=self.take("ID").value;self.take("=");v=self.expr();self.take(";");return Assign(name,v)
  v=self.expr();self.take(";");return ExprStmt(v)
 def expr(self):return self.comparison()
 def comparison(self):
  x=self.additive()
  while self.cur().kind in ("==","!=","<","<=",">",">="):
   op=self.cur().kind;self.i+=1;x=Binary(op,x,self.additive())
  return x
 def additive(self):
  x=self.unary()
  while self.cur().kind in ("+","-"):
   op=self.cur().kind;self.i+=1;x=Binary(op,x,self.unary())
  return x
 def unary(self):
  if self.maybe("!"):return Unary("!",self.unary())
  return self.primary()
 def primary(self):
  t=self.cur()
  if t.kind=="NUMBER":
   self.i+=1;v=int(t.value)
   if v>255:raise SyntaxError(f"line {t.line}:{t.col}: byte literal out of range")
   return Literal(v,"byte")
  if t.kind in ("true","false"):self.i+=1;return Literal(1 if t.kind=="true" else 0,"bool")
  if self.maybe("("):x=self.expr();self.take(")");return x
  name=self.take("ID").value
  if self.maybe("("):
   args=[]
   if self.cur().kind!=")":
    while True:
     args.append(self.expr())
     if not self.maybe(","):break
   self.take(")");return Call(name,args)
  return Name(name)

def parse(text):return Parser(lex(text)).program()
def ast_dict(node):
 if hasattr(node,"__dataclass_fields__"):
  d={"node":type(node).__name__};d.update({k:ast_dict(v) for k,v in asdict(node).items()});return d
 if isinstance(node,list):return [ast_dict(x) for x in node]
 if isinstance(node,tuple):return [ast_dict(x) for x in node]
 if isinstance(node,dict):return {k:ast_dict(v) for k,v in node.items()}
 return node
def compile_source(text,source_name=None):
 from educ_ir import lower
 from educ_codegen import generate
 from eduasm import assemble_object
 from edulink import link
 tree=parse(text);ir=lower(tree);asm=generate(ir);obj,_=assemble_object(asm,source_name);data,symbols,_=link([obj])
 return tree,ir,asm,obj,data,symbols

def main():
 p=argparse.ArgumentParser(prog="educ");p.add_argument("source");p.add_argument("--tokens",action="store_true");p.add_argument("--ast",action="store_true");p.add_argument("--check",action="store_true");p.add_argument("--ir",action="store_true");p.add_argument("--ir-check",action="store_true");p.add_argument("-S","--assembly",action="store_true");p.add_argument("-c","--object",action="store_true");p.add_argument("-o","--output");a=p.parse_args();src=Path(a.source);text=src.read_text()
 if a.tokens:
  for t in lex(text):print(f"{t.line}:{t.col}\\t{t.kind}\\t{t.value}")
 tree=parse(text)
 if a.ast:print(json.dumps(ast_dict(tree),indent=2))
 if a.check:
  from educ_semantic import analyze
  analyze(tree)
 if a.ir or a.ir_check:
  from educ_ir import lower,format_ir
  from educ_ir_validate import validate
  ir=lower(tree)
  if a.ir_check:validate(ir)
  if a.ir:print(format_ir(ir),end="")
 if a.assembly or a.object or a.output:
  tree,ir,asm,obj,data,symbols=compile_source(text,str(src))
  if a.assembly:
   if a.output:Path(a.output).write_text(asm)
   else:print(asm,end="")
  elif a.object:
   dest=Path(a.output or src.with_suffix(".eo"));dest.write_text(json.dumps(obj,indent=2)+"\\n")
  else:
   Path(a.output).write_bytes(data)
 if not any((a.tokens,a.ast,a.check,a.ir,a.ir_check,a.assembly,a.object,a.output)):
  print(json.dumps(ast_dict(tree),indent=2))
if __name__=="__main__":main()
