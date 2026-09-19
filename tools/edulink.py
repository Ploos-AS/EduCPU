"""EduCPU M4 minimal object linker."""
from __future__ import annotations
import argparse,json
from pathlib import Path
def link(objects):
 out=bytearray();symbols={};bases=[];pending=[]
 for obj in objects:
  if obj.get("format")!="educpu-object-v0":raise ValueError("unsupported object format")
  base=len(out);bases.append(base);data=bytes.fromhex(obj["data"]);out.extend(data);locals_=obj.get("locals",{})
  for name,off in obj.get("exports",{}).items():
   if name in symbols:raise ValueError(f"duplicate symbol: {name}")
   symbols[name]=base+off
  for rel in obj.get("relocations",[]):pending.append((base,locals_,rel))
 for base,locals_,rel in pending:
  name=rel["symbol"]
  if name in locals_:value=base+locals_[name]
  elif name in symbols:value=symbols[name]
  else:raise ValueError(f"undefined symbol: {name}")
  pos=base+rel["offset"];value+=rel.get("addend",0)
  if rel["type"]!="abs16le":raise ValueError(f"unsupported relocation: {rel['type']}")
  if not 0<=value<=0xffff:raise ValueError(f"relocation out of range: {name}")
  out[pos]=value&0xff;out[pos+1]=(value>>8)&0xff
 return bytes(out),symbols,bases
def main():
 p=argparse.ArgumentParser(prog="edulink");p.add_argument("objects",nargs="+");p.add_argument("-o","--output",required=True);p.add_argument("-m","--map");a=p.parse_args()
 objs=[json.loads(Path(x).read_text()) for x in a.objects];data,symbols,bases=link(objs);Path(a.output).write_bytes(data)
 if a.map:Path(a.map).write_text(json.dumps({"format":"educpu-link-map-v0","symbols":symbols,"bases":bases},indent=2)+"\n")
if __name__=="__main__":main()
