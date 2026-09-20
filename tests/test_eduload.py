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

def test_eduasm_image(tmp_path):
    p=tmp_path/"hello.eduasm"
    p.write_text("MOVI R0, 42\nHALT\n")
    assert m.image_bytes(p) == bytes([0x11,0x00,0x2a,0x01])

def test_educ_image(tmp_path):
    p=tmp_path/"hello.educ"
    p.write_text("byte main() { return 42; }\n")
    data=m.image_bytes(p)
    assert isinstance(data, bytes)
    assert len(data)>0
    # A compiled program must contain executable machine code, not source text.
    assert data != p.read_bytes()

def test_raw_image(tmp_path):
    p=tmp_path/"hello.bin"; raw=bytes([0x11,0,0x2a,1]); p.write_bytes(raw)
    assert m.image_bytes(p)==raw
