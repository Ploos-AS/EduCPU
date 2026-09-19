import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools")]
from educ import parse
from educ_ir import lower,IRProgram,IRFunction,IRInstr
from educ_ir_validate import validate,IRValidationError

def bad(p,text):
 try:validate(p)
 except IRValidationError as e:assert text in str(e)
 else:assert False

def test_lowered_program_validates():
 assert validate(lower(parse("byte f(byte x){while(x>0){x=x-1;}return x;}")))

def test_undefined_value():
 p=IRProgram([IRFunction("f","byte",[],[IRInstr("ret",args=["%missing"])])])
 bad(p,"undefined value")

def test_unknown_branch_label():
 p=IRProgram([IRFunction("f","void",[],[IRInstr("const","%t0","bool",[1]),IRInstr("br",args=["%t0","yes","no"])])])
 bad(p,"unknown label")

def test_arithmetic_type_error():
 p=IRProgram([IRFunction("f","bool",[],[IRInstr("const","%t0","bool",[1]),IRInstr("add","%t1","byte",["%t0","%t0"]),IRInstr("ret",args=["%t0"])])])
 bad(p,"add requires byte")

def test_call_signature_validation():
 callee=IRFunction("id","byte",[("byte","x")],[IRInstr("ret",args=["x"])])
 caller=IRFunction("f","byte",[],[IRInstr("const","%t0","bool",[1]),IRInstr("call","%t1","byte",["id","%t0"]),IRInstr("ret",args=["%t1"])])
 bad(IRProgram([callee,caller]),"bad call types")

def test_temporary_single_definition():
 p=IRProgram([IRFunction("f","byte",[],[IRInstr("const","%t0","byte",[1]),IRInstr("const","%t0","byte",[2]),IRInstr("ret",args=["%t0"])])])
 bad(p,"temporary redefined")
