"""Opt-in M10 emulator extensions.

ISA v0 Emulator remains untouched; this wrapper adds only capability-gated IRQ
state and experimental IRET (0xF0).
"""
from dataclasses import dataclass
from emulator import eduemu
from capabilities import M10_EXPERIMENTAL


@dataclass
class ExperimentalEmulator:
    cpu: eduemu.Emulator = None

    def __post_init__(self):
        if self.cpu is None:
            self.cpu = eduemu.Emulator()
        self.irq_pending = False
        self.irq_enabled = True
        self.irq_vector = 0
        self.in_interrupt = False

    def reset(self):
        self.cpu.reset()
        self.irq_pending = False
        self.irq_enabled = True
        self.in_interrupt = False

    def request_irq(self):
        self.irq_pending = True

    def _push(self, value):
        self.cpu.sp = (self.cpu.sp - 1) & 0xffff
        self.cpu._write_mem(self.cpu.sp, value)

    def _pop(self):
        value = self.cpu._read_mem(self.cpu.sp)
        self.cpu.sp = (self.cpu.sp + 1) & 0xffff
        return value

    def _accept_irq(self):
        if not self.irq_pending or not self.irq_enabled or self.cpu.trap or self.in_interrupt:
            return False
        self.irq_pending = False
        self.cpu.halted = False
        pc = self.cpu.pc
        self._push((pc >> 8) & 0xff)
        self._push(pc & 0xff)
        self._push(self.cpu.flags)
        self.in_interrupt = True
        self.irq_enabled = False
        self.cpu.pc = self.irq_vector & 0xffff
        return True

    def step(self):
        if self._accept_irq():
            return
        if self.in_interrupt and self.cpu.mem[self.cpu.pc] == 0xf0:
            self.cpu.pc = (self.cpu.pc + 1) & 0xffff
            self.cpu.flags = self._pop()
            low = self._pop()
            high = self._pop()
            self.cpu.pc = low | (high << 8)
            self.in_interrupt = False
            self.irq_enabled = True
            return
        self.cpu.step()

    def run(self, limit=100000):
        count = 0
        while count < limit and not self.cpu.trap:
            if self.cpu.halted and not (self.irq_pending and self.irq_enabled and not self.in_interrupt):
                break
            self.step()
            count += 1
        return count

    def snapshot(self):
        state = self.cpu.snapshot()
        state.update({
            "irq_pending": self.irq_pending,
            "irq_enabled": self.irq_enabled,
            "irq_vector": self.irq_vector,
            "in_interrupt": self.in_interrupt,
            "capabilities": sorted(M10_EXPERIMENTAL.capabilities),
        })
        return state
