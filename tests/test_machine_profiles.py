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


def test_experimental_irq_entry_saves_pc_flags_and_vectors():
 m=experimental_machine();m.cpu.pc=0x1234;m.cpu.flags=0x05;m.irq_vector=0x8000;m.request_irq();m.step()
 assert m.cpu.pc==0x8000
 assert m.in_interrupt and not m.irq_enabled and not m.irq_pending
 assert m.cpu.sp==0xfefd
 assert list(m.cpu.mem[0xfefd:0xff00])==[0x05,0x34,0x12]

def test_disabled_irq_stays_pending_without_cpu_control_transfer():
 m=experimental_machine();m.irq_enabled=False;m.irq_vector=0x8000;m.request_irq();m.step()
 assert m.irq_pending and m.cpu.pc==1 and not m.in_interrupt

def test_irq_wakes_halted_experimental_machine():
 m=experimental_machine();m.cpu.halted=True;m.cpu.pc=0x0042;m.irq_vector=0x9000;m.request_irq();m.step()
 assert not m.cpu.halted and m.cpu.pc==0x9000 and m.in_interrupt

def test_baseline_machine_rejects_irq_requests():
 import pytest
 m=baseline_machine()
 with pytest.raises(ValueError,match="does not support"):m.request_irq()


def test_iret_restores_flags_pc_and_irq_state():
 m=experimental_machine();m.cpu.pc=0x1234;m.cpu.flags=0x05;m.irq_vector=0x8000;m.cpu.mem[0x8000]=0xf0;m.request_irq();m.step();m.step()
 assert m.cpu.pc==0x1234 and m.cpu.flags==0x05
 assert not m.in_interrupt and m.irq_enabled and m.cpu.sp==0xff00

def test_baseline_0xf0_remains_invalid_opcode():
 m=baseline_machine();m.cpu.mem[0]=0xf0;m.step()
 assert m.cpu.trap=="INVALID_OPCODE"

def test_iret_outside_interrupt_traps_in_experimental_profile():
 m=experimental_machine();m.cpu.mem[0]=0xf0;m.step()
 # Outside interrupt context 0xf0 remains unavailable to normal execution.
 assert m.cpu.trap=="INVALID_OPCODE"


def test_trapped_cpu_does_not_accept_pending_irq():
 m=experimental_machine();m.cpu.pc=0x1234;m.cpu.trap="TEST_TRAP";m.irq_vector=0x8000;m.request_irq();m.step()
 assert m.cpu.pc==0x1234 and m.cpu.trap=="TEST_TRAP"
 assert m.irq_pending and not m.in_interrupt

def test_nested_irq_is_deferred_until_iret():
 m=experimental_machine();m.cpu.pc=0x1234;m.irq_vector=0x8000;m.cpu.mem[0x8000]=0x00;m.cpu.mem[0x8001]=0xf0
 m.request_irq();m.step()
 assert m.in_interrupt and not m.irq_enabled and m.cpu.pc==0x8000
 m.request_irq();m.step()
 assert m.irq_pending and m.cpu.pc==0x8001 and m.in_interrupt
 m.step()
 assert m.cpu.pc==0x1234 and m.irq_enabled and not m.in_interrupt and m.irq_pending
 m.step()
 assert m.cpu.pc==0x8000 and m.in_interrupt and not m.irq_pending
