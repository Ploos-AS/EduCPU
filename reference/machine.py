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

 def step(self) -> None:
  if not self._accept_irq(): self.cpu.step()

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
