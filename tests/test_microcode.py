import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools"),str(ROOT/"reference")]
from educpu import CPU
from eduasm import assemble_text
from microcode import plan,MicroStepper

def cpu(src):
    data,_,_=assemble_text(src);c=CPU();c.mem[:len(data)]=data;return c

def test_add_has_alu_and_flags_phases():
    c=cpu("ADD R0, R1\nHALT\n")
    phases=[x.phase for x in plan(c)]
    assert phases[:3]==["FETCH_ADDR","FETCH_OPCODE","DECODE"]
    assert "ALU" in phases and "FLAGS" in phases and "WRITEBACK" in phases

def test_microsteps_do_not_change_state_until_commit():
    c=cpu("MOVI R0, 42\nHALT\n");m=MicroStepper(c)
    first,_=m.next();assert first.phase=="FETCH_ADDR"
    assert c.pc==0 and c.r[0]==0
    committed=False
    while not committed:
        _,committed=m.next()
    assert c.pc==3 and c.r[0]==42

def test_branch_plan_has_control_phase():
    c=cpu("JMP 0x0010\n")
    assert "CONTROL" in [x.phase for x in plan(c)]

def test_halt_commits_after_teaching_sequence():
    c=cpu("HALT\n");m=MicroStepper(c);committed=False
    while not committed:_,committed=m.next()
    assert c.halted
