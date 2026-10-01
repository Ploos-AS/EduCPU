from reference.experimental_microcode import instruction_plan

def phases(plan): return [x[0] for x in plan]

def test_nop_and_halt_plans_are_explicit():
 assert phases(instruction_plan(bytes([0x00]),0))==["FETCH","DECODE","COMMIT"]
 assert phases(instruction_plan(bytes([0x01]),0))==["FETCH","DECODE","CONTROL","COMMIT"]

def test_movi_exposes_immediate_transfer():
 p=instruction_plan(bytes([0x11,2,0xa5]),0)
 assert phases(p)==["FETCH","DECODE","OPERAND","OPERAND","TRANSFER","COMMIT"]
 assert "A5 -> R2" in p[-2][1]

def test_add_and_cmp_distinguish_register_commit():
 add=instruction_plan(bytes([0x20,1,3]),0)
 cmp_=instruction_plan(bytes([0x24,1,3]),0)
 assert phases(add)==["FETCH","DECODE","OPERAND","OPERAND","ALU","FLAGS","COMMIT"]
 assert add[-1][1]=="result -> R1"
 assert cmp_[-1][1]=="no register write"

def test_load_and_store_decode_little_endian_address():
 load=instruction_plan(bytes([0x12,2,0x34,0x12]),0)
 store=instruction_plan(bytes([0x13,0x34,0x12,2]),0)
 assert "1234" in load[3][1]
 assert "memory[1234]" in load[4][1]
 assert "1234" in store[2][1]
 assert "R2" in store[3][1]

def test_conditional_branch_names_flag_condition():
 p=instruction_plan(bytes([0x32,0x34,0x12]),0)
 assert phases(p)==["FETCH","DECODE","ADDRESS","CONTROL","COMMIT"]
 assert p[3][1]=="test condition Z=0"

def test_stack_and_call_ret_make_order_visible():
 push=instruction_plan(bytes([0x40,4]),0)
 call=instruction_plan(bytes([0x38,0x00,0x80]),0)
 ret=instruction_plan(bytes([0x39]),0)
 assert phases(push)==["FETCH","DECODE","OPERAND","STACK","MEMORY WRITE","COMMIT"]
 assert phases(call)==["FETCH","DECODE","ADDRESS","CONTROL","STACK","STACK","COMMIT"]
 assert phases(ret)==["FETCH","DECODE","MEMORY READ","MEMORY READ","STACK","COMMIT"]

def test_experimental_io_still_uses_same_teaching_model():
 p=instruction_plan(bytes([0xe0,2,0x10]),0)
 assert phases(p)==["FETCH","DECODE","OPERAND","OPERAND","I/O READ","TRANSFER","COMMIT"]

def test_every_isa_v0_opcode_has_a_concrete_plan():
 samples={
  0x00:[],0x01:[],0x10:[0,1],0x11:[0,1],0x12:[0,0,0],0x13:[0,0,0],
  0x14:[0,1],0x15:[0,1],0x16:[0,0],0x17:[0,0],0x18:[1],0x19:[1],
  0x20:[0,1],0x21:[0,1],0x22:[0,1],0x23:[0,1],0x24:[0,1],0x25:[0,1],
  0x28:[0,1],0x29:[0,1],0x2a:[0,1],0x2b:[0],0x2c:[0],0x2d:[0],
  0x30:[0,0],0x31:[0,0],0x32:[0,0],0x33:[0,0],0x34:[0,0],0x35:[0,0],0x36:[0,0],
  0x38:[0,0],0x39:[],0x40:[0],0x41:[0],
 }
 assert len(samples)==36
 for op,operands in samples.items():
  plan=instruction_plan(bytes([op]+operands),0)
  assert plan, f"empty plan for {op:02X}"
  assert all(phase!="UNMODELED" for phase,_ in plan), f"unmodeled {op:02X}"
  assert plan[0][0]=="FETCH" and plan[1][0]=="DECODE"


def test_indirect_stack_relative_and_shift_plans_expose_their_special_mechanism():
 loadr=instruction_plan(bytes([0x14,2,5]),0)
 loads=instruction_plan(bytes([0x16,2,0xfc]),0)
 shl=instruction_plan(bytes([0x2c,2]),0)
 assert any("address register R5" in text for _,text in loadr)
 assert any("SP -4" in text for _,text in loads)
 assert any("bit 7 becomes carry" in text for _,text in shl)
