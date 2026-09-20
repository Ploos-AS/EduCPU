// Board-neutral byte loader front-end.
// Owns the memory write port while load_mode is asserted and keeps the CPU reset.
// Transport (UART/USB/etc.) is intentionally outside this module.
module educpu_loader_mux (
    input  logic        load_mode,
    input  logic        load_valid,
    input  logic [15:0] load_addr,
    input  logic [7:0]  load_data,
    output logic        load_ready,

    input  logic        cpu_valid,
    input  logic        cpu_we,
    input  logic [15:0] cpu_addr,
    input  logic [7:0]  cpu_wdata,
    output logic [7:0]  cpu_rdata,
    output logic        cpu_ready,

    output logic        mem_valid,
    output logic        mem_we,
    output logic [15:0] mem_addr,
    output logic [7:0]  mem_wdata,
    input  logic [7:0]  mem_rdata,
    input  logic        mem_ready
);
    always_comb begin
        mem_valid = load_mode ? load_valid : cpu_valid;
        mem_we    = load_mode ? 1'b1      : cpu_we;
        mem_addr  = load_mode ? load_addr : cpu_addr;
        mem_wdata = load_mode ? load_data : cpu_wdata;

        load_ready = load_mode && mem_ready;
        cpu_ready  = !load_mode && mem_ready;
        cpu_rdata  = mem_rdata;
    end
endmodule
