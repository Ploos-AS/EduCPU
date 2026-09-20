import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools"),str(ROOT/"reference")]
from educ import parse
from educ_ir import lower
from educ_codegen import generate,CodegenError
from eduasm import assemble_object
from educpu import CPU

def compile_asm(source):
 return generate(lower(parse(source)))

def test_leaf_add_codegen_and_assembles():
 asm=compile_asm("byte add(byte a,byte b){return a+b;}")
 assert ".export add" in asm
 assert "ENTER " in asm and "STORES [0], R0" in asm and "ADD R7, R6" in asm
 assert "LOADS R0" in asm and "LEAVE " in asm and "RET" in asm
 obj,_=assemble_object(asm)
 assert obj["format"]=="educpu-object-v0" and obj["exports"]["add"]==0

def test_constant_return_codegen():
 asm=compile_asm("byte answer(){return 42;}")
 assert "MOVI R7, 42" in asm and "STORES [0], R7" in asm and "LOADS R0, [0]" in asm

def test_copy_local_codegen():
 asm=compile_asm("byte id(byte x){byte y=x;return y;}")
 assert "STORES [0], R0" in asm
 assert "LOADS R7, [0]" in asm and "STORES [1], R7" in asm

def test_many_values_use_stack_not_register_limit():
 source="byte f(){byte a=1;byte b=2;byte c=3;byte d=4;byte e=5;return a+b+c+d+e;}"
 asm=compile_asm(source)
 assert "ENTER " in asm
 obj,_=assemble_object(asm)
 assert obj["format"]=="educpu-object-v0"

def test_generated_constant_function_executes():
 asm=compile_asm("byte answer(){return 42;}")
 obj,_=assemble_object(asm)
 data=bytes.fromhex(obj["data"])
 c=CPU();c.mem[:len(data)]=data
 # Direct function entry needs a synthetic return address. Return to HALT after body.
 halt=len(data);c.mem[halt]=0x01
 c.sp-=1;c.mem[c.sp]=(halt>>8)&255;c.sp-=1;c.mem[c.sp]=halt&255
 c.run()
 assert c.r[0]==42 and c.halted and c.sp==0xFF00

def test_unsupported_control_flow_is_explicit():
 try:compile_asm("byte f(bool x){if(x){return 1;}else{return 2;}}")
 except CodegenError as e:assert "not yet supported" in str(e)
 else:assert False
