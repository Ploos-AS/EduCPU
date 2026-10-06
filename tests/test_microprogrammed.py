from reference.microprogrammed import (
 ALU,CONTROL_STORE,Destination,FETCH,MicroInstruction,MicroMachine,MicroSequencer,Next,OPCODE_NAMES,Source,program_for
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
 try: program_for("DOES_NOT_EXIST")
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


def test_logical_microprograms_write_result_and_only_zn_flags():
 cases=((0x28,0xf0,0x0f,0x00,0x01),(0x29,0x80,0x01,0x81,0x02),(0x2a,0xaa,0xaa,0x00,0x01))
 for op,a,b,result,flags in cases:
  m=MicroMachine(bytes((op,2,5)));m.r[2]=a;m.r[5]=b;m.flags=0x0f
  _run_one(m)
  assert m.r[2]==result and m.flags==flags

def test_not_is_unary_and_clears_old_carry_overflow():
 m=MicroMachine(bytes((0x2b,2)));m.r[2]=0xff;m.flags=0x0c
 events=[]
 while not (m.seq.phase=="FETCH" and m.seq.micro_pc==0 and m.pc==2):
  events.append(m.step_micro());assert len(events)<10
 assert m.r[2]==0 and m.flags==0x01

def test_shifts_publish_shifted_out_bit_as_carry():
 left=MicroMachine(bytes((0x2c,2)));left.r[2]=0x80
 right=MicroMachine(bytes((0x2d,2)));right.r[2]=0x01
 for m in (left,right):
  while not (m.seq.phase=="FETCH" and m.seq.micro_pc==0 and m.pc==2):m.step_micro()
  assert m.r[2]==0 and m.flags==0x05


def _run_until_fetch(m,pc,limit=20):
 events=[]
 while not (m.seq.phase=="FETCH" and m.seq.micro_pc==0 and m.pc==pc):
  events.append(m.step_micro());assert len(events)<limit
 return events

def test_load_assembles_little_endian_mar_then_reads_data_memory():
 m=MicroMachine(bytes((0x12,2,0x34,0x12)));m.mem[0x1234]=0xa5
 events=_run_until_fetch(m,4)
 assert m.mar==0x1234
 assert m.r[2]==0xa5
 assert m.pc==4
 assert events[-1]["mar"]==0x1234

def test_store_assembles_little_endian_mar_and_writes_data_memory():
 m=MicroMachine(bytes((0x13,0x34,0x12,5)));m.r[5]=0x7c
 _run_until_fetch(m,4)
 assert m.mar==0x1234
 assert m.mem[0x1234]==0x7c
 assert m.pc==4

def test_load_store_leave_flags_unchanged():
 load=MicroMachine(bytes((0x12,2,0x00,0x20)));load.mem[0x2000]=1;load.flags=0x0f
 store=MicroMachine(bytes((0x13,0x00,0x20,2)));store.r[2]=1;store.flags=0x0f
 _run_until_fetch(load,4);_run_until_fetch(store,4)
 assert load.flags==0x0f and store.flags==0x0f


def test_load_and_store_address_capture_respects_different_operand_order():
 load=MicroMachine(bytes((0x12,7,0x78,0x56)));load.mem[0x5678]=0x11
 store=MicroMachine(bytes((0x13,0x78,0x56,7)));store.r[7]=0x22
 _run_until_fetch(load,4);_run_until_fetch(store,4)
 assert load.mar==store.mar==0x5678
 assert load.r[7]==0x11
 assert store.mem[0x5678]==0x22


def test_store_register_source_is_selected_by_final_operand_byte():
 m=MicroMachine(bytes((0x13,0x00,0x40,3)))
 m.r[2]=0x22;m.r[3]=0x33;m.r[4]=0x44
 _run_until_fetch(m,4)
 assert m.mem[0x4000]==0x33
 assert m.r[2:5]==[0x22,0x33,0x44]


def test_loadr_zero_extends_address_register_into_mar():
 m=MicroMachine(bytes((0x14,2,3)));m.r[3]=0xa0;m.mem[0x00a0]=0x5a
 events=_run_until_fetch(m,3)
 assert m.mar==0x00a0 and m.r[2]==0x5a and m.r[3]==0xa0
 assert events[-1]["mar"]==0x00a0

def test_storer_uses_address_register_and_distinct_source_register():
 m=MicroMachine(bytes((0x15,3,5)));m.r[3]=0xb0;m.r[5]=0x7c
 _run_until_fetch(m,3)
 assert m.mar==0x00b0 and m.mem[0x00b0]==0x7c
 assert m.r[3]==0xb0 and m.r[5]==0x7c

def test_register_indirect_memory_operations_preserve_flags():
 load=MicroMachine(bytes((0x14,2,3)));load.r[3]=0x80;load.mem[0x80]=1;load.flags=0x0f
 store=MicroMachine(bytes((0x15,3,2)));store.r[3]=0x80;store.r[2]=2;store.flags=0x0f
 _run_until_fetch(load,3);_run_until_fetch(store,3)
 assert load.flags==0x0f and store.flags==0x0f

def test_register_indirect_rejects_invalid_address_selector():
 m=MicroMachine(bytes((0x14,2,8)))
 try:_run_until_fetch(m,3)
 except ValueError as e:assert str(e)=="INVALID_OPERAND"
 else:raise AssertionError("invalid address register must fail")


def test_storer_mar_survives_later_source_selector_fetch():
 m=MicroMachine(bytes((0x15,3,5)));m.r[3]=0xb0;m.r[5]=0x7c
 events=_run_until_fetch(m,3)
 assert m.mar==0xb0
 assert m.mem[0xb0]==0x7c
 assert all(e["mar"]==0xb0 for e in events[-3:])


def test_loads_builds_effective_address_from_sp_plus_signed_offset():
 m=MicroMachine(bytes((0x16,2,0xfc)));m.sp=0x2000;m.mem[0x1ffc]=0xa5
 events=_run_until_fetch(m,3)
 assert m.mar==0x1ffc and m.r[2]==0xa5 and m.sp==0x2000
 assert events[-1]["sp"]==0x2000

def test_stores_uses_positive_stack_offset_and_distinct_source():
 m=MicroMachine(bytes((0x17,6,5)));m.sp=0x2000;m.r[5]=0x7c
 _run_until_fetch(m,3)
 assert m.mar==0x2006 and m.mem[0x2006]==0x7c and m.r[5]==0x7c

def test_stack_relative_effective_address_wraps_at_16_bits():
 m=MicroMachine(bytes((0x16,1,0xff)));m.sp=0;m.mem[0xffff]=0x42
 _run_until_fetch(m,3)
 assert m.mar==0xffff and m.r[1]==0x42

def test_stack_relative_memory_operations_preserve_sp_and_flags():
 load=MicroMachine(bytes((0x16,1,1)));load.sp=0x3000;load.mem[0x3001]=9;load.flags=0x0f
 store=MicroMachine(bytes((0x17,0xff,1)));store.sp=0x3000;store.r[1]=8;store.flags=0x0f
 _run_until_fetch(load,3);_run_until_fetch(store,3)
 assert load.sp==store.sp==0x3000
 assert load.flags==store.flags==0x0f
 assert store.mem[0x2fff]==8


def test_immediate_alu_microprograms_use_literal_operand_and_match_flags():
 cases=((0x21,0xff,1,0x00,0x05),(0x23,0,1,0xff,0x02))
 for op,a,imm,result,flags in cases:
  m=MicroMachine(bytes((op,2,imm)));m.r[2]=a
  _run_until_fetch(m,3)
  assert m.r[2]==result and m.flags==flags

def test_cmpi_updates_flags_without_writing_register():
 m=MicroMachine(bytes((0x25,2,5)));m.r[2]=5
 _run_until_fetch(m,3)
 assert m.r[2]==5 and m.flags==0x05

def test_immediate_alu_rejects_invalid_destination_selector():
 m=MicroMachine(bytes((0x21,8,1)))
 try:_run_until_fetch(m,3)
 except ValueError as e:assert str(e)=="INVALID_OPERAND"
 else:raise AssertionError("invalid immediate ALU register must fail")


def test_branch_microprograms_taken_and_not_taken():
 cases=((0x30,0,True),(0x31,1,True),(0x31,0,False),(0x32,0,True),(0x33,4,True),(0x34,4,False),(0x35,2,True),(0x36,2,False))
 for op,flags,taken in cases:
  m=MicroMachine(bytes((op,0x34,0x12)));m.flags=flags
  target=0x1234 if taken else 3
  _run_until_fetch(m,target)
  assert m.pc==target and m.flags==flags

def test_branch_target_is_little_endian_and_wrap_safe():
 m=MicroMachine(bytes((0x30,0xfe,0xff)))
 _run_until_fetch(m,0xfffe)
 assert m.mar==0xfffe and m.pc==0xfffe


def test_enter_leave_adjust_sp_and_preserve_flags():
 enter=MicroMachine(bytes((0x18,0x20)));enter.sp=0x0010;enter.flags=0x0f
 _run_until_fetch(enter,2);assert enter.sp==0xfff0 and enter.flags==0x0f
 leave=MicroMachine(bytes((0x19,0x20)));leave.sp=0xfff0;leave.flags=0x0f
 _run_until_fetch(leave,2);assert leave.sp==0x0010 and leave.flags==0x0f

def test_push_decrements_before_write_and_pop_reads_before_increment():
 push=MicroMachine(bytes((0x40,3)));push.sp=0x2000;push.r[3]=0xa5
 _run_until_fetch(push,2);assert push.sp==0x1fff and push.mem[0x1fff]==0xa5
 pop=MicroMachine(bytes((0x41,3)));pop.sp=0x1fff;pop.mem[0x1fff]=0x5a
 _run_until_fetch(pop,2);assert pop.r[3]==0x5a and pop.sp==0x2000

def test_push_pop_preserve_flags_and_wrap_stack_pointer():
 push=MicroMachine(bytes((0x40,0)));push.sp=0;push.r[0]=7;push.flags=0x0f
 _run_until_fetch(push,2);assert push.sp==0xffff and push.mem[0xffff]==7 and push.flags==0x0f
 pop=MicroMachine(bytes((0x41,0)));pop.sp=0xffff;pop.mem[0xffff]=9;pop.flags=0x0f
 _run_until_fetch(pop,2);assert pop.sp==0 and pop.r[0]==9 and pop.flags==0x0f

def test_push_pop_reject_invalid_register_selector():
 for op in (0x40,0x41):
  m=MicroMachine(bytes((op,8)))
  try:_run_until_fetch(m,2)
  except ValueError as e:assert str(e)=="INVALID_OPERAND"
  else:raise AssertionError("invalid stack register must fail")


def test_call_pushes_return_address_and_jumps():
 m=MicroMachine(bytes((0x38,0x34,0x12)));m.sp=0x2000;m.flags=0x0f
 _run_until_fetch(m,0x1234)
 assert m.sp==0x1ffe and m.mem[0x1fff]==0 and m.mem[0x1ffe]==3
 assert m.flags==0x0f

def test_ret_pops_low_then_high_and_restores_pc():
 m=MicroMachine(bytes((0x39,)));m.sp=0x1ffe;m.mem[0x1ffe]=0x78;m.mem[0x1fff]=0x56;m.flags=0x0f
 _run_until_fetch(m,0x5678)
 assert m.sp==0x2000 and m.pc==0x5678 and m.flags==0x0f

def test_call_ret_round_trip():
 m=MicroMachine(bytes((0x38,0x06,0x00,0x01,0,0,0x39)));m.sp=0x3000
 _run_until_fetch(m,6);assert m.sp==0x2ffe
 _run_until_fetch(m,3);assert m.sp==0x3000 and m.pc==3


def test_control_store_covers_complete_isa_v0_opcode_set():
 expected={0x00,0x01,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,
           0x20,0x21,0x22,0x23,0x24,0x25,0x28,0x29,0x2a,0x2b,0x2c,0x2d,
           0x30,0x31,0x32,0x33,0x34,0x35,0x36,0x38,0x39,0x40,0x41}
 assert set(OPCODE_NAMES)==expected
 assert {OPCODE_NAMES[op] for op in expected}==set(CONTROL_STORE)
