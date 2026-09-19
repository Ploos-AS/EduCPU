import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools")]
from educ import parse
from educ_semantic import analyze,SemanticError

def ok(src):return analyze(parse(src))
def bad(src,text):
 try:ok(src)
 except SemanticError as e:assert text in str(e)
 else:assert False

def test_valid_typed_program():
 sigs=ok("""byte add(byte a,byte b){return a+b;}
byte main(){byte x=add(20,22); bool yes=x==42; if(yes){return x;}else{return 0;}}""")
 assert sigs["add"].return_type=="byte"

def test_duplicate_function_and_local():
 bad("byte f(){return 1;} byte f(){return 2;}","duplicate function")
 bad("byte f(byte x){byte x=1;return x;}","duplicate parameter/local")

def test_unknown_names():
 bad("byte f(){return x;}","unknown variable")
 bad("byte f(){return nope();}","unknown function")

def test_type_rules():
 bad("byte f(){bool x=true;return x;}","returns bool")
 bad("byte f(){if(1){return 1;}else{return 0;}}","if condition must be bool")
 bad("byte f(){return true+false;}","requires byte operands")
 bad("bool f(){return 1==true;}","matching value types")

def test_call_signature():
 bad("byte add(byte a,byte b){return a+b;} byte f(){return add(1);}","expected 2 arguments")
 bad("byte id(byte a){return a;} byte f(){return id(true);}","argument 1 is bool")

def test_return_path_validation():
 bad("byte f(bool x){if(x){return 1;}}","not all paths return")
 ok("byte f(bool x){if(x){return 1;}else{return 2;}}")

def test_void_return_rules():
 ok("void f(){return;}")
 bad("void f(){return 1;}","void function cannot return a value")
 bad("byte f(){return;}","must return a value")
