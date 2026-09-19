"""EduCPU ISA v0 executable reference model.

This is deliberately small and explicit. It is an architectural oracle, not a
performance-oriented emulator.
"""
from dataclasses import dataclass, field

MEM_SIZE = 65536

@dataclass
class CPU:
    r: list[int] = field(default_factory=lambda: [0] * 8)
    pc: int = 0
    sp: int = 0xFF00
    flags: int = 0
    mem: bytearray = field(default_factory=lambda: bytearray(MEM_SIZE))
    halted: bool = False
    trap: str | None = None

    Z, N, C, V = 1, 2, 4, 8

    def reset(self):
        self.r[:] = [0] * 8
        self.pc, self.sp, self.flags = 0, 0xFF00, 0
        self.halted, self.trap = False, None

    def fetch(self):
        v = self.mem[self.pc]
        self.pc = (self.pc + 1) & 0xFFFF
        return v

    def reg(self):
        n = self.fetch()
        if n > 7:
            self.trap = "INVALID_OPERAND"
            raise ValueError(self.trap)
        return n

    def addr(self):
        lo, hi = self.fetch(), self.fetch()
        return lo | (hi << 8)

    def set_zn(self, v):
        self.flags &= ~(self.Z | self.N)
        if (v & 0xFF) == 0: self.flags |= self.Z
        if v & 0x80: self.flags |= self.N

    def logic_flags(self, v):
        self.flags = 0
        self.set_zn(v)

    def add(self, a, b):
        s = a + b
        out = s & 0xFF
        self.flags = 0
        self.set_zn(out)
        if s > 0xFF: self.flags |= self.C
        if (~(a ^ b) & (a ^ out) & 0x80): self.flags |= self.V
        return out

    def sub(self, a, b):
        out = (a - b) & 0xFF
        self.flags = 0
        self.set_zn(out)
        if a >= b: self.flags |= self.C
        if ((a ^ b) & (a ^ out) & 0x80): self.flags |= self.V
        return out

    def push(self, v):
        self.sp = (self.sp - 1) & 0xFFFF
        self.mem[self.sp] = v & 0xFF

    def pop(self):
        v = self.mem[self.sp]
        self.sp = (self.sp + 1) & 0xFFFF
        return v

    def step(self):
        if self.halted or self.trap:
            return
        try:
            op = self.fetch()
            if op == 0x00: return
            if op == 0x01: self.halted = True; return
            if op == 0x10:
                d,s=self.reg(),self.reg(); self.r[d]=self.r[s]; return
            if op == 0x11:
                d=self.reg(); self.r[d]=self.fetch(); return
            if op == 0x12:
                d=self.reg(); self.r[d]=self.mem[self.addr()]; return
            if op == 0x13:
                a=self.addr(); s=self.reg(); self.mem[a]=self.r[s]; return
            if op == 0x14:
                d,a=self.reg(),self.reg(); self.r[d]=self.mem[self.r[a]]; return
            if op == 0x15:
                a,s=self.reg(),self.reg(); self.mem[self.r[a]]=self.r[s]; return
            if op in (0x20,0x22,0x24,0x28,0x29,0x2A):
                a,b=self.reg(),self.reg()
                if op==0x20: self.r[a]=self.add(self.r[a],self.r[b])
                elif op==0x22: self.r[a]=self.sub(self.r[a],self.r[b])
                elif op==0x24: self.sub(self.r[a],self.r[b])
                elif op==0x28: self.r[a]&=self.r[b]; self.logic_flags(self.r[a])
                elif op==0x29: self.r[a]|=self.r[b]; self.logic_flags(self.r[a])
                else: self.r[a]^=self.r[b]; self.logic_flags(self.r[a])
                return
            if op in (0x21,0x23,0x25):
                a=self.reg(); b=self.fetch()
                if op==0x21: self.r[a]=self.add(self.r[a],b)
                elif op==0x23: self.r[a]=self.sub(self.r[a],b)
                else: self.sub(self.r[a],b)
                return
            if op == 0x2B:
                d=self.reg(); self.r[d]=(~self.r[d])&0xFF; self.logic_flags(self.r[d]); return
            if op in (0x2C,0x2D):
                d=self.reg(); old=self.r[d]
                if op==0x2C: out=(old<<1)&0xFF; c=(old>>7)&1
                else: out=old>>1; c=old&1
                self.logic_flags(out)
                if c: self.flags|=self.C
                self.r[d]=out; return
            if 0x30 <= op <= 0x36:
                a=self.addr()
                take={0x30:True,0x31:bool(self.flags&self.Z),0x32:not(self.flags&self.Z),
                      0x33:bool(self.flags&self.C),0x34:not(self.flags&self.C),
                      0x35:bool(self.flags&self.N),0x36:not(self.flags&self.N)}[op]
                if take: self.pc=a
                return
            if op == 0x38:
                a=self.addr(); ret=self.pc
                self.push((ret>>8)&0xFF); self.push(ret&0xFF); self.pc=a; return
            if op == 0x39:
                lo=self.pop(); hi=self.pop(); self.pc=lo|(hi<<8); return
            if op == 0x40:
                self.push(self.r[self.reg()]); return
            if op == 0x41:
                d=self.reg(); self.r[d]=self.pop(); return
            self.trap = "INVALID_OPCODE"
        except ValueError:
            return

    def run(self, limit=100000):
        n=0
        while not self.halted and not self.trap and n < limit:
            self.step(); n += 1
        return n
