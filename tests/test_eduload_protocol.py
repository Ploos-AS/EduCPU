import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("p",Path(__file__).parents[1]/"tools"/"eduload_protocol.py")
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

def test_crc_standard_vector():
    assert p.crc16_ccitt_false(b"123456789")==0x29b1

def test_v1_frame_crc():
    image=bytes([0x11,0,0x2a,1])
    frame=p.frame_v1(image)
    assert frame[:5]==bytes([0x55,0xaa,1,4,0])
    body=frame[2:-2]
    crc=frame[-2]|(frame[-1]<<8)
    assert crc==p.crc16_ccitt_false(body)

def test_v1_rejects_empty():
    try:p.frame_v1(b"")
    except ValueError:pass
    else:raise AssertionError("empty image accepted")
