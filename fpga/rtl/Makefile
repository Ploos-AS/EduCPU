IVERILOG ?= iverilog
VVP ?= vvp
YOSYS ?= yosys
NEXTPNR ?= nextpnr-ice40

.PHONY: test bringup-test loader-test serial-loader-test serial-e2e-test synth machine-synth up5k machine-up5k spram-up5k upduino-v31 upduino-v31-loader clean

test:
	$(IVERILOG) -g2012 -o simv educpu_core.sv tb_educpu_core.sv
	$(VVP) simv

bringup-test:
	$(IVERILOG) -g2012 -o bringup-simv educpu_core.sv educpu_bringup_rom.sv tb_upduino_bringup.sv
	$(VVP) bringup-simv

loader-test:
	$(IVERILOG) -g2012 -o loader-simv educpu_core.sv educpu_loader_mux.sv tb_loader.sv
	$(VVP) loader-simv

serial-loader-test:
	$(IVERILOG) -g2012 -o serial-loader-simv educpu_serial_loader.sv tb_serial_loader.sv
	$(VVP) serial-loader-simv

serial-e2e-test:
	$(IVERILOG) -g2012 -o serial-e2e-simv educpu_core.sv educpu_loader_mux.sv educpu_uart_rx.sv educpu_serial_loader.sv tb_serial_e2e.sv
	$(VVP) serial-e2e-simv

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

upduino-v31-loader:
	$(YOSYS) -q -p 'read_verilog -lib -specify +/ice40/cells_sim.v; read_verilog -sv educpu_core.sv educpu_loader_mux.sv educpu_uart_rx.sv educpu_serial_loader.sv educpu_up5k_spram.sv ../boards/upduino-v3.1/educpu_upduino_v31_loader.sv; hierarchy -check -top educpu_upduino_v31_loader; proc; opt; check; synth_ice40 -top educpu_upduino_v31_loader -json educpu_upduino_v31_loader.json'
	$(NEXTPNR) --up5k --package sg48 --json educpu_upduino_v31_loader.json --pcf ../boards/upduino-v3.1/upduino_v31.pcf --asc educpu_upduino_v31_loader.asc --report educpu_upduino_v31_loader-report.json
	icepack educpu_upduino_v31_loader.asc educpu_upduino_v31_loader.bin

machine-up5k: machine-synth
	$(NEXTPNR) --up5k --package sg48 --json educpu_machine.json --asc educpu_machine.asc --freq 12 --report educpu_machine-report.json --pcf-allow-unconstrained

clean:
	rm -f simv bringup-simv loader-simv educpu_core.json educpu_machine.json educpu_core.asc educpu_core-report.json educpu_machine.asc educpu_machine-report.json educpu_up5k_machine.json educpu_up5k_machine.asc educpu_up5k_machine-report.json educpu_upduino_v31.json educpu_upduino_v31.asc educpu_upduino_v31.bin educpu_upduino_v31-report.json
