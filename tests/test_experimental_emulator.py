from experimental import ExperimentalEmulator


def test_emulator_irq_entry_and_iret():
    m=ExperimentalEmulator()
    m.cpu.pc=0x1234
    m.cpu.flags=0x05
    m.irq_vector=0x8000
    m.cpu.mem[0x8000]=0xF0
    m.request_irq()
    m.step()
    assert m.in_interrupt and m.cpu.pc==0x8000 and not m.irq_enabled
    m.step()
    assert not m.in_interrupt and m.irq_enabled
    assert m.cpu.pc==0x1234 and m.cpu.flags==0x05


def test_emulator_irq_wakes_halt():
    m=ExperimentalEmulator()
    m.cpu.halted=True
    m.cpu.pc=0x0042
    m.irq_vector=0x9000
    m.request_irq()
    m.step()
    assert m.cpu.pc==0x9000 and not m.cpu.halted and m.in_interrupt


def test_emulator_nested_irq_is_pending():
    m=ExperimentalEmulator()
    m.irq_vector=0x8000
    m.cpu.mem[0x8000]=0xF0
    m.cpu.pc=0x1234
    m.request_irq()
    m.step()
    m.request_irq()
    # Execute a normal handler instruction while the nested request is deferred.
    m.cpu.mem[0x8000]=0x00
    m.cpu.mem[0x8001]=0xF0
    m.step()
    assert m.irq_pending and m.in_interrupt and m.cpu.pc==0x8001


def test_experimental_emulator_io_defaults_and_callbacks():
 e=ExperimentalEmulator(); written=[]
 assert e.in_port(0x42)==0
 e.out_port(0x42,0xaa)
 e.register_io(0x142,read=lambda:0x1ab,write=lambda value:written.append(value))
 assert e.in_port(0x42)==0xab
 e.out_port(0x42,0x1cd)
 assert written==[0xcd]

def test_experimental_emulator_io_registration_survives_cpu_reset():
 e=ExperimentalEmulator(); e.register_io(7,read=lambda:0x5a)
 e.reset()
 assert e.in_port(7)==0x5a


def test_experimental_emulator_executes_in_out_instructions():
 e=ExperimentalEmulator();written=[];e.cpu.flags=0x0d
 e.register_io(0x10,read=lambda:0xa5)
 e.register_io(0x20,write=written.append)
 e.cpu.mem[:7]=bytes((0xe0,2,0x10,0xe1,0x20,2,0x01));e.run()
 assert e.cpu.r[2]==0xa5 and written==[0xa5]
 assert e.cpu.flags==0x0d and e.cpu.pc==7 and e.cpu.halted and e.cpu.trap is None

def test_reference_and_emulator_io_instruction_semantics_match():
 from machine import experimental_machine
 program=bytes((0xe0,2,0x10,0xe1,0x20,2,0xe0,4,0x77,0xe1,0x78,4,0x01))
 ref=experimental_machine();emu=ExperimentalEmulator()
 ref_writes=[];emu_writes=[]
 ref.register_io(0x10,read=lambda:0xa5);ref.register_io(0x20,write=ref_writes.append)
 emu.register_io(0x10,read=lambda:0xa5);emu.register_io(0x20,write=emu_writes.append)
 ref.cpu.flags=emu.cpu.flags=0x0d
 ref.cpu.mem[:len(program)]=program;emu.cpu.mem[:len(program)]=program
 ref.run();emu.run()
 assert emu.cpu.r==ref.cpu.r
 assert emu.cpu.pc==ref.cpu.pc
 assert emu.cpu.sp==ref.cpu.sp
 assert emu.cpu.flags==ref.cpu.flags
 assert emu.cpu.halted==ref.cpu.halted
 assert emu.cpu.trap==ref.cpu.trap
 assert emu_writes==ref_writes==[0xa5]


def test_reference_and_emulator_expose_same_io_transaction():
 from machine import experimental_machine
 ref=experimental_machine();emu=ExperimentalEmulator()
 ref.register_io(0x10,read=lambda:0xa5);emu.register_io(0x10,read=lambda:0xa5)
 program=bytes((0xe0,2,0x10))
 ref.cpu.mem[:3]=program;emu.cpu.mem[:3]=program
 ref.step();emu.step()
 assert emu.last_io==ref.last_io=={"direction":"in","port":0x10,"value":0xa5,"mapped":True}
 ref.out_port(0x77,0x1ff);emu.out_port(0x77,0x1ff)
 assert emu.last_io==ref.last_io=={"direction":"out","port":0x77,"value":0xff,"mapped":False}
 emu.reset()
 assert emu.last_io is None
