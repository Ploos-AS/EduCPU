"""Independent EduCPU ISA v0 emulator core.

This implementation deliberately does not import or inherit the reference CPU.
The reference model is an oracle used only by differential tests.
"""
from dataclasses import dataclass, field
from typing import Callable

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
    before_step: Callable[["Emulator"], None] | None = None
    after_step: Callable[["Emulator"], None] | None = None
    on_memory_read: Callable[[int, int], None] | None = None
    on_memory_write: Callable[[int, int], None] | None = None

    Z, N, C, V = 1, 2, 4, 8

    def reset(self) -> None:
        self.r[:] = [0] * 8
        self.pc = 0
        self.sp = 0xFF00
        self.flags = 0
        self.halted = False
        self.trap = None

    def _read_mem(self, address: int) -> int:
        address &= 0xFFFF
        value = self.mem[address]
        if self.on_memory_read:
            self.on_memory_read(address, value)
        return value

    def _write_mem(self, address: int, value: int) -> None:
        address &= 0xFFFF
        value &= 0xFF
        self.mem[address] = value
        if self.on_memory_write:
            self.on_memory_write(address, value)

    def _fetch(self) -> int:
        value = self._read_mem(self.pc)
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

    def _set_zn(self, value: int) -> None:
        self.flags &= ~(self.Z | self.N)
        if (value & 0xFF) == 0:
            self.flags |= self.Z
        if value & 0x80:
            self.flags |= self.N

    def _logic_flags(self, value: int) -> None:
        self.flags = 0
        self._set_zn(value)

    def _add8(self, left: int, right: int) -> int:
        total = left + right
        result = total & 0xFF
        self.flags = 0
        self._set_zn(result)
        if total > 0xFF:
            self.flags |= self.C
        if (~(left ^ right) & (left ^ result) & 0x80) != 0:
            self.flags |= self.V
        return result

    def _sub8(self, left: int, right: int) -> int:
        result = (left - right) & 0xFF
        self.flags = 0
        self._set_zn(result)
        if left >= right:
            self.flags |= self.C
        if ((left ^ right) & (left ^ result) & 0x80) != 0:
            self.flags |= self.V
        return result

    def _step(self) -> None:
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
            self._write_mem(address, self.r[source])
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
            self._write_mem(self.r[address_register], self.r[source])
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
            self._write_mem((self.sp + offset) & 0xFFFF, self.r[source])
            return

        if opcode in (0x20, 0x22, 0x24, 0x28, 0x29, 0x2A):
            left = self._reg_operand()
            if left is None:
                return
            right = self._reg_operand()
            if right is None:
                return
            if opcode == 0x20:
                self.r[left] = self._add8(self.r[left], self.r[right])
            elif opcode == 0x22:
                self.r[left] = self._sub8(self.r[left], self.r[right])
            elif opcode == 0x24:
                self._sub8(self.r[left], self.r[right])
            elif opcode == 0x28:
                self.r[left] &= self.r[right]
                self._logic_flags(self.r[left])
            elif opcode == 0x29:
                self.r[left] |= self.r[right]
                self._logic_flags(self.r[left])
            else:
                self.r[left] ^= self.r[right]
                self._logic_flags(self.r[left])
            return

        if opcode in (0x21, 0x23, 0x25):
            register = self._reg_operand()
            if register is None:
                return
            immediate = self._fetch()
            if opcode == 0x21:
                self.r[register] = self._add8(self.r[register], immediate)
            elif opcode == 0x23:
                self.r[register] = self._sub8(self.r[register], immediate)
            else:
                self._sub8(self.r[register], immediate)
            return

        if opcode == 0x2B:
            register = self._reg_operand()
            if register is None:
                return
            self.r[register] = (~self.r[register]) & 0xFF
            self._logic_flags(self.r[register])
            return

        if opcode in (0x2C, 0x2D):
            register = self._reg_operand()
            if register is None:
                return
            old = self.r[register]
            if opcode == 0x2C:
                result = (old << 1) & 0xFF
                carry = (old >> 7) & 1
            else:
                result = old >> 1
                carry = old & 1
            self._logic_flags(result)
            if carry:
                self.flags |= self.C
            self.r[register] = result
            return

        if 0x30 <= opcode <= 0x36:
            address = self._addr_operand()
            take = {
                0x30: True,
                0x31: bool(self.flags & self.Z),
                0x32: not bool(self.flags & self.Z),
                0x33: bool(self.flags & self.C),
                0x34: not bool(self.flags & self.C),
                0x35: bool(self.flags & self.N),
                0x36: not bool(self.flags & self.N),
            }[opcode]
            if take:
                self.pc = address
            return

        if opcode in (0x40, 0x41):
            register = self._reg_operand()
            if register is None:
                return
            if opcode == 0x40:
                self.sp = (self.sp - 1) & 0xFFFF
                self._write_mem(self.sp, self.r[register])
            else:
                self.r[register] = self.mem[self.sp]
                self.sp = (self.sp + 1) & 0xFFFF
            return

        if opcode == 0x42:
            self.sp = (self.sp - 1) & 0xFFFF
            self._write_mem(self.sp, (self.pc >> 8) & 0xFF)
            self.sp = (self.sp - 1) & 0xFFFF
            self._write_mem(self.sp, self.pc & 0xFF)
            return

        if opcode == 0x43:
            low = self.mem[self.sp]
            self.sp = (self.sp + 1) & 0xFFFF
            high = self.mem[self.sp]
            self.sp = (self.sp + 1) & 0xFFFF
            self.pc = low | (high << 8)
            return

        if opcode == 0x44:
            self.sp = (self.sp - 1) & 0xFFFF
            self.mem[self.sp] = (self.pc >> 8) & 0xFF
            self.sp = (self.sp - 1) & 0xFFFF
            self.mem[self.sp] = self.pc & 0xFF
            self.pc = self._addr_operand()
            return

        if opcode == 0x45:
            low = self.mem[self.sp]
            self.sp = (self.sp + 1) & 0xFFFF
            high = self.mem[self.sp]
            self.sp = (self.sp + 1) & 0xFFFF
            self.pc = low | (high << 8)
            return

        if opcode == 0x48:  # PUSHA
            for register in range(8):
                self.sp = (self.sp - 1) & 0xFFFF
                self._write_mem(self.sp, self.r[register])
            return

        if opcode == 0x49:  # POPA
            for register in reversed(range(8)):
                self.r[register] = self.mem[self.sp]
                self.sp = (self.sp + 1) & 0xFFFF
            return

        if opcode == 0x46:  # ENTER frame_size
            frame_size = self._fetch()
            self.sp = (self.sp - 1) & 0xFFFF
            self._write_mem(self.sp, (self.r[7] >> 8) & 0xFF)
            self.sp = (self.sp - 1) & 0xFFFF
            self._write_mem(self.sp, self.r[7] & 0xFF)
            self.r[7] = self.sp
            self.sp = (self.sp - frame_size) & 0xFFFF
            return

        if opcode == 0x47:  # LEAVE
            self.sp = self.r[7]
            low = self.mem[self.sp]
            self.sp = (self.sp + 1) & 0xFFFF
            high = self.mem[self.sp]
            self.sp = (self.sp + 1) & 0xFFFF
            self.r[7] = low | (high << 8)
            return

        self.trap = "INVALID_OPCODE"

    def step(self) -> None:
        if self.halted or self.trap:
            return
        if self.before_step:
            self.before_step(self)
        self._step()
        if self.after_step:
            self.after_step(self)

    def run(self, limit: int = 100000) -> int:
        count = 0
        while not self.halted and not self.trap and count < limit:
            self.step()
            count += 1
        return count
