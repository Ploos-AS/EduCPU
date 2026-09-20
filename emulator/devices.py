"""Deterministic emulator device layer.

Devices live above the CPU ISA. Memory mapping is explicit and optional; an
unmapped address remains ordinary RAM.
"""
from dataclasses import dataclass, field
from typing import Iterable


class Device:
    def reset(self) -> None:
        raise NotImplementedError

    def read(self, offset: int) -> int:
        raise NotImplementedError

    def write(self, offset: int, value: int) -> None:
        raise NotImplementedError


@dataclass
class ByteStreamDevice(Device):
    """Deterministic byte input/output device for emulator tests and demos."""
    input_bytes: bytearray = field(default_factory=bytearray)
    output_bytes: bytearray = field(default_factory=bytearray)

    def __init__(self, input_bytes: Iterable[int] = ()):
        self.input_bytes = bytearray(x & 0xFF for x in input_bytes)
        self.output_bytes = bytearray()

    def reset(self) -> None:
        self.output_bytes.clear()

    def read(self, offset: int) -> int:
        if offset != 0 or not self.input_bytes:
            return 0
        return self.input_bytes.pop(0)

    def write(self, offset: int, value: int) -> None:
        if offset == 0:
            self.output_bytes.append(value & 0xFF)


@dataclass
class DeviceMap:
    devices: list[tuple[int, int, Device]] = field(default_factory=list)

    def attach(self, start: int, end: int, device: Device) -> None:
        if start < 0 or end > 0x10000 or start >= end:
            raise ValueError("invalid device range")
        if any(start < b and a < end for a, b, _ in self.devices):
            raise ValueError("overlapping device range")
        self.devices.append((start, end, device))

    def reset(self) -> None:
        for _, _, device in self.devices:
            device.reset()

    def lookup(self, address: int):
        for start, end, device in self.devices:
            if start <= address < end:
                return device, address - start
        return None
