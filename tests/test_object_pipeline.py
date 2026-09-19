import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools"),str(ROOT/"reference")]
from eduasm import assemble_object
from edulink import link
from educpu import CPU

def test_assemble_link_execute_two_objects():
 main,_=assemble_object(".export start\n.import add_two\nstart:\n MOVI R0,20\n MOVI R1,22\n CALL add_two\n HALT\n")
 lib,_=assemble_object(".export add_two\nadd_two:\n ADD R0,R1\n RET\n")
 data,symbols,_=link([main,lib])
 c=CPU();c.mem[:len(data)]=data;c.run()
 assert c.r[0]==42 and c.halted and symbols["start"]==0 and symbols["add_two"]==10

def test_local_label_relocated_when_object_moves():
 prefix,_=assemble_object(".export prefix\nprefix: NOP\n")
 obj,_=assemble_object(".export fn\nfn: JMP done\n MOVI R0,1\ndone: MOVI R0,7\n HALT\n")
 data,symbols,_=link([prefix,obj])
 c=CPU();c.pc=symbols["fn"];c.mem[:len(data)]=data;c.run()
 assert c.r[0]==7 and c.halted

def test_export_must_exist():
 try:assemble_object(".export nope\nHALT\n")
 except ValueError as e:assert "export has no label" in str(e)
 else:assert False

def test_binary_mode_rejects_imports():
 from eduasm import assemble_text
 try:assemble_text(".import other\nCALL other\n")
 except ValueError as e:assert "object output" in str(e)
 else:assert False
