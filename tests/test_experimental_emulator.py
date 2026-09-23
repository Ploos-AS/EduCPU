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
    m.step()
    assert m.irq_pending and m.in_interrupt
