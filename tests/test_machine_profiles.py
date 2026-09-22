from machine import ReferenceMachine, baseline_machine, experimental_machine

PROGRAM=bytes((0x11,0x00,0x2a,0x01))  # MOVI R0,42; HALT

def _run(machine):
 machine.cpu.mem[:len(PROGRAM)]=PROGRAM
 machine.run()
 return machine.cpu.r[0],machine.cpu.pc,machine.cpu.halted,machine.cpu.trap

def test_default_machine_is_frozen_isa_v0():
 m=ReferenceMachine()
 assert m.profile.name=="isa-v0"
 assert m.capabilities==frozenset()

def test_experimental_machine_is_explicit():
 m=experimental_machine()
 assert m.profile.name=="experimental"
 assert m.supports("experimental.interrupts")

def test_profile_does_not_change_baseline_execution_semantics():
 assert _run(baseline_machine())==_run(experimental_machine())==(42,4,True,None)

def test_named_profile_factory():
 assert ReferenceMachine.named("isa-v0").profile.name=="isa-v0"
 assert ReferenceMachine.named("experimental").profile.name=="experimental"
