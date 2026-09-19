import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"reference"))
from eduasm import assemble_text, debug_map
from edudis import disassemble
from educpu import CPU

def test_known_encoding():
    data,labels,_=assemble_text("start: MOVI R0, 10\nADD R0, R0\nHALT\n")
    assert labels["start"]==0
    assert data==bytes([0x11,0,10,0x20,0,0,0x01])

def test_label_and_execution():
    src="""MOVI R0, 3
MOVI R1, 0
loop:
ADD R1, R0
SUBI R0, 1
CMPI R0, 0
JNZ loop
HALT
"""
    data,labels,_=assemble_text(src)
    assert labels["loop"]==6
    c=CPU();c.mem[:len(data)]=data;c.run()
    assert c.r[1]==6 and c.halted

def test_disassembly():
    data,_,_=assemble_text("MOVI R2, 0x2A\nHALT\n")
    rows=disassemble(data)
    assert rows[0][2]=="MOVI R2, 0x2A"
    assert rows[1][2]=="HALT"

def test_bad_register():
    try: assemble_text("MOVI R8, 1")
    except ValueError as e: assert "R0..R7" in str(e)
    else: assert False

def test_forward_label():
    data,labels,_=assemble_text("JMP done\nMOVI R0, 1\ndone: HALT\n")
    assert labels["done"]==6
    assert data[:3]==bytes([0x30,6,0])


def test_debug_map_correlates_address_line_and_bytes():
    data,_,rows=assemble_text("; comment\nstart: MOVI R0, 7\nHALT\n")
    dbg=debug_map(rows,"demo.eduasm")
    assert dbg["source"]=="demo.eduasm"
    assert dbg["instructions"][0]["address"]==0
    assert dbg["instructions"][0]["line"]==2
    assert dbg["instructions"][0]["bytes"]=="110007"
