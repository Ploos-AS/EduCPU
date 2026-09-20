IVERILOG ?= iverilog
VVP ?= vvp
YOSYS ?= yosys
NEXTPNR ?= nextpnr-ice40

.PHONY: test synth machine-synth up5k machine-up5k clean

test:
	$(IVERILOG) -g2012 -o simv educpu_core.sv tb_educpu_core.sv
	$(VVP) simv

synth:
	$(YOSYS) -q -p 'read_verilog -sv educpu_core.sv; hierarchy -check -top educpu_core; proc; opt; check; synth_ice40 -top educpu_core -json educpu_core.json; stat'

machine-synth:
	$(YOSYS) -q -p 'read_verilog -sv educpu_core.sv educpu_sync_ram.sv educpu_machine.sv; hierarchy -check -top educpu_machine; proc; memory; opt; check; synth_ice40 -top educpu_machine -json educpu_machine.json; stat'


up5k: synth
	$(NEXTPNR) --up5k --package sg48 --json educpu_core.json --asc educpu_core.asc --freq 12 --report educpu_core-report.json --pcf-allow-unconstrained

machine-up5k: machine-synth
	$(NEXTPNR) --up5k --package sg48 --json educpu_machine.json --asc educpu_machine.asc --freq 12 --report educpu_machine-report.json --pcf-allow-unconstrained

clean:
	rm -f simv educpu_core.json educpu_machine.json educpu_core.asc educpu_core-report.json educpu_machine.asc educpu_machine-report.json
