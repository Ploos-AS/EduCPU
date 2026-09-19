"""EduCPU ISA v0 disassembler."""
from __future__ import annotations
import argparse
from pathlib import Path
from eduasm import OPS

BY_OPCODE={v[0]:(k,v[1]) for k,v in OPS.items()}
def disassemble(data):
    out=[];pc=0
    while pc<len(data):
        start=pc;op=data[pc];pc+=1
        if op not in BY_OPCODE:
            out.append((start,data[start:pc],f".BYTE 0x{op:02X}"));continue
        name,spec=BY_OPCODE[op];args=[];ok=True
        for typ in spec:
            need=1 if typ in ("r","i8") else 2
            if pc+need>len(data):ok=False;break
            if typ=="r":
                v=data[pc];pc+=1;args.append(f"R{v}" if v<8 else f"<R?{v}>")
            elif typ=="i8":
                args.append(f"0x{data[pc]:02X}");pc+=1
            else:
                v=data[pc]|(data[pc+1]<<8);pc+=2;args.append(f"0x{v:04X}")
        if not ok:
            out.append((start,data[start:],".BYTE "+", ".join(f"0x{x:02X}" for x in data[start:])));break
        text=name+(" "+", ".join(args) if args else "")
        out.append((start,data[start:pc],text))
    return out
def main():
    p=argparse.ArgumentParser(prog="edudis");p.add_argument("binary");a=p.parse_args()
    for pc,b,s in disassemble(Path(a.binary).read_bytes()):print(f"{pc:04X}  {b.hex(' ').upper():<14} {s}")
if __name__=="__main__":main()
