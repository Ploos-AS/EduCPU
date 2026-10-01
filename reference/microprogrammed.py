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
    # MOVI uses TMP first as the register selector and then as the immediate
    # transfer latch. The executable datapath model below makes these two
    # operand-fetch steps visible.
    "MOVI": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.REG_A,pc_increment=True,next=Next.FETCH),
    ),
    "MOV": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.REG_B,Destination.REG_A,next=Next.FETCH),
    ),
    "ADD": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.ALU,Destination.REG_A,alu=ALU.ADD,next=Next.FETCH),
    ),
    "SUB": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.ALU,Destination.REG_A,alu=ALU.SUB,next=Next.FETCH),
    ),
    "CMP": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.ALU,Destination.FLAGS,alu=ALU.SUB,next=Next.FETCH),
    ),
}

def program_for(name):
    try:return CONTROL_STORE[name.upper()]
    except KeyError as e:raise KeyError(f"no microprogram for {name}") from e


OPCODE_NAMES={0x00:"NOP",0x01:"HALT",0x10:"MOV",0x11:"MOVI",0x20:"ADD",0x22:"SUB",0x24:"CMP"}

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


class MicroMachine:
    """Small executable datapath for qualified microprograms."""
    def __init__(self,memory=b""):
        self.mem=bytearray(65536);self.mem[:len(memory)]=memory
        self.r=[0]*8;self.pc=0;self.ir=0;self.tmp=0;self.mem_latch=0;self.flags=0
        self.seq=MicroSequencer()

    def step_micro(self):
        u=self.seq.current()
        if u is None:return None
        # Source value is sampled before destinations are updated.
        src={Source.NONE:0,Source.PC:self.pc,Source.MEM:self.mem_latch,
             Source.TMP if hasattr(Source,"TMP") else Source.NONE:0}.get(u.source,0)
        # A memory read is an explicit request whose result becomes MEM.
        if u.memory_read:self.mem_latch=self.mem[self.pc&0xffff]
        if u.source==Source.MEM:src=self.mem_latch
        elif u.source==Source.REG_B:
            if not 0<=self.mem_latch<=7:raise ValueError("INVALID_OPERAND")
            src=self.r[self.mem_latch]
        elif u.source==Source.ALU:
            if not 0<=self.tmp<=7 or not 0<=self.mem_latch<=7:raise ValueError("INVALID_OPERAND")
            a=self.r[self.tmp];b=self.r[self.mem_latch]
            if u.alu==ALU.ADD:
                total=a+b;src=total&0xff
                self.flags=(1 if src==0 else 0)|(2 if src&0x80 else 0)|(4 if total>0xff else 0)|(8 if (~(a^b)&(a^src)&0x80) else 0)
            elif u.alu==ALU.SUB:
                src=(a-b)&0xff
                self.flags=(1 if src==0 else 0)|(2 if src&0x80 else 0)|(4 if a>=b else 0)|(8 if ((a^b)&(a^src)&0x80) else 0)
            else:raise NotImplementedError(f"ALU operation {u.alu.name}")
        if u.destination==Destination.IR:self.ir=src&0xff
        elif u.destination==Destination.TMP:self.tmp=src&0xff
        elif u.destination==Destination.REG_A:
            if not 0<=self.tmp<=7:raise ValueError("INVALID_OPERAND")
            self.r[self.tmp]=src&0xff
        elif u.destination==Destination.FLAGS:
            pass  # ALU already committed flags; result is intentionally discarded
        if u.pc_increment:self.pc=(self.pc+1)&0xffff
        event=self.seq.step(ir=self.ir if u.next==Next.DISPATCH else None)
        event.update({"pc":self.pc,"ir":self.ir,"tmp":self.tmp,"flags":self.flags,"registers":self.r.copy()})
        return event
