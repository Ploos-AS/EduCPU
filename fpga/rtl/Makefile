IVERILOG ?= iverilog
VVP ?= vvp
YOSYS ?= yosys
NEXTPNR ?= nextpnr-ice40

.PHONY: test bringup-test synth machine-synth up5k machine-up5k spram-up5k upduino-v31 clean

test:
	$(IVERILOG) -g2012 -o simv educpu_core.sv tb_educpu_core.sv
	$(VVP) simv

bringup-test:
	$(IVERILOG) -g2012 -o bringup-simv educpu_core.sv educpu_bringup_rom.sv tb_upduino_bringup.sv
	$(VVP) bringup-simv

synth:
	$(YOSYS) -q -p 'read_verilog -sv educpu_core.sv; hierarchy -check -top educpu_core; proc; opt; check; synth_ice40 -top educpu_core -json educpu_core.json; stat'

machine-synth:
	$(YOSYS) -q -p 'read_verilog -sv educpu_core.sv educpu_sync_ram.sv educpu_machine.sv; hierarchy -check -top educpu_machine; proc; memory; opt; check; synth_ice40 -top educpu_machine -json educpu_machine.json; stat'


up5k: synth
	$(NEXTPNR) --up5k --package sg48 --json educpu_core.json --asc educpu_core.asc --freq 12 --report educpu_core-report.json --pcf-allow-unconstrained

spram-up5k:
	$(YOSYS) -q -p 'read_verilog -lib -specify +/ice40/cells_sim.v; read_verilog -sv educpu_core.sv educpu_up5k_spram.sv educpu_up5k_machine.sv; hierarchy -check -top educpu_up5k_machine; proc; opt; check; synth_ice40 -top educpu_up5k_machine -json educpu_up5k_machine.json; stat'
	$(NEXTPNR) --up5k --package sg48 --json educpu_up5k_machine.json --asc educpu_up5k_machine.asc --freq 12 --report educpu_up5k_machine-report.json --pcf-allow-unconstrained

upduino-v31:
	$(YOSYS) -q -p 'read_verilog -lib -specify +/ice40/cells_sim.v; read_verilog -sv educpu_core.sv educpu_up5k_spram.sv educpu_bringup_rom.sv ../boards/upduino-v3.1/educpu_upduino_v31.sv; hierarchy -check -top educpu_upduino_v31; proc; opt; check; synth_ice40 -top educpu_upduino_v31 -json educpu_upduino_v31.json'
	$(NEXTPNR) --up5k --package sg48 --json educpu_upduino_v31.json --pcf ../boards/upduino-v3.1/upduino_v31.pcf --asc educpu_upduino_v31.asc --report educpu_upduino_v31-report.json
	icepack educpu_upduino_v31.asc educpu_upduino_v31.bin

machine-up5k: machine-synth
	$(NEXTPNR) --up5k --package sg48 --json educpu_machine.json --asc educpu_machine.asc --freq 12 --report educpu_machine-report.json --pcf-allow-unconstrained

clean:
	rm -f simv bringup-simv educpu_core.json educpu_machine.json educpu_core.asc educpu_core-report.json educpu_machine.asc educpu_machine-report.json educpu_up5k_machine.json educpu_up5k_machine.asc educpu_up5k_machine-report.json educpu_upduino_v31.json educpu_upduino_v31.asc educpu_upduino_v31.bin educpu_upduino_v31-report.json
