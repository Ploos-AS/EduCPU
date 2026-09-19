"""EduASM assembler and M4 object emitter for EduCPU ISA v0."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

OPS={
"NOP":(0x00,[]),"HALT":(0x01,[]),"MOV":(0x10,["r","r"]),"MOVI":(0x11,["r","i8"]),
"LOAD":(0x12,["r","a16"]),"STORE":(0x13,["a16","r"]),"LOADR":(0x14,["r","r"]),"STORER":(0x15,["r","r"]),
"LOADS":(0x16,["r","s8"]),"STORES":(0x17,["s8","r"]),"ENTER":(0x18,["i8"]),"LEAVE":(0x19,["i8"]),
"ADD":(0x20,["r","r"]),"ADDI":(0x21,["r","i8"]),"SUB":(0x22,["r","r"]),"SUBI":(0x23,["r","i8"]),
"CMP":(0x24,["r","r"]),"CMPI":(0x25,["r","i8"]),"AND":(0x28,["r","r"]),"OR":(0x29,["r","r"]),"XOR":(0x2A,["r","r"]),
"NOT":(0x2B,["r"]),"SHL":(0x2C,["r"]),"SHR":(0x2D,["r"]),"JMP":(0x30,["a16"]),"JZ":(0x31,["a16"]),
"JNZ":(0x32,["a16"]),"JC":(0x33,["a16"]),"JNC":(0x34,["a16"]),"JN":(0x35,["a16"]),"JP":(0x36,["a16"]),
"CALL":(0x38,["a16"]),"RET":(0x39,[]),"PUSH":(0x40,["r"]),"POP":(0x41,["r"])}

def clean(s):return s.split(";",1)[0].split("#",1)[0].strip()
def number(s,labels):
 s=s.strip()
 if s in labels:return labels[s]
 if s.startswith("$"):return int(s[1:],16)
 if s.lower().startswith("0x"):return int(s,16)
 if s.lower().startswith("0b"):return int(s,2)
 return int(s,10)
def reg(s):
 m=re.fullmatch(r"[Rr]([0-7])",s.strip())
 if not m:raise ValueError(f"expected R0..R7, got {s}")
 return int(m.group(1))
def unwrap_addr(s):
 s=s.strip();return s[1:-1].strip() if s.startswith("[") and s.endswith("]") else s
def parse(lines):
 labels={};rows=[];exports=set();imports=set();pc=0
 for no,raw in enumerate(lines,1):
  line=clean(raw)
  if not line:continue
  if line.lower().startswith((".export ",".import ")):
   directive,name=line.split(None,1);name=name.strip()
   if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*",name):raise ValueError(f"line {no}: bad symbol {name}")
   (exports if directive.lower()==".export" else imports).add(name);continue
  if ":" in line:
   label,rest=line.split(":",1);label=label.strip()
   if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*",label):raise ValueError(f"line {no}: bad label")
   if label in labels:raise ValueError(f"line {no}: duplicate label {label}")
   labels[label]=pc;line=rest.strip()
   if not line:continue
  parts=line.split(None,1);name=parts[0].upper()
  if name not in OPS:raise ValueError(f"line {no}: unknown instruction {name}")
  args=[] if len(parts)==1 else [x.strip() for x in parts[1].split(",")];spec=OPS[name][1]
  if len(args)!=len(spec):raise ValueError(f"line {no}: {name} expects {len(spec)} operands")
  rows.append((no,pc,name,args,raw.rstrip()));pc+=1+sum(1 if typ in ("r","i8","s8") else 2 for typ in spec)
 return labels,rows,exports,imports

def _encode(labels,rows,object_mode=False,imports=frozenset()):
 out=bytearray();listing=[];relocs=[]
 for no,pc,name,args,source in rows:
  op,spec=OPS[name];b=[op]
  try:
   for typ,arg in zip(spec,args):
    raw=unwrap_addr(arg)
    if typ=="r":b.append(reg(raw))
    elif typ=="i8":
     v=number(raw,labels)
     if not 0<=v<=255:raise ValueError("8-bit immediate out of range")
     b.append(v)
    elif typ=="s8":
     v=number(raw,labels)
     if not -128<=v<=127:raise ValueError("signed stack offset out of range")
     b.append(v&255)
    else:
     operand_offset=pc+len(b)
     if object_mode and (raw in labels or raw in imports):
      if raw not in labels and raw not in imports:raise ValueError(f"unknown symbol {raw}")
      relocs.append({"offset":operand_offset,"type":"abs16le","symbol":raw});v=0
     else:v=number(raw,labels)
     if not 0<=v<=65535:raise ValueError("16-bit address out of range")
     b.extend((v&255,v>>8))
  except ValueError as e:raise ValueError(f"line {no}: {e}") from e
  out.extend(b);listing.append((pc,bytes(b),source,no))
 return bytes(out),listing,relocs

def assemble_text(text,listing=False):
 labels,rows,exports,imports=parse(text.splitlines())
 if imports:raise ValueError("imports require object output")
 data,listing_rows,_=_encode(labels,rows)
 return data,labels,listing_rows

def assemble_object(text,source_name=None):
 labels,rows,exports,imports=parse(text.splitlines())
 missing=exports-labels.keys()
 if missing:raise ValueError("export has no label: "+", ".join(sorted(missing)))
 overlap=imports & labels.keys()
 if overlap:raise ValueError("symbol cannot be both imported and local: "+", ".join(sorted(overlap)))
 data,listing,relocs=_encode(labels,rows,True,imports)
 referenced={r["symbol"] for r in relocs}
 unused=imports-referenced
 if unused:raise ValueError("unused import: "+", ".join(sorted(unused)))
 obj={"format":"educpu-object-v0","data":data.hex(),"exports":{n:labels[n] for n in sorted(exports)},
      "locals":labels,"imports":sorted(imports),"relocations":relocs}
 if source_name:obj["source"]=source_name
 return obj,listing

def debug_map(rows,source_name=None):
 return {"format":"educpu-debug-v0","source":source_name,"instructions":[{"address":pc,"size":len(b),"line":no,"source":src,"bytes":b.hex()} for pc,b,src,no in rows]}

def main():
 p=argparse.ArgumentParser(prog="eduasm");p.add_argument("source");p.add_argument("-o","--output");p.add_argument("-l","--listing",action="store_true");p.add_argument("-g","--debug-map",action="store_true");p.add_argument("-c","--object",action="store_true");a=p.parse_args()
 src=Path(a.source)
 if a.object:
  obj,rows=assemble_object(src.read_text(),str(src));dest=Path(a.output or src.with_suffix(".eo"));dest.write_text(json.dumps(obj,indent=2)+"\n")
 else:
  data,_,rows=assemble_text(src.read_text());dest=Path(a.output or src.with_suffix(".bin"));dest.write_bytes(data)
 if a.listing:
  for pc,b,s,no in rows:print(f"{pc:04X}  {b.hex(' ').upper():<14} L{no:<4} {s}")
 if a.debug_map:
  dest.with_suffix(dest.suffix+".dbg.json").write_text(json.dumps(debug_map(rows,str(src)),indent=2)+"\n")
if __name__=="__main__":main()
