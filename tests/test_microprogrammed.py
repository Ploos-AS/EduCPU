from reference.microprogrammed import (
 ALU,CONTROL_STORE,Destination,FETCH,MicroInstruction,Next,Source,program_for
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
