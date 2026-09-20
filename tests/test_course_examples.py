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
