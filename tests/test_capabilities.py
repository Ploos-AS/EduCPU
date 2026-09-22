import pytest
from capabilities import ISA_V0,KNOWN_EXPERIMENTAL_CAPABILITIES,M10_EXPERIMENTAL,machine_profile

def test_isa_v0_has_no_experimental_capabilities():
 assert ISA_V0.capabilities==frozenset()
 for capability in KNOWN_EXPERIMENTAL_CAPABILITIES:assert not ISA_V0.supports(capability)

def test_experimental_profile_advertises_named_capabilities():
 assert M10_EXPERIMENTAL.capabilities==KNOWN_EXPERIMENTAL_CAPABILITIES
 assert M10_EXPERIMENTAL.supports("experimental.interrupts")

def test_require_rejects_unsupported_capability():
 with pytest.raises(ValueError,match="does not support"):ISA_V0.require("experimental.interrupts")

def test_profile_lookup_is_explicit():
 assert machine_profile("isa-v0") is ISA_V0
 assert machine_profile("experimental") is M10_EXPERIMENTAL
 with pytest.raises(ValueError,match="unknown EduCPU machine profile"):machine_profile("future")
