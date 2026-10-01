from reference.microprogrammed import (
 ALU,CONTROL_STORE,Destination,FETCH,MicroInstruction,MicroMachine,MicroSequencer,Next,Source,program_for
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
 try: program_for("AND")
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


def test_movi_executes_entirely_through_visible_microsteps():
 m=MicroMachine(bytes((0x11,2,0xa5)))
 events=[]
 while not (m.seq.phase=="FETCH" and m.seq.micro_pc==0 and m.pc==3):
  events.append(m.step_micro())
  assert len(events)<10
 assert m.r[2]==0xa5
 assert m.pc==3
 # 2 shared fetch microinstructions + 4 MOVI microinstructions.
 assert len(events)==6
 assert events[1]["after"]["phase"]=="EXECUTE"
 assert events[-1]["after"]["phase"]=="FETCH"


def test_movi_invalid_register_selector_is_not_hidden():
 m=MicroMachine(bytes((0x11,8,0xa5)))
 m.step_micro();m.step_micro();m.step_micro();m.step_micro();m.step_micro()
 try:m.step_micro()
 except ValueError as e:assert "INVALID_OPERAND" in str(e)
 else:raise AssertionError("invalid register selector must fail")


def test_mov_reads_source_register_and_writes_destination_via_control_store():
 m=MicroMachine(bytes((0x10,2,5)))
 m.r[5]=0x7c
 events=[]
 while not (m.seq.phase=="FETCH" and m.seq.micro_pc==0 and m.pc==3):
  events.append(m.step_micro());assert len(events)<12
 assert m.r[2]==0x7c
 assert m.r[5]==0x7c
 assert m.pc==3
 assert len(events)==7


def test_mov_rejects_invalid_source_selector():
 m=MicroMachine(bytes((0x10,2,8)))
 for _ in range(6):m.step_micro()
 try:m.step_micro()
 except ValueError as e:assert "INVALID_OPERAND" in str(e)
 else:raise AssertionError("invalid MOV source selector must fail")


def _run_one(m):
 events=[]
 while not (m.seq.phase=="FETCH" and m.seq.micro_pc==0 and m.pc==3):
  events.append(m.step_micro());assert len(events)<12
 return events

def test_add_runs_through_alu_and_writes_result_and_flags():
 m=MicroMachine(bytes((0x20,2,5)));m.r[2]=0x7f;m.r[5]=1
 events=_run_one(m)
 assert m.r[2]==0x80
 assert m.r[5]==1
 assert m.flags==0x0a  # N + signed overflow
 assert len(events)==7
 assert events[-1]["flags"]==0x0a

def test_add_sets_zero_and_carry_on_unsigned_wrap():
 m=MicroMachine(bytes((0x20,2,5)));m.r[2]=0xff;m.r[5]=1
 _run_one(m)
 assert m.r[2]==0
 assert m.flags==0x05  # Z + C

def test_add_rejects_invalid_register_selector():
 m=MicroMachine(bytes((0x20,8,1)))
 for _ in range(6):m.step_micro()
 try:m.step_micro()
 except ValueError as e:assert "INVALID_OPERAND" in str(e)
 else:raise AssertionError("invalid ADD selector must fail")


def test_sub_writes_result_and_subtraction_flags():
 m=MicroMachine(bytes((0x22,2,5)));m.r[2]=0x00;m.r[5]=1
 _run_one(m)
 assert m.r[2]==0xff
 assert m.flags==0x02  # N, no-borrow carry is clear

def test_sub_no_borrow_sets_carry():
 m=MicroMachine(bytes((0x22,2,5)));m.r[2]=5;m.r[5]=3
 _run_one(m)
 assert m.r[2]==2
 assert m.flags==0x04

def test_cmp_updates_flags_but_discards_alu_result():
 m=MicroMachine(bytes((0x24,2,5)));m.r[2]=5;m.r[5]=5
 events=_run_one(m)
 assert m.r[2]==5 and m.r[5]==5
 assert m.flags==0x05  # equal: Z + no-borrow C
 assert events[-1]["registers"][2]==5

def test_cmp_signed_overflow_matches_subtraction_semantics():
 m=MicroMachine(bytes((0x24,2,5)));m.r[2]=0x80;m.r[5]=1
 _run_one(m)
 assert m.r[2]==0x80
 assert m.flags==0x0c  # C + V; result 7F is discarded
