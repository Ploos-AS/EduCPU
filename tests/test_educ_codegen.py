import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools")]
from educ import parse
from educ_ir import lower
from educ_codegen import generate,CodegenError
from eduasm import assemble_object

def compile_asm(source):
 return generate(lower(parse(source)))

def test_leaf_add_codegen_and_assembles():
 asm=compile_asm("byte add(byte a,byte b){return a+b;}")
 assert ".export add" in asm
 assert "ADD R7, R1" in asm and "MOV R0, R7" in asm and "RET" in asm
 obj,_=assemble_object(asm)
 assert obj["format"]=="educpu-object-v0" and obj["exports"]["add"]==0

def test_constant_return_codegen():
 asm=compile_asm("byte answer(){return 42;}")
 assert "MOVI R7, 42" in asm and "MOV R0, R7" in asm

def test_copy_local_codegen():
 asm=compile_asm("byte id(byte x){byte y=x;return y;}")
 assert "MOV R7, R0" in asm and "MOV R0, R7" in asm

def test_unsupported_control_flow_is_explicit():
 try:compile_asm("byte f(bool x){if(x){return 1;}else{return 2;}}")
 except CodegenError as e:assert "initial backend slice" in str(e)
 else:assert False
