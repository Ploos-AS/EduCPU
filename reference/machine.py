"""EduCPU reference-machine profiles.

Profiles wrap the frozen ISA v0 CPU with explicit capability metadata. M10
experiments can extend this boundary without silently changing CPU semantics.
"""
from dataclasses import dataclass, field
from capabilities import ISA_V0, M10_EXPERIMENTAL, MachineProfile, machine_profile
from educpu import CPU

@dataclass
class ReferenceMachine:
 profile: MachineProfile = ISA_V0
 cpu: CPU = field(default_factory=CPU)
 irq_pending: bool = False
 irq_enabled: bool = True
 irq_vector: int = 0
 in_interrupt: bool = False
 io_readers: dict = field(default_factory=dict)
 io_writers: dict = field(default_factory=dict)
 last_io: dict | None = None

 @classmethod
 def named(cls, name: str) -> "ReferenceMachine":
  return cls(profile=machine_profile(name))

 @property
 def capabilities(self) -> frozenset[str]:
  return self.profile.capabilities

 def supports(self, capability: str) -> bool:
  return self.profile.supports(capability)

 def reset(self) -> None:
  self.cpu.reset()
  self.irq_pending=False
  self.irq_enabled=True
  self.in_interrupt=False
  self.last_io=None

 def register_io(self, port: int, read=None, write=None) -> None:
  self.profile.require("experimental.io")
  port &= 0xff
  if read is not None: self.io_readers[port]=read
  if write is not None: self.io_writers[port]=write

 def in_port(self, port: int) -> int:
  self.profile.require("experimental.io")
  port&=0xff;reader=self.io_readers.get(port);value=(reader()&0xff) if reader else 0
  self.last_io={"direction":"in","port":port,"value":value,"mapped":reader is not None}
  return value

 def out_port(self, port: int, value: int) -> None:
  self.profile.require("experimental.io")
  port&=0xff;value&=0xff;writer=self.io_writers.get(port)
  self.last_io={"direction":"out","port":port,"value":value,"mapped":writer is not None}
  if writer: writer(value)

 def request_irq(self) -> None:
  self.profile.require("experimental.interrupts")
  self.irq_pending=True

 def _accept_irq(self) -> bool:
  if not self.supports("experimental.interrupts") or not self.irq_pending or not self.irq_enabled or self.cpu.trap or self.in_interrupt:
   return False
  self.irq_pending=False
  self.cpu.halted=False
  pc=self.cpu.pc
  self.cpu.push((pc>>8)&0xff)
  self.cpu.push(pc&0xff)
  self.cpu.push(self.cpu.flags)
  self.in_interrupt=True
  self.irq_enabled=False
  self.cpu.pc=self.irq_vector&0xffff
  return True

 def _iret(self) -> None:
  self.profile.require("experimental.interrupts")
  if not self.in_interrupt:
   self.cpu.trap="INVALID_IRET"
   return
  self.cpu.flags=self.cpu.pop()
  lo=self.cpu.pop();hi=self.cpu.pop()
  self.cpu.pc=lo|(hi<<8)
  self.in_interrupt=False
  self.irq_enabled=True

 def _io_instruction(self) -> bool:
  if not self.supports("experimental.io"): return False
  op=self.cpu.mem[self.cpu.pc]
  if op not in (0xe0,0xe1): return False
  self.cpu.pc=(self.cpu.pc+1)&0xffff
  try:
   if op==0xe0:
    d=self.cpu.reg();port=self.cpu.fetch();self.cpu.r[d]=self.in_port(port)
   else:
    port=self.cpu.fetch();s=self.cpu.reg();self.out_port(port,self.cpu.r[s])
  except ValueError:
   pass
  return True

 def step(self) -> None:
  if self._accept_irq(): return
  if self._io_instruction(): return
  if self.supports("experimental.interrupts") and self.in_interrupt and self.cpu.mem[self.cpu.pc]==0xf0:
   self.cpu.pc=(self.cpu.pc+1)&0xffff
   self._iret();return
  self.cpu.step()

 def run(self, limit: int = 100000) -> int:
  n=0
  while n<limit and not self.cpu.trap:
   if self.cpu.halted and not (self.irq_pending and self.irq_enabled and not self.in_interrupt): break
   self.step();n+=1
   if self.cpu.halted and not self.irq_pending: break
  return n

def baseline_machine() -> ReferenceMachine:
 return ReferenceMachine(ISA_V0)

def experimental_machine() -> ReferenceMachine:
 return ReferenceMachine(M10_EXPERIMENTAL)
