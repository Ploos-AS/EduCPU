import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools"),str(ROOT/"reference")]
from educ import parse,compile_source
from educ_ir import lower
from educ_codegen import generate,CodegenError
from eduasm import assemble_object
from edulink import link
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
 data,_,_=link([obj])
 c=CPU();c.mem[:len(data)]=data
 # Direct function entry needs a synthetic return address. Return to HALT after body.
 halt=len(data);c.mem[halt]=0x01
 c.sp-=1;c.mem[c.sp]=(halt>>8)&255;c.sp-=1;c.mem[c.sp]=halt&255
 c.run()
 assert c.r[0]==42 and c.halted and c.sp==0xFF00

def run_function(source, args=(), entry=None):
 asm=compile_asm(source);obj,_=assemble_object(asm);data,symbols,_=link([obj])
 c=CPU();c.mem[:len(data)]=data
 if entry is None:entry="main" if "main" in symbols else next(iter(symbols))
 c.pc=symbols[entry]
 for i,v in enumerate(args):c.r[i]=v
 halt=len(data);c.mem[halt]=0x01
 c.sp-=1;c.mem[c.sp]=(halt>>8)&255;c.sp-=1;c.mem[c.sp]=halt&255
 c.run()
 return c

def test_if_else_executes_both_paths():
 source="byte choose(bool x){if(x){return 11;}else{return 22;}}"
 assert run_function(source,(1,)).r[0]==11
 assert run_function(source,(0,)).r[0]==22

def test_while_executes():
 source="byte count(byte n){byte x=0;while(x<n){x=x+1;}return x;}"
 c=run_function(source,(7,))
 assert c.r[0]==7 and c.sp==0xFF00

def test_all_unsigned_comparisons():
 ops=[("==",1,1,1),("!=",1,2,1),("<",1,2,1),("<=",2,2,1),(">",3,2,1),(">=",2,2,1),
      ("==",1,2,0),("!=",2,2,0),("<",2,1,0),("<=",3,2,0),(">",2,3,0),(">=",1,2,0)]
 for op,a,b,want in ops:
  c=run_function(f"bool f(byte a,byte b){{return a {op} b;}}",(a,b))
  assert c.r[0]==want,(op,a,b,c.r[0])

def test_boolean_not():
 assert run_function("bool f(bool x){return !x;}",(0,)).r[0]==1
 assert run_function("bool f(bool x){return !x;}",(1,)).r[0]==0

def test_function_call_executes():
 source="byte add(byte a,byte b){return a+b;} byte main(){return add(20,22);}"
 c=run_function(source)
 assert c.r[0]==42 and c.halted and c.sp==0xFF00

def test_nested_calls_execute():
 source="byte inc(byte x){return x+1;} byte twice(byte x){return inc(inc(x));} byte main(){return twice(40);}"
 c=run_function(source)
 assert c.r[0]==42 and c.halted and c.sp==0xFF00

def test_recursion_executes():
 source="byte sum(byte n){if(n==0){return 0;}else{return n+sum(n-1);}} byte main(){return sum(10);}"
 c=run_function(source)
 assert c.r[0]==55 and c.halted and c.sp==0xFF00

def test_void_call_statement_executes():
 source="void ping(){return;} byte main(){ping();return 42;}"
 c=run_function(source)
 assert c.r[0]==42 and c.halted and c.sp==0xFF00


def test_control_flow_labels_are_namespaced_per_function():
 source="byte a(bool x){if(x){return 1;}else{return 0;}} byte b(bool x){if(x){return 2;}else{return 0;}} byte main(){return a(1)+b(1);}"
 asm=compile_asm(source)
 assert "__a_if_then_0:" in asm and "__b_if_then_0:" in asm
 obj,_=assemble_object(asm)
 data,_,_=link([obj])
 assert data
 c=run_function(source)
 assert c.r[0]==3 and c.halted and c.sp==0xFF00


def test_complete_educ_compile_pipeline_executes():
 source="byte add(byte a,byte b){return a+b;} byte main(){return add(20,22);}"
 tree,ir,asm,obj,data,symbols=compile_source(source,"pipeline.educ")
 assert tree.functions and ir.functions
 assert ".export main" in asm
 assert obj["format"]=="educpu-object-v0"
 c=CPU();c.mem[:len(data)]=data;c.pc=symbols["main"]
 halt=len(data);c.mem[halt]=0x01
 c.sp-=1;c.mem[c.sp]=(halt>>8)&255;c.sp-=1;c.mem[c.sp]=halt&255
 c.run()
 assert c.r[0]==42 and c.halted and c.sp==0xFF00
