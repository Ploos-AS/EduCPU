IVERILOG ?= iverilog
VVP ?= vvp
YOSYS ?= yosys

.PHONY: test synth clean

test:
	$(IVERILOG) -g2012 -o simv educpu_core.sv tb_educpu_core.sv
	$(VVP) simv

synth:
	$(YOSYS) -q -p 'read_verilog -sv educpu_core.sv; hierarchy -check -top educpu_core; proc; opt; check; synth_ice40 -top educpu_core -json educpu_core.json; stat'

clean:
	rm -f simv educpu_core.json
