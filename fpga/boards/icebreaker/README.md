# iCEBreaker secondary target

This directory contains the secondary EduCPU iCE40UP5K target for iCEBreaker-class hardware. It deliberately reuses the board-neutral core, bring-up ROM and UP5K SPRAM implementation.

The wrapper expects the board 12 MHz clock as `clk_12mhz`, an active-low reset as `reset_n`, and exposes a single active-high HALT/no-TRAP status LED.

Pin constraints are intentionally not guessed. Add a board-revision-specific PCF only after verifying the exact iCEBreaker hardware revision and its official pinout. Until then this target is a synthesis/portability target, not a physical qualification claim.
