import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools"),str(ROOT/"reference")]
from eduasm import assemble_text
from edusim import Simulator, state, diff

def test_step_changes_visible_state():
    data,_,_=assemble_text("MOVI R0, 42\nHALT\n")
    s=Simulator(data);before=state(s.cpu);s.cpu.step();after=state(s.cpu)
    changes=diff(before,after)
    assert "R0: 00->2A" in changes
    assert s.cpu.pc==3

def test_breakpoint_stops_before_instruction():
    data,labels,_=assemble_text("MOVI R0, 1\nnext: ADDI R0, 1\nHALT\n")
    s=Simulator(data);s.breakpoints.add(labels["next"]);s.run()
    assert s.cpu.r[0]==1 and s.cpu.pc==labels["next"]

def test_watch_target_memory_with_store():
    data,_,_=assemble_text("MOVI R0, 0x55\nSTORE [0x0100], R0\nHALT\n")
    s=Simulator(data);s.watch.add(0x0100);s.run()
    assert s.cpu.mem[0x0100]==0x55

def test_instruction_decode():
    data,_,_=assemble_text("MOVI R3, 7\nHALT\n")
    s=Simulator(data)
    from edusim import instruction_at
    assert instruction_at(s.cpu,0)=="MOVI R3, 0x07"
