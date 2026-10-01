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
