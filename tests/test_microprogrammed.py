from reference.microprogrammed import (
 ALU,CONTROL_STORE,Destination,FETCH,MicroInstruction,MicroSequencer,Next,Source,program_for
)

def test_control_word_round_trips_every_field():
 u=MicroInstruction(Source.ALU,Destination.REG_A,ALU.ADD,True,True,True,Next.DISPATCH)
 assert MicroInstruction.decode(u.encode())==u
 assert 0<=u.encode()<(1<<24)

def test_fetch_is_shared_and_visible():
 assert len(FETCH)==2
 assert FETCH[0].source==Source.PC and FETCH[0].memory_read
 assert FETCH[1].source==Source.MEM and FETCH[1].destination==Destination.IR
 assert FETCH[1].pc_increment and FETCH[1].next==Next.DISPATCH

def test_first_control_store_programs_are_intentionally_tiny():
 assert program_for("nop")==CONTROL_STORE["NOP"]
 assert program_for("NOP")[-1].next==Next.FETCH
 assert program_for("HALT")[-1].next==Next.HALT

def test_unknown_microprogram_is_explicit():
 try: program_for("MOVI")
 except KeyError as e: assert "no microprogram" in str(e)
 else: raise AssertionError("missing microprogram must not silently execute")

def test_control_word_fields_fit_without_overlap():
 # Maximum legal values exercise every allocated field.
 u=MicroInstruction(Source.ALU,Destination.FLAGS,ALU.SHR,True,True,True,Next.HALT)
 word=u.encode()
 assert MicroInstruction.decode(word)==u


def test_microsequencer_exposes_fetch_dispatch_nop_fetch_cycle():
 s=MicroSequencer()
 assert (s.phase,s.micro_pc)==("FETCH",0)
 first=s.step()
 assert first["after"]["micro_pc"]==1
 dispatch=s.step(ir=0x00)
 assert dispatch["after"]["phase"]=="EXECUTE"
 assert dispatch["after"]["micro_pc"]==0
 done=s.step()
 assert done["after"]["phase"]=="FETCH"
 assert done["after"]["micro_pc"]==0


def test_microsequencer_halt_stops_control_machine():
 s=MicroSequencer();s.step();s.step(ir=0x01);event=s.step()
 assert event["after"]["halted"] is True
 assert s.current() is None


def test_dispatch_requires_visible_ir_and_known_opcode():
 s=MicroSequencer();s.step()
 try:s.step()
 except ValueError as e:assert "requires IR" in str(e)
 else:raise AssertionError("dispatch without IR must fail")
 s.reset();s.step()
 try:s.step(ir=0xff)
 except KeyError as e:assert "no opcode dispatch" in str(e)
 else:raise AssertionError("unknown opcode must not dispatch")
