from edusim_experimental import ExperimentalSimulator


def test_experimental_simulator_exposes_input_transaction_and_state_change():
 sim=ExperimentalSimulator(bytes((0xe0,2,0x10)))
 sim.register_io(0x10,read=lambda:0xa5)
 event=sim.step_event()
 assert event["io"]=={"direction":"in","port":0x10,"value":0xa5,"mapped":True}
 assert "R2: 00->A5" in event["changes"]
 text=sim.format_event(event)
 assert "I/O IN port=10 value=A5 mapped=yes" in text
 assert "R2: 00->A5" in text


def test_experimental_simulator_exposes_unmapped_output():
 sim=ExperimentalSimulator(bytes((0xe1,0x77,3)))
 sim.cpu.r[3]=0x5a
 event=sim.step_event()
 assert event["io"]=={"direction":"out","port":0x77,"value":0x5a,"mapped":False}
 assert "I/O OUT port=77 value=5A mapped=no" in sim.format_event(event)


def test_non_io_step_has_no_io_event():
 sim=ExperimentalSimulator(bytes((0x00,)))
 event=sim.step_event()
 assert event["io"] is None


def test_in_micro_plan_explains_complete_cpu_to_device_path():
 sim=ExperimentalSimulator(bytes((0xe0,2,0x10)))
 phases=sim.micro_plan()
 assert [p for p,_ in phases]==["FETCH","DECODE","OPERAND","OPERAND","I/O READ","TRANSFER","COMMIT"]
 assert "R2" in phases[2][1]
 assert "10" in phases[3][1]
 assert "FLAGS unchanged" in phases[-1][1]

def test_out_micro_plan_explains_device_commit():
 sim=ExperimentalSimulator(bytes((0xe1,0x20,3)))
 phases=sim.micro_plan()
 assert [p for p,_ in phases]==["FETCH","DECODE","OPERAND","OPERAND","I/O WRITE","TRANSFER","COMMIT"]
 assert "R3" in phases[3][1]
 assert "20" in phases[4][1]
 assert "device observes output byte" in phases[-1][1]

def test_movi_micro_plan_can_be_predicted_before_step_and_compared_after():
 sim=ExperimentalSimulator(bytes((0x11,2,0xa5)))
 plan=sim.micro_plan()
 assert [p for p,_ in plan]==["FETCH","DECODE","OPERAND","OPERAND","TRANSFER","COMMIT"]
 assert "A5 -> R2" in plan[-2][1]
 event=sim.step_event()
 assert "R2: 00->A5" in event["changes"]
 assert event["after"]["flags"]==event["before"]["flags"]


def test_cmp_plan_predicts_flags_without_register_write():
 sim=ExperimentalSimulator(bytes((0x24,1,3)))
 sim.cpu.r[1]=5;sim.cpu.r[3]=5
 plan=sim.micro_plan()
 assert plan[-1][1]=="no register write"
 before=sim.cpu.r.copy()
 event=sim.step_event()
 assert event["after"]["registers"]==before
 assert "FLAGS: 00->05" in event["changes"]
