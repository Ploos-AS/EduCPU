module tb_differential;
    logic clk=0, reset=1;
    logic [7:0] mem[0:65535];
    logic [7:0] mem_rdata;
    logic [15:0] mem_addr;
    logic [7:0] mem_wdata;
    logic mem_we, mem_valid, halted, trap;
    logic mem_ready = 1'b0;
    logic pending = 1'b0;
    logic wait_release = 1'b0;
    logic [15:0] pending_addr;
    logic pending_we;
    logic [7:0] pending_wdata;
    integer i, cycles;
    logic [31:0] mem_hash;
    reg [1023:0] image;

    always @(posedge clk) begin
        mem_ready <= 1'b0;
        if (pending) begin
            mem_rdata <= mem[pending_addr];
            if (pending_we) mem[pending_addr] <= pending_wdata;
            mem_ready <= 1'b1;
            pending <= 1'b0;
            wait_release <= 1'b1;
        end else if (wait_release) begin
            // Do not accept the still-asserted request in the completion cycle.
            // Give the core one cycle to advance and present the next address.
            wait_release <= 1'b0;
        end else if (mem_valid) begin
            pending_addr <= mem_addr;
            pending_we <= mem_we;
            pending_wdata <= mem_wdata;
            pending <= 1'b1;
        end
    end
    always #5 clk=~clk;

    educpu_core dut(.clk,.reset,.mem_rdata,.mem_addr,.mem_wdata,.mem_we,.mem_valid,.mem_ready,.halted,.trap);

    initial begin
        for(i=0;i<65536;i=i+1) mem[i]=0;
        if(!$value$plusargs("IMAGE=%s",image)) begin $display("missing +IMAGE"); $fatal(1); end
        $readmemh(image,mem);
        @(posedge clk); #1; reset=0;
        cycles=0;
        while(!halted && !trap && cycles<1000) begin @(posedge clk); #1; cycles=cycles+1; end
        $write("pc=%04x sp=%04x flags=%02x halted=%0d trap=%0d regs=",dut.pc,dut.sp,dut.flags,halted,trap);
        for(i=0;i<8;i=i+1) begin $write("%02x",dut.r[i]); if(i!=7)$write(" "); end
        mem_hash=32'h811c9dc5;
        for(i=0;i<65536;i=i+1) begin
            mem_hash=(mem_hash ^ mem[i]) * 32'h01000193;
        end
        $write(" memhash=%08x\n",mem_hash);
        if(cycles>=1000)$fatal(1,"cycle limit");
        $finish;
    end
endmodule
