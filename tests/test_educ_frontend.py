import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools")]
from educ import lex,parse,Program,Function,VarDecl,If,Binary,Call

def test_lexer_tracks_tokens_and_lines():
 t=lex("byte main() {\n return 42;\n}\n")
 assert t[0].kind=="byte" and t[0].line==1
 assert any(x.kind=="NUMBER" and x.value=="42" and x.line==2 for x in t)

def test_parse_functions_call_and_if():
 tree=parse("""byte add(byte a, byte b){ return a+b; }
byte main(){ byte x=add(20,22); if(x==42){ return x; } else { return 0; } }
""")
 assert isinstance(tree,Program) and len(tree.functions)==2
 main=tree.functions[1];assert isinstance(main,Function)
 assert isinstance(main.body[0],VarDecl) and isinstance(main.body[0].value,Call)
 assert isinstance(main.body[1],If) and isinstance(main.body[1].condition,Binary)

def test_parse_while_assignment():
 tree=parse("byte main(){ byte x=3; while(x>0){ x=x-1; } return x; }")
 assert tree.functions[0].body[1].__class__.__name__=="While"

def test_reject_literal_over_255():
 try:parse("byte main(){ return 256; }")
 except SyntaxError as e:assert "out of range" in str(e)
 else:assert False

def test_reject_more_than_four_params():
 try:parse("byte f(byte a,byte b,byte c,byte d,byte e){return a;}")
 except SyntaxError as e:assert "four parameters" in str(e)
 else:assert False
