"""Conceptual M10 micro-operation plans.

These are teaching phases, not a claim about RTL clock-cycle timing.
"""

NAMES={0x00:"NOP",0x01:"HALT",0x10:"MOV",0x11:"MOVI",0x12:"LOAD",0x13:"STORE",
0x14:"LOADR",0x15:"STORER",0x16:"LOADS",0x17:"STORES",0x18:"ENTER",0x19:"LEAVE",
0x20:"ADD",0x21:"ADDI",0x22:"SUB",0x23:"SUBI",0x24:"CMP",0x25:"CMPI",
0x28:"AND",0x29:"OR",0x2a:"XOR",0x2b:"NOT",0x2c:"SHL",0x2d:"SHR",
0x30:"JMP",0x31:"JZ",0x32:"JNZ",0x33:"JC",0x34:"JNC",0x35:"JN",0x36:"JP",
0x38:"CALL",0x39:"RET",0x40:"PUSH",0x41:"POP",0xe0:"IN",0xe1:"OUT"}

def _b(mem,a): return mem[a&0xffff]
def _reg(mem,a): return f"R{_b(mem,a)}"
def _addr(mem,a): return _b(mem,a)|(_b(mem,a+1)<<8)
def _fetch(pc,op): return ("FETCH",f"read opcode {op:02X} from memory[{pc&0xffff:04X}]")
def _decode(op): return ("DECODE",f"decode {op:02X} as {NAMES.get(op,'unknown opcode')}")

