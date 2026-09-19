import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools"),str(ROOT/"reference")]
from eduasm import assemble_text
from educpu import CPU

def run(src):
 data,_,_=assemble_text(src);c=CPU();c.mem[:len(data)]=data;c.run();return c,data

def test_enter_store_load_leave():
 c,data=run("""MOVI R0, 42
ENTER 2
STORES [0], R0
MOVI R0, 0
LOADS R0, [0]
LEAVE 2
HALT
""")
 assert c.r[0]==42 and c.sp==0xFF00 and c.halted
 assert bytes([0x18,2]) in data and bytes([0x17,0,0]) in data and bytes([0x16,0,0]) in data

def test_signed_stack_offset():
 c,_=run("""MOVI R0, 99
PUSH R0
LOADS R1, [0]
LOADS R2, [1]
POP R3
HALT
""")
 assert c.r[1]==99 and c.r[3]==99

def test_stack_offset_range_rejected():
 try:assemble_text("LOADS R0, [128]")
 except ValueError as e:assert "stack offset" in str(e)
 else:assert False
