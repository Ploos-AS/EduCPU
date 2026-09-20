#!/usr/bin/env python3
"""Send an EduCPU machine-code image using serial loader protocol v0."""
import argparse, pathlib, sys, time

def frame(image: bytes) -> bytes:
    if not image:
        raise ValueError("image is empty")
    if len(image) > 0xffff:
        raise ValueError("image exceeds protocol-v0 65535-byte limit")
    n=len(image)
    return bytes((0x55,0xaa,n&0xff,(n>>8)&0xff))+image

def main():
    ap=argparse.ArgumentParser(description="Load an EduCPU binary over UART")
    ap.add_argument("image",type=pathlib.Path)
    ap.add_argument("--port",required=True,help="serial port, e.g. /dev/ttyUSB0 or COM4")
    ap.add_argument("--baud",type=int,default=115200)
    args=ap.parse_args()
    data=args.image.read_bytes()
    packet=frame(data)
    try:
        import serial
    except ImportError:
        sys.exit("pyserial is required: python -m pip install pyserial")
    with serial.Serial(args.port,args.baud,bytesize=8,parity="N",stopbits=1,timeout=1) as s:
        s.reset_input_buffer()
        s.write(packet); s.flush()
        # Give the FPGA time to consume the final byte before closing the port.
        time.sleep(0.05)
    print(f"sent {len(data)} bytes to {args.port} at {args.baud} baud")

if __name__=="__main__":
    main()
