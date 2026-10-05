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
# MAR is an internal 16-bit address latch; address-byte assembly is deliberately
# explicit in MicroMachine rather than hidden in architectural registers.
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

    "LOAD": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.MEM,Destination.REG_A,memory_read=True,next=Next.FETCH),
    ),
    "STORE": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.REG_A,Destination.MEM,memory_write=True,next=Next.FETCH),
    ),    "LOADS": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.MEM,Destination.REG_A,memory_read=True,next=Next.FETCH),
    ),
    "STORES": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.REG_A,Destination.MEM,memory_write=True,next=Next.FETCH),
    ),
    "LOADR": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.MEM,Destination.REG_A,memory_read=True,next=Next.FETCH),
    ),
    "STORER": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.REG_A,Destination.MEM,memory_write=True,next=Next.FETCH),
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
    "ADDI": (
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
    "SUBI": (
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

    "CMPI": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.ALU,Destination.FLAGS,alu=ALU.SUB,next=Next.FETCH),
    ),
    "ENTER": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.SP,pc_increment=True,next=Next.FETCH),
    ),
    "LEAVE": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.SP,pc_increment=True,next=Next.FETCH),
    ),
    "CALL": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.PC,Destination.MEM,memory_write=True), MicroInstruction(Source.PC,Destination.MEM,memory_write=True),
        MicroInstruction(Source.NONE,Destination.PC,next=Next.FETCH),
    ),
    "RET": (
        MicroInstruction(Source.MEM,Destination.TMP,memory_read=True),
        MicroInstruction(Source.MEM,Destination.PC,memory_read=True,next=Next.FETCH),
    ),
    "PUSH": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.REG_A,Destination.MEM,memory_write=True,next=Next.FETCH),
    ),
    "POP": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True),
        MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.MEM,Destination.REG_A,memory_read=True,next=Next.FETCH),
    ),
    "JMP": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.PC,pc_increment=True,next=Next.FETCH),
    ),
    "JZ": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.PC,pc_increment=True,next=Next.FETCH),
    ),
    "JNZ": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.PC,pc_increment=True,next=Next.FETCH),
    ),
    "JC": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.PC,pc_increment=True,next=Next.FETCH),
    ),
    "JNC": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.PC,pc_increment=True,next=Next.FETCH),
    ),
    "JN": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.PC,pc_increment=True,next=Next.FETCH),
    ),
    "JP": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.PC,pc_increment=True,next=Next.FETCH),
    ),
    "AND": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.ALU,Destination.REG_A,alu=ALU.AND,next=Next.FETCH),
    ),
    "OR": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.ALU,Destination.REG_A,alu=ALU.OR,next=Next.FETCH),
    ),
    "XOR": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.NONE,pc_increment=True),
        MicroInstruction(Source.ALU,Destination.REG_A,alu=ALU.XOR,next=Next.FETCH),
    ),
    "NOT": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.ALU,Destination.REG_A,alu=ALU.NOT,next=Next.FETCH),
    ),
    "SHL": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.ALU,Destination.REG_A,alu=ALU.SHL,next=Next.FETCH),
    ),
    "SHR": (
        MicroInstruction(Source.PC,Destination.NONE,memory_read=True), MicroInstruction(Source.MEM,Destination.TMP,pc_increment=True),
        MicroInstruction(Source.ALU,Destination.REG_A,alu=ALU.SHR,next=Next.FETCH),
    ),}

def program_for(name):
    try:return CONTROL_STORE[name.upper()]
    except KeyError as e:raise KeyError(f"no microprogram for {name}") from e


