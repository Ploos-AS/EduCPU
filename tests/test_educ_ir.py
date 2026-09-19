import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools")]
from educ import parse
from educ_ir import lower,format_ir

def test_lower_arithmetic_and_return():
 ir=lower(parse("byte add(byte a,byte b){return a+b;}"))
 f=ir.functions[0]
 assert [(i.op,i.type) for i in f.instructions]==[("add","byte"),("ret",None)]
 assert f.instructions[0].args==["a","b"]

def test_lower_call_and_local():
 ir=lower(parse("byte id(byte x){return x;} byte main(){byte y=id(7);return y;}"))
 f=ir.functions[1]
 assert [i.op for i in f.instructions]==["const","call","copy","ret"]
 assert f.instructions[1].args[0]=="id"

def test_if_lowers_to_explicit_control_flow():
 ir=lower(parse("byte f(bool x){if(x){return 1;}else{return 2;}}"))
 ops=[i.op for i in ir.functions[0].instructions]
 assert "br" in ops and ops.count("label")==3 and "jmp" in ops

def test_while_lowers_to_loop_labels():
 ir=lower(parse("byte f(){byte x=2;while(x>0){x=x-1;}return x;}"))
 ops=[i.op for i in ir.functions[0].instructions]
 assert "br" in ops and ops.count("label")==3 and "jmp" in ops

def test_text_ir_is_inspectable():
 text=format_ir(lower(parse("byte f(){return 42;}")))
 assert "func byte f()" in text and "%t0:byte = const 42" in text and "ret %t0" in text
