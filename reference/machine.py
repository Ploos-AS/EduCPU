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

 def step(self) -> None:
  self.cpu.step()

 def run(self, limit: int = 100000) -> int:
  return self.cpu.run(limit)

def baseline_machine() -> ReferenceMachine:
 return ReferenceMachine(ISA_V0)

def experimental_machine() -> ReferenceMachine:
 return ReferenceMachine(M10_EXPERIMENTAL)
