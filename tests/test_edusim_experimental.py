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
