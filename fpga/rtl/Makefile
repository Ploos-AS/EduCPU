IVERILOG ?= iverilog
VVP ?= vvp

.PHONY: test clean

test:
	$(IVERILOG) -g2012 -o simv educpu_core.sv tb_educpu_core.sv
	$(VVP) simv

clean:
	rm -f simv
