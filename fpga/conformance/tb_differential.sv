module tb_differential;
    logic clk=0, reset=1;
    logic [7:0] mem[0:65535];
    logic [7:0] mem_rdata;
    logic [15:0] mem_addr;
    logic [7:0] mem_wdata;
    logic mem_we, halted, trap;
    integer i, cycles;
    reg [1023:0] image;

    assign mem_rdata=mem[mem_addr];
    always @(posedge clk) if(mem_we) mem[mem_addr] <= mem_wdata;
    always #5 clk=~clk;

    educpu_core dut(.clk,.reset,.mem_rdata,.mem_addr,.mem_wdata,.mem_we,.halted,.trap);

    initial begin
        for(i=0;i<65536;i=i+1) mem[i]=0;
        if(!$value$plusargs("IMAGE=%s",image)) begin $display("missing +IMAGE"); $fatal(1); end
        $readmemh(image,mem);
        @(posedge clk); #1; reset=0;
        cycles=0;
        while(!halted && !trap && cycles<1000) begin @(posedge clk); #1; cycles=cycles+1; end
        $write("pc=%04x sp=%04x flags=%02x halted=%0d trap=%0d regs=",dut.pc,dut.sp,dut.flags,halted,trap);
        for(i=0;i<8;i=i+1) begin $write("%02x",dut.r[i]); if(i!=7)$write(" "); end
        $write("\n");
        if(cycles>=1000)$fatal(1,"cycle limit");
        $finish;
    end
endmodule
