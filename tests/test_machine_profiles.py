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


def test_experimental_io_unmapped_reads_zero_and_writes_are_ignored():
 m=experimental_machine()
 assert m.in_port(0x42)==0
 m.out_port(0x42,0xaa)

def test_baseline_machine_rejects_experimental_io():
 import pytest
 m=baseline_machine()
 with pytest.raises(ValueError,match="does not support"):m.in_port(0)
 with pytest.raises(ValueError,match="does not support"):m.out_port(0,1)

def test_experimental_io_device_callbacks_and_byte_masking():
 m=experimental_machine(); written=[]
 m.register_io(0x142,read=lambda:0x1ab,write=lambda value:written.append(value))
 assert m.in_port(0x42)==0xab
 m.out_port(0x42,0x1cd)
 assert written==[0xcd]

def test_experimental_io_read_and_write_can_be_registered_independently():
 m=experimental_machine(); written=[]
 m.register_io(7,write=written.append)
 assert m.in_port(7)==0
 m.out_port(7,0x55)
 assert written==[0x55]


def test_experimental_in_instruction_reads_port_without_changing_flags():
 m=experimental_machine();m.cpu.flags=0x0d
 m.register_io(0x10,read=lambda:0xa5)
 m.cpu.mem[:4]=bytes((0xe0,2,0x10,0x01));m.run()
 assert m.cpu.r[2]==0xa5 and m.cpu.flags==0x0d and m.cpu.halted and m.cpu.trap is None

def test_experimental_out_instruction_writes_register_without_changing_flags():
 m=experimental_machine();written=[];m.cpu.r[3]=0x5a;m.cpu.flags=0x06
 m.register_io(0x20,write=written.append)
 m.cpu.mem[:4]=bytes((0xe1,0x20,3,0x01));m.run()
 assert written==[0x5a] and m.cpu.flags==0x06 and m.cpu.halted and m.cpu.trap is None

def test_experimental_unmapped_in_and_out_instructions_are_deterministic():
 m=experimental_machine();m.cpu.r[1]=0xff
 m.cpu.mem[:7]=bytes((0xe0,1,0x77,0xe1,0x78,1,0x01));m.run()
 assert m.cpu.r[1]==0 and m.cpu.halted and m.cpu.trap is None

def test_baseline_e0_e1_remain_invalid_opcodes():
 for opcode in (0xe0,0xe1):
  m=baseline_machine();m.cpu.mem[0]=opcode;m.step()
  assert m.cpu.trap=="INVALID_OPCODE"
