import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools"),str(ROOT/"reference")]
from edulink import link
from educpu import CPU

def obj(data="",exports=None,relocations=None):
 return {"format":"educpu-object-v0","data":data,"exports":exports or {},"locals":{},"imports":[],"relocations":relocations or []}

def test_links_abs16_call_and_runs():
 main=obj("38000001",{"start":0},[{"offset":1,"type":"abs16le","symbol":"answer"}])
 lib=obj("11002a39",{"answer":0})
 data,symbols,bases=link([main,lib])
 assert symbols["answer"]==4 and data[:4]==bytes([0x38,4,0,0x01])
 c=CPU();c.mem[:len(data)]=data;c.run()
 assert c.r[0]==42 and c.halted

def test_duplicate_symbol_rejected():
 try:link([obj(exports={"x":0}),obj(exports={"x":0})])
 except ValueError as e:assert "duplicate symbol" in str(e)
 else:assert False

def test_undefined_symbol_rejected():
 try:link([obj("0000",relocations=[{"offset":0,"type":"abs16le","symbol":"missing"}])])
 except ValueError as e:assert "undefined symbol" in str(e)
 else:assert False

def test_rejects_legacy_unversioned_object():
 try:link([{"data":""}])
 except ValueError as e:assert "unsupported object format" in str(e)
 else:assert False
