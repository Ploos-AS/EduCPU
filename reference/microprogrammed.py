"""M10.3 experimental microprogrammed control model.

This module models *actual encoded microinstructions*.  It is intentionally
separate from experimental_microcode.py, whose plans are explanatory
micro-operations rather than a claim about implementation timing.
"""
from dataclasses import dataclass
from enum import IntEnum

class Source(IntEnum):
    NONE=0; PC=1; REG_A=2; REG_B=3; IMM=4; MEM=5; SP=6; ALU=7
class Destination(IntEnum):
    NONE=0; PC=1; REG_A=2; MEM=3; SP=4; IR=5; TMP=6; FLAGS=7
class ALU(IntEnum):
    PASS=0; ADD=1; SUB=2; AND=3; OR=4; XOR=5; NOT=6; SHL=7; SHR=8
class Next(IntEnum):
    STEP=0; FETCH=1; DISPATCH=2; HALT=3

@dataclass(frozen=True)
class MicroInstruction:
    source:Source=Source.NONE
    destination:Destination=Destination.NONE
    alu:ALU=ALU.PASS
    memory_read:bool=False
    memory_write:bool=False
    pc_increment:bool=False
    next:Next=Next.STEP

    def encode(self):
        """Encode the readable fields into a deterministic 24-bit control word."""
        word=int(self.source)
        word|=int(self.destination)<<3
        word|=int(self.alu)<<6
        word|=int(self.memory_read)<<10
        word|=int(self.memory_write)<<11
        word|=int(self.pc_increment)<<12
        word|=int(self.next)<<13
        return word

    @classmethod
    def decode(cls,word):
        if word<0 or word >= (1<<24): raise ValueError("control word must be 24-bit")
        return cls(Source(word&7),Destination((word>>3)&7),ALU((word>>6)&15),
                   bool(word&(1<<10)),bool(word&(1<<11)),bool(word&(1<<12)),
                   Next((word>>13)&3))

# Every instruction begins with the same visible fetch sequence.
FETCH=(
    MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
    MicroInstruction(Source.MEM,Destination.IR,pc_increment=True,next=Next.DISPATCH),
)

# First real microprograms.  More ISA families are added only after the
# control-word vocabulary is qualified.
CONTROL_STORE={
    "NOP": (MicroInstruction(next=Next.FETCH),),
    "HALT": (MicroInstruction(next=Next.HALT),),
}

def program_for(name):
    try:return CONTROL_STORE[name.upper()]
    except KeyError as e:raise KeyError(f"no microprogram for {name}") from e


OPCODE_NAMES={0x00:"NOP",0x01:"HALT"}

class MicroSequencer:
    """Step-visible controller for fetch/dispatch/control-store sequencing."""
    def __init__(self):
        self.phase="FETCH"
        self.micro_pc=0
        self.opcode=None
        self.halted=False

    def reset(self):
        self.phase="FETCH";self.micro_pc=0;self.opcode=None;self.halted=False

    def current(self):
        if self.halted:return None
        if self.phase=="FETCH":return FETCH[self.micro_pc]
        if self.phase=="EXECUTE":return program_for(OPCODE_NAMES[self.opcode])[self.micro_pc]
        raise RuntimeError(f"invalid sequencer phase {self.phase}")

    def step(self,ir=None):
        """Advance after the current microinstruction has completed.

        ir is required only when a DISPATCH microinstruction completes.
        """
        u=self.current()
        if u is None:return None
        before={"phase":self.phase,"micro_pc":self.micro_pc,"opcode":self.opcode}
        if u.next==Next.HALT:
            self.halted=True
        elif u.next==Next.FETCH:
            self.phase="FETCH";self.micro_pc=0;self.opcode=None
        elif u.next==Next.DISPATCH:
            if ir is None:raise ValueError("dispatch requires IR opcode")
            if ir not in OPCODE_NAMES:raise KeyError(f"no opcode dispatch for {ir:02X}")
            self.phase="EXECUTE";self.micro_pc=0;self.opcode=ir
        else:
            self.micro_pc+=1
        return {"before":before,"control_word":u.encode(),
                "after":{"phase":self.phase,"micro_pc":self.micro_pc,
                         "opcode":self.opcode,"halted":self.halted}}