def instruction_plan(memory,pc):
 op=_b(memory,pc); p=[_fetch(pc,op),_decode(op)]
 if op==0x00:return p+[("COMMIT","NOP changes no architectural state")]
 if op==0x01:return p+[("CONTROL","set HALT state"),("COMMIT","CPU stops until reset or an enabled wake mechanism")]
 if op==0x10:
  d,s=_reg(memory,pc+1),_reg(memory,pc+2)
  return p+[("OPERAND",f"select destination {d}"),("OPERAND",f"read source {s}"),("TRANSFER",f"{s} -> {d}"),("COMMIT",f"write {d}; FLAGS unchanged")]
 if op==0x11:
  d,v=_reg(memory,pc+1),_b(memory,pc+2)
  return p+[("OPERAND",f"select destination {d}"),("OPERAND",f"read immediate {v:02X}"),("TRANSFER",f"{v:02X} -> {d}"),("COMMIT",f"write {d}; FLAGS unchanged")]
 if op in (0x20,0x22,0x24,0x28,0x29,0x2a):
  a,b=_reg(memory,pc+1),_reg(memory,pc+2); n=NAMES[op]
  dest="no register write" if op==0x24 else f"result -> {a}"
  return p+[("OPERAND",f"read {a}"),("OPERAND",f"read {b}"),("ALU",f"{n}({a},{b})"),("FLAGS","compute instruction flags"),("COMMIT",dest)]
 if op in (0x21,0x23,0x25):
  a,v=_reg(memory,pc+1),_b(memory,pc+2); n=NAMES[op]
  dest="no register write" if op==0x25 else f"result -> {a}"
  return p+[("OPERAND",f"read {a}"),("OPERAND",f"read immediate {v:02X}"),("ALU",f"{n}({a},{v:02X})"),("FLAGS","compute Z/N/C/V"),("COMMIT",dest)]
 if op in (0x14,0x15):
  a=_reg(memory,pc+2 if op==0x14 else pc+1)
  if op==0x14:
   d=_reg(memory,pc+1);return p+[("OPERAND",f"select {d}"),("OPERAND",f"read address register {a}"),("ADDRESS",f"use low-byte address from {a}"),("MEMORY READ",f"read memory[address in {a}]"),("TRANSFER",f"memory -> {d}"),("COMMIT",f"write {d}; FLAGS unchanged")]
  s=_reg(memory,pc+2);return p+[("OPERAND",f"read address register {a}"),("OPERAND",f"read {s}"),("ADDRESS",f"use low-byte address from {a}"),("MEMORY WRITE",f"{s} -> memory[address in {a}]"),("COMMIT","memory updated; FLAGS unchanged")]
 if op in (0x16,0x17):
  off=_b(memory,pc+2 if op==0x16 else pc+1); signed=off-256 if off&0x80 else off
  if op==0x16:
   d=_reg(memory,pc+1);return p+[("OPERAND",f"select {d}"),("OPERAND",f"read signed offset {signed}"),("ADDRESS",f"form SP {signed:+d}"),("MEMORY READ","read stack-relative byte"),("TRANSFER",f"memory -> {d}"),("COMMIT",f"write {d}; FLAGS unchanged")]
  s=_reg(memory,pc+2);return p+[("OPERAND",f"read signed offset {signed}"),("OPERAND",f"read {s}"),("ADDRESS",f"form SP {signed:+d}"),("MEMORY WRITE",f"{s} -> stack-relative address"),("COMMIT","memory updated; FLAGS unchanged")]
 if op in (0x18,0x19):
  n=_b(memory,pc+1);direction="-" if op==0x18 else "+"
  return p+[("OPERAND",f"read frame size {n}"),("STACK",f"SP <- SP {direction} {n}"),("COMMIT","new SP visible; FLAGS unchanged")]
 if op in (0x2b,0x2c,0x2d):
  d=_reg(memory,pc+1);n=NAMES[op]
  detail={0x2b:"bitwise invert",0x2c:"shift left; old bit 7 becomes carry",0x2d:"shift right; old bit 0 becomes carry"}[op]
  return p+[("OPERAND",f"read {d}"),("ALU",f"{n}: {detail}"),("FLAGS","compute instruction flags"),("COMMIT",f"result -> {d}")]
 if op in (0x12,0x13):
  a=_addr(memory,pc+2 if op==0x12 else pc+1)
  if op==0x12:
   d=_reg(memory,pc+1);return p+[("OPERAND",f"select {d}"),("ADDRESS",f"form address {a:04X}"),("MEMORY READ",f"read memory[{a:04X}]"),("TRANSFER",f"memory -> {d}"),("COMMIT",f"write {d}; FLAGS unchanged")]
  s=_reg(memory,pc+3);return p+[("ADDRESS",f"form address {a:04X}"),("OPERAND",f"read {s}"),("MEMORY WRITE",f"{s} -> memory[{a:04X}]"),("COMMIT","memory updated; FLAGS unchanged")]
 if 0x30<=op<=0x36:
  a=_addr(memory,pc+1);cond={"30":"always","31":"Z=1","32":"Z=0","33":"C=1","34":"C=0","35":"N=1","36":"N=0"}[f"{op:02X}"]
  return p+[("ADDRESS",f"form branch target {a:04X}"),("CONTROL",f"test condition {cond}"),("COMMIT",f"if true, PC <- {a:04X}; otherwise keep sequential PC")]
 if op==0x40:
  r=_reg(memory,pc+1);return p+[("OPERAND",f"read {r}"),("STACK","SP <- SP - 1"),("MEMORY WRITE",f"{r} -> memory[SP]"),("COMMIT","new SP and stack byte visible")]
 if op==0x41:
  r=_reg(memory,pc+1);return p+[("OPERAND",f"select {r}"),("MEMORY READ","read memory[SP]"),("STACK","SP <- SP + 1"),("COMMIT",f"stack byte -> {r}")]
 if op==0x38:
  a=_addr(memory,pc+1);return p+[("ADDRESS",f"form call target {a:04X}"),("CONTROL","capture sequential PC as return address"),("STACK","push return-address high byte"),("STACK","push return-address low byte"),("COMMIT",f"PC <- {a:04X}")]
 if op==0x39:return p+[("MEMORY READ","pop return-address low byte"),("MEMORY READ","pop return-address high byte"),("STACK","SP <- SP + 2"),("COMMIT","PC <- reconstructed return address")]
 if op in (0xe0,0xe1): return io_plan(memory,pc)
 return p+[("UNMODELED",f"{NAMES.get(op,'opcode')} micro-operation plan not added yet")]

def io_plan(memory,pc):
 op=_b(memory,pc)
 if op==0xe0:
  reg=_b(memory,pc+1);port=_b(memory,pc+2)
  return [_fetch(pc,op),_decode(op),("OPERAND",f"read destination register selector R{reg}"),("OPERAND",f"read I/O port address {port:02X}"),("I/O READ",f"select port {port:02X} and request one input byte"),("TRANSFER",f"transfer device byte from port {port:02X} toward R{reg}"),("COMMIT",f"write input byte to R{reg}; FLAGS unchanged")]
 if op==0xe1:
  port=_b(memory,pc+1);reg=_b(memory,pc+2)
  return [_fetch(pc,op),_decode(op),("OPERAND",f"read I/O port address {port:02X}"),("OPERAND",f"read source register selector R{reg}"),("I/O WRITE",f"select port {port:02X} and present byte from R{reg}"),("TRANSFER",f"transfer R{reg} byte to device at port {port:02X}"),("COMMIT","device observes output byte; FLAGS unchanged")]
 return []
