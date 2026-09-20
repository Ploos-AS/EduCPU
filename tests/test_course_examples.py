from pathlib import Path

from eduasm import assemble_text
from educpu import CPU

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "course" / "examples" / "lesson01-number-formats.eduasm"


def test_lesson01_number_formats_assemble_identically():
    data, _, rows = assemble_text(FIXTURE.read_text())
    # MOVI is opcode, register, immediate. All three immediate bytes must be 0x2A.
    assert data == bytes([
        0x11, 0x00, 0x2A,
        0x11, 0x01, 0x2A,
        0x11, 0x02, 0x2A,
        0x01,
    ])
    assert [row[1][-1] for row in rows[:3]] == [0x2A, 0x2A, 0x2A]


def test_lesson01_number_formats_execute_as_same_value():
    data, _, _ = assemble_text(FIXTURE.read_text())
    cpu = CPU()
    cpu.mem[:len(data)] = data
    cpu.run()
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.r[:3] == [42, 42, 42]


def test_lesson02_logic_fixture():
    source = ROOT / "course" / "examples" / "lesson02-logic.eduasm"
    data, _, _ = assemble_text(source.read_text())
    cpu = CPU()
    cpu.mem[:len(data)] = data
    cpu.run()
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.r[0] == 0xCC
    assert cpu.r[1] == 0xAA
    assert cpu.r[2] == 0x88  # AND
    assert cpu.r[3] == 0xEE  # OR
    assert cpu.r[4] == 0x66  # XOR
    assert cpu.r[5] == 0x33  # NOT


def test_lesson03_cpu_cycle_fixture():
    source = ROOT / "course" / "examples" / "lesson03-cpu-cycle.eduasm"
    data, _, _ = assemble_text(source.read_text())
    cpu = CPU()
    cpu.mem[:len(data)] = data
    cpu.run()
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.r[0] == 30
    assert cpu.r[1] == 20
    assert cpu.pc == len(data)
    assert cpu.flags == 0


def test_lesson04_machine_state_step_by_step():
    source = ROOT / "course" / "examples" / "lesson04-machine-state.eduasm"
    data, _, _ = assemble_text(source.read_text())
    cpu = CPU()
    cpu.mem[:len(data)] = data

    assert (cpu.r[0], cpu.r[1], cpu.pc, cpu.sp, cpu.flags) == (0, 0, 0, 0xFF00, 0)
    cpu.step()
    assert (cpu.r[0], cpu.pc, cpu.flags) == (5, 3, 0)
    cpu.step()
    assert (cpu.r[1], cpu.pc, cpu.flags) == (5, 6, 0)
    cpu.step()
    assert cpu.r[0] == 0
    assert cpu.pc == 9
    assert cpu.flags == (CPU.Z | CPU.C)
    assert cpu.sp == 0xFF00
    cpu.step()
    assert cpu.halted
    assert cpu.pc == len(data)


def test_lesson05_exact_machine_code():
    source = ROOT / "course" / "examples" / "lesson05-machine-code.eduasm"
    data, _, rows = assemble_text(source.read_text())
    assert data == bytes([
        0x11, 0x00, 0x2A,
        0x11, 0x01, 0x01,
        0x20, 0x00, 0x01,
        0x01,
    ])
    assert [(pc, len(encoded)) for pc, encoded, _, _ in rows] == [
        (0x0000, 3), (0x0003, 3), (0x0006, 3), (0x0009, 1)
    ]


def test_lesson05_little_endian_address_encoding():
    data, _, _ = assemble_text("JMP 0x1234\n")
    assert data == bytes([0x30, 0x34, 0x12])
