import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools"),str(ROOT/"reference")]
from eduasm import assemble_text
from educpu import CPU

def test_recursive_sum_uses_independent_frames_and_restores_sp():
 src=(ROOT/"examples"/"recursive_sum.eduasm").read_text()
 data,_,_=assemble_text(src);c=CPU();initial_sp=c.sp;c.mem[:len(data)]=data
 steps=c.run()
 assert c.halted and c.trap is None
 assert c.r[0]==15
 assert c.sp==initial_sp
 assert steps<200

def test_recursive_sum_deeper_case():
 src=(ROOT/"examples"/"recursive_sum.eduasm").read_text().replace("MOVI R0, 5","MOVI R0, 10")
 data,_,_=assemble_text(src);c=CPU();c.mem[:len(data)]=data;c.run()
 assert c.r[0]==55 and c.sp==0xFF00 and c.halted
