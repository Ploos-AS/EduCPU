"""Serial-loader protocol helpers shared by host tooling and tests."""

def crc16_ccitt_false(data: bytes) -> int:
    crc=0xffff
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc=((crc<<1)^0x1021)&0xffff if crc&0x8000 else (crc<<1)&0xffff
    return crc

def frame_v1(image: bytes) -> bytes:
    if not image: raise ValueError("image is empty")
    if len(image)>0xffff: raise ValueError("image exceeds 65535-byte limit")
    n=len(image)
    body=bytes((1,n&255,n>>8))+image
    crc=crc16_ccitt_false(body)
    return bytes((0x55,0xaa))+body+bytes((crc&255,crc>>8))
