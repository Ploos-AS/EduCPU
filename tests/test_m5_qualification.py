import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools")]
from educ import lex,parse
from educ_semantic import analyze
from educ_ir import lower,format_ir
from educ_ir_validate import validate

def test_m5_complete_frontend_pipeline():
 source=(ROOT/"examples"/"hello.educ").read_text()
 tokens=lex(source)
 assert tokens[-1].kind=="EOF" and any(t.kind=="if" for t in tokens)
 ast=parse(source)
 sigs=analyze(ast)
 assert sigs["add"].return_type=="byte" and sigs["main"].return_type=="byte"
 ir=lower(ast)
 assert validate(ir)
 text=format_ir(ir)
 assert "func byte add(byte a, byte b)" in text
 assert "call add" in text and "br " in text and "ret " in text

def test_m5_recursion_frontend_pipeline():
 source="""byte sum(byte n) {
    if (n == 0) { return 0; }
    else { return n + sum(n - 1); }
}
byte main() { return sum(5); }
"""
 ast=parse(source);analyze(ast);ir=lower(ast)
 assert validate(ir)
 text=format_ir(ir)
 assert "call sum" in text
