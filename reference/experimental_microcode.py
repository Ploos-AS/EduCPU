"""Conceptual M10 micro-operation plans.

These are teaching phases, not a claim about RTL clock-cycle timing.
"""


def io_plan(memory, pc):
    op=memory[pc & 0xffff]
    if op==0xe0:
        reg=memory[(pc+1)&0xffff]
        port=memory[(pc+2)&0xffff]
        return [
            ("FETCH",f"read opcode E0 from memory[{pc & 0xffff:04X}]"),
            ("DECODE","decode E0 as IN rd,port8"),
            ("OPERAND",f"read destination register selector R{reg}"),
            ("OPERAND",f"read I/O port address {port:02X}"),
            ("I/O READ",f"select port {port:02X} and request one input byte"),
            ("TRANSFER",f"transfer device byte from port {port:02X} toward R{reg}"),
            ("COMMIT",f"write input byte to R{reg}; FLAGS unchanged"),
        ]
    if op==0xe1:
        port=memory[(pc+1)&0xffff]
        reg=memory[(pc+2)&0xffff]
        return [
            ("FETCH",f"read opcode E1 from memory[{pc & 0xffff:04X}]"),
            ("DECODE","decode E1 as OUT port8,rs"),
            ("OPERAND",f"read I/O port address {port:02X}"),
            ("OPERAND",f"read source register selector R{reg}"),
            ("I/O WRITE",f"select port {port:02X} and present byte from R{reg}"),
            ("TRANSFER",f"transfer R{reg} byte to device at port {port:02X}"),
            ("COMMIT","device observes output byte; FLAGS unchanged"),
        ]
    return []
