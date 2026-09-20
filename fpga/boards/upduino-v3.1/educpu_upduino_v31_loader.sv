// UPduino v3.x serial-loader wrapper for EduCPU.
// FTDI serial RX loads a program into SPRAM; CPU is held reset until complete.
module educpu_upduino_v31_loader (
    input logic serial_rxd,
    output logic led_r, output logic led_g, output logic led_b
);
    logic clk; logic [3:0] por=4'hf; logic por_reset;
    logic [7:0] rx_data,load_data,cpu_rdata,ram_rdata,cpu_wdata,mem_wdata;
    logic rx_valid,load_mode,load_valid,load_ready,started,protocol_error;
    logic cpu_valid,cpu_we,cpu_ready,mem_valid,mem_we,ram_ready,halted,trap;
    logic [15:0] load_addr,cpu_addr,mem_addr;
    SB_HFOSC #(.CLKHF_DIV("0b10")) hfosc(.CLKHFPU(1'b1),.CLKHFEN(1'b1),.CLKHF(clk));
    always_ff @(posedge clk) if(por!=0) por<=por-1'b1;
    assign por_reset=(por!=0);
    educpu_uart_rx #(.CLKS_PER_BIT(104)) uart(.clk(clk),.reset(por_reset),.rx(serial_rxd),.data(rx_data),.data_valid(rx_valid));
    educpu_serial_loader loader(.clk(clk),.reset(por_reset),.rx_data(rx_data),.rx_valid(rx_valid),
      .load_mode(load_mode),.load_valid(load_valid),.load_addr(load_addr),.load_data(load_data),
      .load_ready(load_ready),.started(started),.protocol_error(protocol_error));
    educpu_core cpu(.clk(clk),.reset(por_reset|load_mode),.mem_rdata(cpu_rdata),.mem_addr(cpu_addr),
      .mem_wdata(cpu_wdata),.mem_we(cpu_we),.mem_valid(cpu_valid),.mem_ready(cpu_ready),.halted(halted),.trap(trap));
    educpu_loader_mux mux(.load_mode(load_mode),.load_valid(load_valid),.load_addr(load_addr),.load_data(load_data),
      .load_ready(load_ready),.cpu_valid(cpu_valid),.cpu_we(cpu_we),.cpu_addr(cpu_addr),.cpu_wdata(cpu_wdata),
      .cpu_rdata(cpu_rdata),.cpu_ready(cpu_ready),.mem_valid(mem_valid),.mem_we(mem_we),.mem_addr(mem_addr),
      .mem_wdata(mem_wdata),.mem_rdata(ram_rdata),.mem_ready(ram_ready));
    educpu_up5k_spram ram(.clk(clk),.reset(por_reset),.valid(mem_valid),.we(mem_we),.addr(mem_addr),
      .wdata(mem_wdata),.rdata(ram_rdata),.ready(ram_ready));
    assign led_r=!(trap|protocol_error);
    assign led_g=!load_mode;
    assign led_b=!(halted&&!trap);
endmodule
