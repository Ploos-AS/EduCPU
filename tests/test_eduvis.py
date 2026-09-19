import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools"),str(ROOT/"reference")]
from eduasm import assemble_text,debug_map
from eduvis import Visualizer
def visualizer(src):
 data,_,rows=assemble_text(src);return Visualizer(data,debug_map(rows,"demo.eduasm"))
def test_snapshot_correlates_source():
 s=visualizer("MOVI R0, 42\nHALT\n").snapshot();assert s["instruction"]=="MOVI R0, 0x2A" and s["source"]["line"]==1
def test_microstep_exposes_phase_without_early_commit():
 v=visualizer("MOVI R0, 42\nHALT\n");s=v.action("micro");assert s["phase"]=="FETCH_ADDR" and s["registers"][0]==0 and s["pc"]==0
def test_instruction_step_updates_state():
 v=visualizer("MOVI R0, 42\nHALT\n");s=v.action("step");assert s["registers"][0]==42 and s["pc"]==3
def test_reset_restores_cpu_and_program():
 v=visualizer("MOVI R0, 42\nHALT\n");v.action("step");s=v.action("reset");assert s["registers"][0]==0 and s["pc"]==0 and s["instruction"]=="MOVI R0, 0x2A"
