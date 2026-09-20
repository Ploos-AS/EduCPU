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


def assert_differential(program, setup=None, memory_addresses=()):
    reference, emulator = machines(program)
    if setup:
        setup(reference)
        setup(emulator)
    reference.run()
    emulator.run()
    assert state(emulator) == state(reference)
    for address in memory_addresses:
        assert emulator.mem[address] == reference.mem[address]


def test_mov_and_movi_differential():
    assert_differential(bytes([
        0x11, 0x01, 0xA5,       # MOVI R1,0xA5
        0x10, 0x02, 0x01,       # MOV R2,R1
        0x01,
    ]))


def test_absolute_load_store_differential():
    assert_differential(bytes([
        0x11, 0x03, 0x5A,
        0x13, 0x34, 0x12, 0x03, # STORE [0x1234],R3
        0x12, 0x04, 0x34, 0x12, # LOAD R4,[0x1234]
        0x01,
    ]), memory_addresses=(0x1234,))


def test_register_indirect_load_store_differential():
    assert_differential(bytes([
        0x11, 0x00, 0x80,       # address in page zero
        0x11, 0x01, 0xCC,
        0x15, 0x00, 0x01,       # STORER [R0],R1
        0x14, 0x02, 0x00,       # LOADR R2,[R0]
        0x01,
    ]), memory_addresses=(0x0080,))


def test_sp_relative_load_store_positive_and_negative_offsets():
    def setup(cpu):
        cpu.sp = 0x9000

    assert_differential(bytes([
        0x11, 0x01, 0x12,
        0x17, 0x05, 0x01,       # STORES [SP+5],R1
        0x16, 0x02, 0x05,       # LOADS R2,[SP+5]
        0x11, 0x03, 0x34,
        0x17, 0xFE, 0x03,       # STORES [SP-2],R3
        0x16, 0x04, 0xFE,       # LOADS R4,[SP-2]
        0x01,
    ]), setup=setup, memory_addresses=(0x9005, 0x8FFE))


def test_data_movement_preserves_flags():
    def setup(cpu):
        cpu.flags = cpu.Z | cpu.N | cpu.C | cpu.V

    assert_differential(bytes([
        0x11, 0x00, 0x20,
        0x11, 0x01, 0x7E,
        0x15, 0x00, 0x01,
        0x14, 0x02, 0x00,
        0x01,
    ]), setup=setup, memory_addresses=(0x20,))


def test_invalid_second_register_operand_differential():
    reference, emulator = machines(bytes([0x10, 0x00, 0x08]))
    reference.step()
    emulator.step()
    assert state(emulator) == state(reference)
    assert emulator.trap == "INVALID_OPERAND"
    assert emulator.pc == 3


def test_add_and_addi_flags_differential():
    assert_differential(bytes([
        0x11, 0x00, 0x7F,
        0x21, 0x00, 0x01,       # signed overflow: 0x7f + 1
        0x11, 0x01, 0xFF,
        0x21, 0x01, 0x01,       # carry + zero
        0x20, 0x00, 0x01,
        0x01,
    ]))


def test_sub_subi_cmp_cmpi_flags_differential():
    assert_differential(bytes([
        0x11, 0x00, 0x80,
        0x23, 0x00, 0x01,
        0x11, 0x01, 0x01,
        0x22, 0x01, 0x00,
        0x24, 0x00, 0x01,
        0x25, 0x00, 0x7F,
        0x01,
    ]))


def test_logic_and_not_flags_differential():
    assert_differential(bytes([
        0x11, 0x00, 0xF0,
        0x11, 0x01, 0x0F,
        0x28, 0x00, 0x01,
        0x29, 0x00, 0x01,
        0x2A, 0x00, 0x01,
        0x2B, 0x00,
        0x01,
    ]))


def test_shift_carry_zero_and_negative_differential():
    assert_differential(bytes([
        0x11, 0x00, 0x80,
        0x2C, 0x00,             # SHL: carry=1, zero=1
        0x11, 0x01, 0x01,
        0x2D, 0x01,             # SHR: carry=1, zero=1
        0x11, 0x02, 0x40,
        0x2C, 0x02,             # result 0x80, negative=1
        0x01,
    ]))


def test_alu_invalid_register_operand_differential():
    for program in (
        bytes([0x20, 0x08, 0x00]),
        bytes([0x20, 0x00, 0x08]),
        bytes([0x21, 0x08, 0x01]),
        bytes([0x2B, 0x08]),
        bytes([0x2C, 0x08]),
    ):
        reference, emulator = machines(program)
        reference.step()
        emulator.step()
        assert state(emulator) == state(reference)
        assert emulator.trap == "INVALID_OPERAND"


