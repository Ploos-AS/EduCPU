import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("eduload",Path(__file__).parents[1]/"tools"/"eduload.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_frame():
    assert m.frame(bytes([0x11,0,0x2a,1])) == bytes([0x55,0xaa,4,0,0x11,0,0x2a,1])

def test_empty():
    try: m.frame(b"")
    except ValueError: pass
    else: raise AssertionError("empty image accepted")

def test_too_large():
    try: m.frame(bytes(65536))
    except ValueError: pass
    else: raise AssertionError("oversized image accepted")
