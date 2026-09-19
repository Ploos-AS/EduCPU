"""Pedagogical micro-step model for EduCPU.

This models visible teaching phases. It does not define FPGA timing.
"""
from dataclasses import dataclass
from edudis import disassemble

@dataclass(frozen=True)
class MicroStep:
    phase: str
    text: str

def _decode(mem, pc):
    return disassemble(bytes(mem[pc:pc+4]))[0][2]

def plan(cpu):
    pc=cpu.pc; op=cpu.mem[pc]; ins=_decode(cpu.mem,pc)
    steps=[
        MicroStep("FETCH_ADDR",f"Address bus <- PC = 0x{pc:04X}"),
        MicroStep("FETCH_OPCODE",f"IR <- MEM[0x{pc:04X}] = 0x{op:02X}"),
        MicroStep("DECODE",f"Decode IR 0x{op:02X}: {ins}"),
    ]
    if op not in (0x00,0x01,0x39):
        steps.append(MicroStep("READ_OPERANDS","Read encoded operands and required register/memory values"))
    if op in range(0x20,0x2E):
        steps.append(MicroStep("ALU","ALU performs arithmetic, logic, compare, or shift operation"))
    elif op in (0x12,0x14):
        steps.append(MicroStep("MEM_READ","Read data memory operand"))
    elif op in (0x13,0x15):
        steps.append(MicroStep("MEM_WRITE","Write data memory operand"))
    elif 0x30<=op<=0x39:
        steps.append(MicroStep("CONTROL","Evaluate/perform control-flow operation"))
    elif op in (0x40,0x41):
        steps.append(MicroStep("STACK","Perform stack memory operation"))
    elif op not in (0x00,0x01):
        steps.append(MicroStep("EXECUTE","Perform instruction operation"))
    if op in range(0x20,0x2E):
        steps.append(MicroStep("FLAGS","Update flags defined by the ISA"))
    if op not in (0x00,0x24,0x25,0x30,0x31,0x32,0x33,0x34,0x35,0x36,0x38,0x39,0x40,0x01):
        steps.append(MicroStep("WRITEBACK","Commit result to destination register"))
    steps.append(MicroStep("PC","PC now identifies the next architectural instruction"))
    return steps

class MicroStepper:
    def __init__(self,cpu):
        self.cpu=cpu; self.steps=[]; self.index=0; self.start_pc=None

    @property
    def active(self): return bool(self.steps)

    def begin(self):
        if self.cpu.halted or self.cpu.trap:return None
        self.start_pc=self.cpu.pc;self.steps=plan(self.cpu);self.index=0
        return self.steps[0] if self.steps else None

    def next(self):
        if not self.steps:self.begin()
        if not self.steps:return None,False
        step=self.steps[self.index];self.index+=1
        committed=False
        if self.index==len(self.steps):
            self.cpu.step();self.steps=[];self.index=0;committed=True
        return step,committed

    def cancel(self):
        self.steps=[];self.index=0;self.start_pc=None
