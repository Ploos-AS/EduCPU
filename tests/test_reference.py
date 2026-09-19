import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "reference"))
from educpu import CPU

def cpu_with(code):
    c=CPU(); c.mem[:len(code)]=bytes(code); return c

def test_reset():
    c=CPU(); c.r[2]=99; c.pc=4; c.reset()
    assert c.r == [0]*8 and c.pc == 0 and c.sp == 0xFF00 and c.flags == 0

def test_movi_add_halt():
    c=cpu_with([0x11,0,10, 0x11,1,20, 0x20,0,1, 0x01])
    c.run()
    assert c.r[0] == 30 and c.halted and c.pc == 10

def test_add_carry_zero():
    c=cpu_with([0x11,0,255, 0x21,0,1, 0x01]); c.run()
    assert c.r[0] == 0
    assert c.flags & CPU.Z and c.flags & CPU.C

def test_sub_no_borrow_convention():
    c=cpu_with([0x11,0,5, 0x23,0,3, 0x01]); c.run()
    assert c.r[0] == 2 and c.flags & CPU.C

def test_branch():
    c=cpu_with([0x11,0,0, 0x25,0,0, 0x31,12,0, 0x11,1,99, 0x01])
    c.run()
    assert c.r[1] == 0 and c.halted

def test_call_ret_stack():
    code=[0x38,6,0, 0x01,0,0, 0x11,0,42, 0x39]
    c=cpu_with(code); c.run()
    assert c.r[0] == 42 and c.halted and c.sp == 0xFF00

def test_little_endian_absolute_load():
    c=cpu_with([0x12,0,0x34,0x12,0x01]); c.mem[0x1234]=0xA5; c.run()
    assert c.r[0] == 0xA5

def test_invalid_opcode_traps():
    c=cpu_with([0xFF]); c.step()
    assert c.trap == "INVALID_OPCODE"

def test_invalid_register_traps():
    c=cpu_with([0x11,8,1]); c.step()
    assert c.trap == "INVALID_OPERAND"
