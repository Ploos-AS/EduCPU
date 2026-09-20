IVERILOG ?= iverilog
VVP ?= vvp
YOSYS ?= yosys
NEXTPNR ?= nextpnr-ice40

.PHONY: test synth up5k clean

test:
	$(IVERILOG) -g2012 -o simv educpu_core.sv tb_educpu_core.sv
	$(VVP) simv

synth:
	$(YOSYS) -q -p 'read_verilog -sv educpu_core.sv; hierarchy -check -top educpu_core; proc; opt; check; synth_ice40 -top educpu_core -json educpu_core.json; stat'

up5k: synth
	$(NEXTPNR) --up5k --package sg48 --json educpu_core.json --asc educpu_core.asc --freq 12 --report educpu_core-report.json --pcf-allow-unconstrained

clean:
	rm -f simv educpu_core.json educpu_core.asc educpu_core-report.json
