"""Independent EduCPU ISA v0 emulator core.

This implementation deliberately does not import or inherit the reference CPU.
The reference model is an oracle used only by differential tests.
"""
from dataclasses import dataclass, field

MEM_SIZE = 65536


@dataclass
class Emulator:
    r: list[int] = field(default_factory=lambda: [0] * 8)
    pc: int = 0
    sp: int = 0xFF00
    flags: int = 0
    mem: bytearray = field(default_factory=lambda: bytearray(MEM_SIZE))
    halted: bool = False
    trap: str | None = None

    Z, N, C, V = 1, 2, 4, 8

    def reset(self) -> None:
        self.r[:] = [0] * 8
        self.pc = 0
        self.sp = 0xFF00
        self.flags = 0
        self.halted = False
        self.trap = None

    def _fetch(self) -> int:
        value = self.mem[self.pc]
        self.pc = (self.pc + 1) & 0xFFFF
        return value

    def _reg_operand(self) -> int | None:
        number = self._fetch()
        if number > 7:
            self.trap = "INVALID_OPERAND"
            return None
        return number

    def _addr_operand(self) -> int:
        low = self._fetch()
        high = self._fetch()
        return low | (high << 8)

    def _signed_offset(self) -> int:
        value = self._fetch()
        return value - 256 if value & 0x80 else value

    def step(self) -> None:
        if self.halted or self.trap:
            return

        opcode = self._fetch()

        if opcode == 0x00:  # NOP
            return
        if opcode == 0x01:  # HALT
            self.halted = True
            return

        if opcode == 0x10:  # MOV rd,rs
            destination = self._reg_operand()
            if destination is None:
                return
            source = self._reg_operand()
            if source is None:
                return
            self.r[destination] = self.r[source]
            return
        if opcode == 0x11:  # MOVI rd,imm8
            destination = self._reg_operand()
            if destination is None:
                return
            self.r[destination] = self._fetch()
            return
        if opcode == 0x12:  # LOAD rd,[addr16]
            destination = self._reg_operand()
            if destination is None:
                return
            self.r[destination] = self.mem[self._addr_operand()]
            return
        if opcode == 0x13:  # STORE [addr16],rs
            address = self._addr_operand()
            source = self._reg_operand()
            if source is None:
                return
            self.mem[address] = self.r[source]
            return
        if opcode == 0x14:  # LOADR rd,[ra]
            destination = self._reg_operand()
            if destination is None:
                return
            address_register = self._reg_operand()
            if address_register is None:
                return
            self.r[destination] = self.mem[self.r[address_register]]
            return
        if opcode == 0x15:  # STORER [ra],rs
            address_register = self._reg_operand()
            if address_register is None:
                return
            source = self._reg_operand()
            if source is None:
                return
            self.mem[self.r[address_register]] = self.r[source]
            return
        if opcode == 0x16:  # LOADS rd,[SP+off8]
            destination = self._reg_operand()
            if destination is None:
                return
            offset = self._signed_offset()
            self.r[destination] = self.mem[(self.sp + offset) & 0xFFFF]
            return
        if opcode == 0x17:  # STORES [SP+off8],rs
            offset = self._signed_offset()
            source = self._reg_operand()
            if source is None:
                return
            self.mem[(self.sp + offset) & 0xFFFF] = self.r[source]
            return

        self.trap = "INVALID_OPCODE"

    def run(self, limit: int = 100000) -> int:
        count = 0
        while not self.halted and not self.trap and count < limit:
            self.step()
            count += 1
        return count
