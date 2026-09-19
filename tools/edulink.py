"""EduCPU M4 minimal object linker."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def link(objects):
 out=bytearray();symbols={};bases=[];pending=[]
 for obj in objects:
  base=len(out);bases.append(base);data=bytes.fromhex(obj["data"]);out.extend(data)
  for name,off in obj.get("exports",{}).items():
   if name in symbols:raise ValueError(f"duplicate symbol: {name}")
   symbols[name]=base+off
  for rel in obj.get("relocations",[]):pending.append((base,rel))
 for base,rel in pending:
  name=rel["symbol"]
  if name not in symbols:raise ValueError(f"undefined symbol: {name}")
  pos=base+rel["offset"];value=symbols[name]+rel.get("addend",0)
  if rel["type"]!="abs16le":raise ValueError(f"unsupported relocation: {rel['type']}")
  out[pos]=value&0xff;out[pos+1]=(value>>8)&0xff
 return bytes(out),symbols,bases

def main():
 p=argparse.ArgumentParser(prog="edulink");p.add_argument("objects",nargs="+");p.add_argument("-o","--output",required=True);p.add_argument("-m","--map");a=p.parse_args()
 objs=[json.loads(Path(x).read_text()) for x in a.objects];data,symbols,bases=link(objs);Path(a.output).write_bytes(data)
 if a.map:Path(a.map).write_text(json.dumps({"format":"educpu-link-map-v0","symbols":symbols,"bases":bases},indent=2)+"\n")
if __name__=="__main__":main()
