"""EduCPU machine-profile capability discovery."""
from dataclasses import dataclass

KNOWN_EXPERIMENTAL_CAPABILITIES=frozenset({
 "experimental.interrupts","experimental.io","experimental.microcode",
 "experimental.privilege","experimental.vm","experimental.pipeline","experimental.cache",
})

@dataclass(frozen=True)
class MachineProfile:
 name:str
 capabilities:frozenset[str]=frozenset()
 def supports(self,capability:str)->bool:return capability in self.capabilities
 def require(self,capability:str)->None:
  if not self.supports(capability):
   raise ValueError(f"machine profile {self.name!r} does not support {capability!r}")

ISA_V0=MachineProfile("isa-v0")
M10_EXPERIMENTAL=MachineProfile("experimental",KNOWN_EXPERIMENTAL_CAPABILITIES)

def machine_profile(name:str)->MachineProfile:
 profiles={ISA_V0.name:ISA_V0,M10_EXPERIMENTAL.name:M10_EXPERIMENTAL}
 try:return profiles[name]
 except KeyError as exc:raise ValueError(f"unknown EduCPU machine profile: {name!r}") from exc
