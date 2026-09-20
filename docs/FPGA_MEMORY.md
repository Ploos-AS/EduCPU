# FPGA memory subsystem contract

## Purpose

The qualified `educpu_core` currently exposes a simple byte memory bus with combinational read data. That is useful for ISA qualification, but the physical FPGA machine needs a memory implementation that maps cleanly to iCE40 block RAM/SPRAM.

This document freezes the next implementation boundary before changing RTL.

## Architectural requirement

Memory timing is **not** part of EduCPU ISA v0. Programs observe byte reads/writes and instruction semantics, not whether a physical memory needs one or more FPGA clocks. Therefore a board wrapper or memory adapter may add wait cycles without changing the ISA, provided architectural state changes remain identical to the reference CPU.

## M0.10 plan

1. Preserve the existing qualified CPU/reference differential suite as the semantic oracle.
2. Introduce an explicit request/ready byte-memory interface at the core boundary.
3. Make fetch, load, stack and RET reads wait for a completed read transaction.
4. Make STORE, PUSH and CALL writes complete exactly once.
5. Add a synchronous 64 KiB teaching-memory wrapper for simulation.
6. Re-run every ISA differential vector against the synchronous-memory configuration.
7. Only then map board-specific storage to UP5K BRAM/SPRAM/external memory.

## Proposed core bus

- `mem_valid`: request is active.
- `mem_we`: request is a write when high, read when low.
- `mem_addr[15:0]`: byte address.
- `mem_wdata[7:0]`: write byte.
- `mem_rdata[7:0]`: completed read byte.
- `mem_ready`: current request completed.

The core must hold request address/data/control stable while `mem_valid && !mem_ready`.

## Qualification gate

The interface migration is complete only when all existing smoke tests and all 20 opcode-complete reference↔RTL differential programs pass with at least one-cycle synchronous memory latency. Full-memory-state comparison remains required.

## UP5K note

The existing board-neutral core already place-and-routes on iCE40UP5K SG48 at 932/5280 logic cells (17%) and 20.68 MHz estimated maximum frequency, with a 12 MHz target. Those figures exclude the machine memory and are therefore a CPU-core baseline, not final board utilization.

## M0.10 qualification status

The first request/ready migration is qualified in FPGA CI #68.

- core stalls architectural state until `mem_ready`
- differential memory model uses a delayed request/completion transaction
- duplicate request acceptance found by the first run was fixed before qualification
- all 20 opcode-complete reference↔RTL programs PASS
- full-memory signatures still match
- iCE40UP5K place-and-route still PASSes at the 12 MHz target
- post-handshake core utilization: 954/5280 logic cells (18%)

This qualifies the handshake semantics. The next gate is a synthesizable synchronous memory wrapper rather than a testbench-only memory model.
