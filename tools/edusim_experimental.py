"""EduCPU M10 experimental teaching simulator.

Keeps M3 EduSim frozen while exposing capability-gated machine experiments.
"""
from machine import experimental_machine
from experimental_microcode import io_plan


def state(cpu):
    return {"pc":cpu.pc,"sp":cpu.sp,"flags":cpu.flags,
            "registers":cpu.r.copy(),"halted":cpu.halted,"trap":cpu.trap}


def changes(before, after):
    out=[]
    for i,(a,b) in enumerate(zip(before["registers"],after["registers"])):
        if a!=b: out.append(f"R{i}: {a:02X}->{b:02X}")
    if before["pc"]!=after["pc"]: out.append(f"PC: {before['pc']:04X}->{after['pc']:04X}")
    if before["sp"]!=after["sp"]: out.append(f"SP: {before['sp']:04X}->{after['sp']:04X}")
    if before["flags"]!=after["flags"]: out.append(f"FLAGS: {before['flags']:02X}->{after['flags']:02X}")
    if before["halted"]!=after["halted"]: out.append(f"HALT={after['halted']}")
    if before["trap"]!=after["trap"]: out.append(f"TRAP={after['trap']}")
    return out


class ExperimentalSimulator:
    def __init__(self, data=b""):
        self.machine=experimental_machine()
        self.machine.cpu.mem[:len(data)]=data

    @property
    def cpu(self):
        return self.machine.cpu

    def register_io(self, port, read=None, write=None):
        self.machine.register_io(port, read=read, write=write)

    def micro_plan(self):
        return io_plan(self.cpu.mem, self.cpu.pc)

    def step_event(self):
        pc=self.cpu.pc
        before=state(self.cpu)
        self.machine.last_io=None
        self.machine.step()
        after=state(self.cpu)
        return {"pc":pc,"before":before,"after":after,
                "changes":changes(before,after),"io":self.machine.last_io}

    @staticmethod
    def format_event(event):
        lines=[f"{event['pc']:04X}: STEP"]
        if event["io"]:
            io=event["io"]
            lines.append(
                f"I/O {io['direction'].upper()} port={io['port']:02X} "
                f"value={io['value']:02X} mapped={'yes' if io['mapped'] else 'no'}"
            )
        if event["changes"]:
            lines.append("  "+", ".join(event["changes"]))
        return "\n".join(lines)
