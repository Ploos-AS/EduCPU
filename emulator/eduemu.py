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

    def step(self) -> None:
        if self.halted or self.trap:
            return

        opcode = self._fetch()

        if opcode == 0x00:  # NOP
            return
        if opcode == 0x01:  # HALT
            self.halted = True
            return

        # Decode the register operand for MOV so malformed operands trap in
        # exactly the architectural place required by ISA v0. MOV execution
        # itself is introduced with the data-movement conformance stage.
        if opcode == 0x10:
            destination = self._reg_operand()
            if destination is None:
                return
            source = self._reg_operand()
            if source is None:
                return
            self.trap = "UNIMPLEMENTED_INSTRUCTION"
            return

        self.trap = "INVALID_OPCODE"

    def run(self, limit: int = 100000) -> int:
        count = 0
        while not self.halted and not self.trap and count < limit:
            self.step()
            count += 1
        return count