def test_jmp_differential():
    # Jump over an invalid opcode to HALT.
    assert_differential(bytes([
        0x30, 0x04, 0x00,
        0xFE,
        0x01,
    ]))


def test_conditional_branches_taken_and_not_taken_differential():
    cases = (
        (0x31, 0x01, True),   # JZ
        (0x31, 0x00, False),
        (0x32, 0x00, True),   # JNZ
        (0x32, 0x01, False),
        (0x33, 0x04, True),   # JC
        (0x33, 0x00, False),
        (0x34, 0x00, True),   # JNC
        (0x34, 0x04, False),
        (0x35, 0x02, True),   # JN
        (0x35, 0x00, False),
        (0x36, 0x00, True),   # JP means N=0
        (0x36, 0x02, False),
    )
    for opcode, flags, should_take in cases:
        reference, emulator = machines(bytes([opcode, 0x06, 0x00, 0x01]))
        reference.flags = emulator.flags = flags
        reference.step()
        emulator.step()
        assert state(emulator) == state(reference)
        assert emulator.pc == (0x0006 if should_take else 0x0003)


def test_branch_address_is_little_endian():
    reference, emulator = machines(bytes([0x30, 0x34, 0x12]))
    reference.step()
    emulator.step()
    assert state(emulator) == state(reference)
    assert emulator.pc == 0x1234


def test_conditional_branch_preserves_flags():
    for opcode in range(0x31, 0x37):
        reference, emulator = machines(bytes([opcode, 0x03, 0x00]))
        reference.flags = emulator.flags = 0x0F
        reference.step()
        emulator.step()
        assert state(emulator) == state(reference)
        assert emulator.flags == 0x0F


def test_push_pop_differential_and_stack_direction():
    def setup(cpu):
        cpu.sp = 0x9000
        cpu.r[2] = 0xA5
    assert_differential(bytes([
        0x40, 0x02,       # PUSH R2
        0x41, 0x03,       # POP R3
        0x01,
    ]), setup=setup, memory_addresses=(0x8FFF,))


def test_call_ret_differential_and_return_address_bytes():
    def setup(cpu):
        cpu.sp = 0x9000
    program = bytes([
        0x44, 0x08, 0x00, # CALL 0x0008
        0x01,             # return target: HALT
        0x00, 0x00, 0x00,
        0x45,             # RET at 0x0007? target adjusted below
        0x01,
    ])
    reference, emulator = machines(program)
    reference.sp = emulator.sp = 0x9000
    # CALL target is 8, where HALT lives.
    reference.run()
    emulator.run()
    assert state(emulator) == state(reference)
    assert emulator.halted
    assert emulator.sp == 0x9000


def test_call_pushes_high_then_low_and_ret_restores_pc():
    program = bytes([0x44, 0x06, 0x00, 0x01, 0x00, 0x00, 0x45])
    reference, emulator = machines(program)
    reference.sp = emulator.sp = 0x9000
    reference.step()
    emulator.step()
    assert state(emulator) == state(reference)
    assert emulator.sp == 0x8FFE
    assert emulator.mem[0x8FFF] == 0x00
    assert emulator.mem[0x8FFE] == 0x03
    reference.step()
    emulator.step()
    assert state(emulator) == state(reference)
    assert emulator.pc == 0x0003
    assert emulator.sp == 0x9000


def test_enter_leave_frame_differential():
    def setup(cpu):
        cpu.sp = 0x9000
        cpu.r[7] = 0x8800
    program = bytes([
        0x46, 0x10,       # ENTER 16
        0x47,             # LEAVE
        0x01,
    ])
    reference, emulator = machines(program)
    setup(reference)
    setup(emulator)
    reference.run()
    emulator.run()
    assert state(emulator) == state(reference)
    assert emulator.sp == 0x9000
    assert emulator.r[7] == 0x8800


def test_enter_frame_layout_matches_reference():
    def setup(cpu):
        cpu.sp = 0x9000
        cpu.r[7] = 0x8800
    reference, emulator = machines(bytes([0x46, 0x04]))
    setup(reference)
    setup(emulator)
    reference.step()
    emulator.step()
    assert state(emulator) == state(reference)
    assert emulator.sp == 0x8FFA
    assert emulator.r[7] == 0x8FFE
    assert emulator.mem[0x8FFF] == 0x88
    assert emulator.mem[0x8FFE] == 0x00