OPCODE_NAMES={0x00:"NOP",0x01:"HALT",0x10:"MOV",0x11:"MOVI",0x12:"LOAD",0x13:"STORE",0x14:"LOADR",0x15:"STORER",0x16:"LOADS",0x17:"STORES",0x18:"ENTER",0x19:"LEAVE",0x38:"CALL",0x39:"RET",0x40:"PUSH",0x41:"POP",0x20:"ADD",0x21:"ADDI",0x22:"SUB",0x23:"SUBI",0x24:"CMP",0x25:"CMPI",0x30:"JMP",0x31:"JZ",0x32:"JNZ",0x33:"JC",0x34:"JNC",0x35:"JN",0x36:"JP",0x28:"AND",0x29:"OR",0x2a:"XOR",0x2b:"NOT",0x2c:"SHL",0x2d:"SHR"}

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
        self.r=[0]*8;self.pc=0;self.ir=0;self.tmp=0;self.mem_latch=0;self.flags=0;self.mar=0;self.addr_bytes=[];self.sp=0xFF00
        self.seq=MicroSequencer()

    def step_micro(self):
        u=self.seq.current()
        if u is None:return None
        # Source value is sampled before destinations are updated.
        src={Source.NONE:0,Source.PC:self.pc,Source.MEM:self.mem_latch,
             Source.TMP if hasattr(Source,"TMP") else Source.NONE:0}.get(u.source,0)
        # During LOAD/STORE operand fetch, remember the two little-endian
        # address bytes. The final data access uses MAR rather than PC.
        data_access=self.seq.phase=="EXECUTE" and ((self.seq.opcode in (0x12,0x13) and self.seq.micro_pc==6) or (self.seq.opcode in (0x14,0x15,0x16,0x17) and self.seq.micro_pc==4) or (self.seq.opcode==0x41 and self.seq.micro_pc==2) or (self.seq.opcode==0x39 and self.seq.micro_pc in (0,1)))
        if u.memory_read:
            if self.seq.phase=="EXECUTE" and ((self.seq.opcode==0x41 and self.seq.micro_pc==2) or self.seq.opcode==0x39):self.mar=self.sp
            address=self.mar if data_access else self.pc
            self.mem_latch=self.mem[address&0xffff]
        capture_steps={0x12:(3,5),0x13:(1,3),0x30:(1,3),0x31:(1,3),0x32:(1,3),0x33:(1,3),0x34:(1,3),0x35:(1,3),0x36:(1,3)}
        if self.seq.phase=="EXECUTE" and self.seq.opcode in capture_steps and self.seq.micro_pc in capture_steps[self.seq.opcode]:
            self.addr_bytes.append(self.mem_latch)
            if len(self.addr_bytes)==2:self.mar=self.addr_bytes[0]|(self.addr_bytes[1]<<8)
        stack_offset_step={0x16:3,0x17:1}
        if self.seq.phase=="EXECUTE" and self.seq.opcode in stack_offset_step and self.seq.micro_pc==stack_offset_step[self.seq.opcode]:
            off=self.mem_latch if self.mem_latch<0x80 else self.mem_latch-0x100
            self.mar=(self.sp+off)&0xffff
        register_address_step={0x14:3,0x15:1}
        if self.seq.phase=="EXECUTE" and self.seq.opcode in register_address_step and self.seq.micro_pc==register_address_step[self.seq.opcode]:
            if not 0<=self.mem_latch<=7:raise ValueError("INVALID_OPERAND")
            self.mar=self.r[self.mem_latch]
        if self.seq.phase=="EXECUTE" and self.seq.opcode==0x38 and self.seq.micro_pc in (4,5):
            # addr_bytes holds CALL's little-endian target; PC already points
            # at the sequential return address after operand fetch.
            target=self.addr_bytes[0]|(self.addr_bytes[1]<<8)
            self.sp=(self.sp-1)&0xffff;self.mar=self.sp
            ret=self.pc&0xffff;src=((ret>>8)&0xff) if self.seq.micro_pc==4 else (ret&0xff)
            if self.seq.micro_pc==5:self.mar=self.sp
        if self.seq.phase=="EXECUTE" and self.seq.opcode==0x40 and self.seq.micro_pc==2:
            if not 0<=self.tmp<=7:raise ValueError("INVALID_OPERAND")
            self.sp=(self.sp-1)&0xffff;self.mar=self.sp
        if u.source==Source.MEM:src=self.mem_latch
        elif u.source==Source.REG_A:
            if not 0<=self.mem_latch<=7:raise ValueError("INVALID_OPERAND")
            src=self.r[self.mem_latch]
        elif u.source==Source.REG_B:
            if not 0<=self.mem_latch<=7:raise ValueError("INVALID_OPERAND")
            src=self.r[self.mem_latch]
        elif u.source==Source.ALU:
            if not 0<=self.tmp<=7 or not 0<=self.mem_latch<=7:raise ValueError("INVALID_OPERAND")
            a=self.r[self.tmp];b=self.mem_latch if self.seq.opcode in (0x21,0x23,0x25) else self.r[self.mem_latch]
            if u.alu==ALU.ADD:
                total=a+b;src=total&0xff
                self.flags=(1 if src==0 else 0)|(2 if src&0x80 else 0)|(4 if total>0xff else 0)|(8 if (~(a^b)&(a^src)&0x80) else 0)
            elif u.alu==ALU.SUB:
                src=(a-b)&0xff
                self.flags=(1 if src==0 else 0)|(2 if src&0x80 else 0)|(4 if a>=b else 0)|(8 if ((a^b)&(a^src)&0x80) else 0)
            elif u.alu in (ALU.AND,ALU.OR,ALU.XOR):
                src={ALU.AND:a&b,ALU.OR:a|b,ALU.XOR:a^b}[u.alu]
                self.flags=(1 if src==0 else 0)|(2 if src&0x80 else 0)
            elif u.alu==ALU.NOT:
                src=(~a)&0xff;self.flags=(1 if src==0 else 0)|(2 if src&0x80 else 0)
            elif u.alu==ALU.SHL:
                src=(a<<1)&0xff;self.flags=(1 if src==0 else 0)|(2 if src&0x80 else 0)|(4 if a&0x80 else 0)
            elif u.alu==ALU.SHR:
                src=a>>1;self.flags=(1 if src==0 else 0)|(2 if src&0x80 else 0)|(4 if a&1 else 0)
            else:raise NotImplementedError(f"ALU operation {u.alu.name}")
        if u.destination==Destination.PC and self.seq.opcode==0x39:
            self.pc=(self.tmp&0xff)|((self.mem_latch&0xff)<<8)
        elif u.destination==Destination.PC and self.seq.opcode==0x38:
            self.pc=(self.addr_bytes[0]|(self.addr_bytes[1]<<8))&0xffff
        elif u.destination==Destination.PC:
            # The final target byte is itself an instruction operand: consume it
            # before choosing target vs sequential PC.
            sequential=(self.pc+1)&0xffff if u.pc_increment else self.pc
            take={0x30:True,0x31:bool(self.flags&1),0x32:not bool(self.flags&1),0x33:bool(self.flags&4),0x34:not bool(self.flags&4),0x35:bool(self.flags&2),0x36:not bool(self.flags&2)}.get(self.seq.opcode,True)
            self.pc=(self.mar&0xffff) if take else sequential
        if u.destination==Destination.IR:self.ir=src&0xff
        elif u.destination==Destination.TMP:self.tmp=src&0xff
        elif u.destination==Destination.REG_A:
            if not 0<=self.tmp<=7:raise ValueError("INVALID_OPERAND")
            self.r[self.tmp]=src&0xff
        elif u.destination==Destination.SP:
            if self.seq.opcode==0x18:self.sp=(self.sp-src)&0xffff
            elif self.seq.opcode==0x19:self.sp=(self.sp+src)&0xffff
        elif u.destination==Destination.FLAGS:
            pass  # ALU already committed flags; result is intentionally discarded
        elif u.destination==Destination.MEM and u.memory_write:
            self.mem[self.mar&0xffff]=src&0xff
        if self.seq.phase=="EXECUTE" and self.seq.opcode==0x41 and self.seq.micro_pc==2:self.sp=(self.sp+1)&0xffff
        if self.seq.phase=="EXECUTE" and self.seq.opcode==0x39 and self.seq.micro_pc in (0,1):self.sp=(self.sp+1)&0xffff
        if u.pc_increment and u.destination!=Destination.PC:self.pc=(self.pc+1)&0xffff
        if u.next==Next.FETCH and self.seq.phase=="EXECUTE":self.addr_bytes=[]
        event=self.seq.step(ir=self.ir if u.next==Next.DISPATCH else None)
        event.update({"pc":self.pc,"ir":self.ir,"tmp":self.tmp,"flags":self.flags,"mar":self.mar,"sp":self.sp,"registers":self.r.copy()})
        return event
