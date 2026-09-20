from educpu import CPU
from eduemu import Emulator


def state(cpu):
    return {
        "r": list(cpu.r),
        "pc": cpu.pc,
        "sp": cpu.sp,
        "flags": cpu.flags,
        "halted": cpu.halted,
        "trap": cpu.trap,
    }


def machines(program):
    reference = CPU()
    emulator = Emulator()
    reference.mem[:len(program)] = program
    emulator.mem[:len(program)] = program
    return reference, emulator


def test_emulator_reset_matches_reference():
    reference, emulator = machines(b"")
    reference.r[3] = emulator.r[3] = 0xAA
    reference.pc = emulator.pc = 0x1234
    reference.sp = emulator.sp = 0x2222
    reference.flags = emulator.flags = 0x0F
    reference.halted = emulator.halted = True
    reference.trap = emulator.trap = "TEST"
    reference.reset()
    emulator.reset()
    assert state(emulator) == state(reference)


def test_nop_halt_differential():
    reference, emulator = machines(bytes([0x00, 0x01]))
    reference.run()
    emulator.run()
    assert state(emulator) == state(reference)
    assert emulator.pc == 2
    assert emulator.halted


def test_invalid_opcode_differential():
    reference, emulator = machines(bytes([0xFE]))
    reference.step()
    emulator.step()
    assert state(emulator) == state(reference)
    assert emulator.trap == "INVALID_OPCODE"
    assert emulator.pc == 1


def test_invalid_register_operand_differential():
    # MOV R8,R0: the first register byte is architecturally invalid.
    reference, emulator = machines(bytes([0x10, 0x08, 0x00]))
    reference.step()
    emulator.step()
    assert state(emulator) == state(reference)
    assert emulator.trap == "INVALID_OPERAND"
    assert emulator.pc == 2


def test_step_after_halt_or_trap_is_stable():
    for program in (bytes([0x01]), bytes([0xFE])):
        reference, emulator = machines(program)
        reference.step()
        emulator.step()
        before = state(emulator)
        reference.step()
        emulator.step()
        assert state(emulator) == before
        assert state(emulator) == state(reference)
