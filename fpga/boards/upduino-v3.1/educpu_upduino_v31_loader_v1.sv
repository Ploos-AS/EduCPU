// UPduino v3.x protocol-v1 serial loader with bidirectional status.
module educpu_upduino_v31_loader_v1(
 input logic serial_rxd, output logic serial_txd,
 output logic led_r,output logic led_g,output logic led_b);
 logic clk; logic [3:0] por=4'hf; logic rst;
 logic [7:0] rx_data,load_data,cpu_rdata,ram_rdata,cpu_wdata,mem_wdata,tx_data;
 logic rx_valid,load_mode,load_valid,load_ready,started,protocol_error,accepted;
 logic cpu_valid,cpu_we,cpu_ready,mem_valid,mem_we,ram_ready,halted,trap,tx_valid,tx_ready;
 logic [15:0] load_addr,cpu_addr,mem_addr;
 SB_HFOSC #(.CLKHF_DIV("0b10")) hf(.CLKHFPU(1'b1),.CLKHFEN(1'b1),.CLKHF(clk));
 always_ff @(posedge clk) if(por!=0) por<=por-1'b1; assign rst=(por!=0);
 educpu_uart_rx #(.CLKS_PER_BIT(104)) urx(.clk(clk),.reset(rst),.rx(serial_rxd),.data(rx_data),.data_valid(rx_valid));
 educpu_serial_loader_v1 loader(.clk,.reset(rst),.rx_data,.rx_valid,.load_mode,.load_valid,.load_addr,.load_data,.load_ready,.started,.protocol_error,.accepted);
 educpu_core cpu(.clk,.reset(rst|load_mode),.mem_rdata(cpu_rdata),.mem_addr(cpu_addr),.mem_wdata(cpu_wdata),.mem_we(cpu_we),.mem_valid(cpu_valid),.mem_ready(cpu_ready),.halted,.trap);
 educpu_loader_mux mux(.load_mode,.load_valid,.load_addr,.load_data,.load_ready,.cpu_valid,.cpu_we,.cpu_addr,.cpu_wdata,.cpu_rdata,.cpu_ready,.mem_valid,.mem_we,.mem_addr,.mem_wdata,.mem_rdata(ram_rdata),.mem_ready(ram_ready));
 educpu_up5k_spram ram(.clk,.reset(rst),.valid(mem_valid),.we(mem_we),.addr(mem_addr),.wdata(mem_wdata),.rdata(ram_rdata),.ready(ram_ready));
 educpu_loader_status status(.clk,.reset(rst),.accepted,.protocol_error,.halted,.trap,.tx_ready,.tx_valid,.tx_data);
 educpu_uart_tx #(.CLKS_PER_BIT(104)) utx(.clk,.reset(rst),.data(tx_data),.valid(tx_valid),.ready(tx_ready),.tx(serial_txd));
 assign led_r=!(trap|protocol_error); assign led_g=!load_mode; assign led_b=!(halted&&!trap);
endmodule
