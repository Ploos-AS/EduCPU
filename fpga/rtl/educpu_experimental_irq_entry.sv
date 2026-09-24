// M10.1 experimental architectural IRQ stack sequencer.
// Kept separate from frozen educpu_core.sv.
module educpu_experimental_irq_entry (
 input logic clk,input logic reset,
 input logic irq_accept,input logic [15:0] irq_vector,
 input logic iret_request,
 input logic [15:0] cpu_pc,input logic [15:0] cpu_sp,input logic [7:0] cpu_flags,
 input logic [7:0] mem_rdata,input logic mem_ready,
 output logic busy,output logic mem_valid,output logic mem_we,
 output logic [15:0] mem_addr,output logic [7:0] mem_wdata,
 output logic state_write,output logic [15:0] next_pc,output logic [15:0] next_sp,
 output logic [7:0] next_flags,output logic iret_complete
);
 typedef enum logic [2:0] {IDLE,PUSH_HI,PUSH_LO,PUSH_FLAGS,POP_FLAGS,POP_LO,POP_HI} st_t;
 st_t state; logic [15:0] saved_pc; logic [15:0] work_sp; logic [7:0] saved_flags; logic [7:0] pop_flags,pop_lo;
 always_comb begin
  mem_valid=0; mem_we=0; mem_addr=work_sp; mem_wdata=0;
  case(state)
   PUSH_HI: begin mem_valid=1;mem_we=1;mem_addr=work_sp-1;mem_wdata=saved_pc[15:8];end
   PUSH_LO: begin mem_valid=1;mem_we=1;mem_addr=work_sp-1;mem_wdata=saved_pc[7:0];end
   PUSH_FLAGS: begin mem_valid=1;mem_we=1;mem_addr=work_sp-1;mem_wdata=saved_flags;end
   POP_FLAGS,POP_LO,POP_HI: begin mem_valid=1;mem_addr=work_sp;end
  endcase
 end
 always_ff @(posedge clk) begin
  if(reset) begin state<=IDLE;busy<=0;state_write<=0;iret_complete<=0; end
  else begin
   state_write<=0;iret_complete<=0;
   case(state)
    IDLE: if(irq_accept) begin saved_pc<=cpu_pc;saved_flags<=cpu_flags;work_sp<=cpu_sp;busy<=1;state<=PUSH_HI; end
          else if(iret_request) begin work_sp<=cpu_sp;busy<=1;state<=POP_FLAGS; end
    PUSH_HI: begin if(mem_ready) begin work_sp<=work_sp-1;state<=PUSH_LO;end end
    PUSH_LO: begin if(mem_ready) begin work_sp<=work_sp-1;state<=PUSH_FLAGS;end end
    PUSH_FLAGS: begin if(mem_ready) begin next_sp<=work_sp-1;next_pc<=irq_vector;next_flags<=saved_flags;state_write<=1;busy<=0;state<=IDLE;end end
    POP_FLAGS: beginif(mem_ready)begin pop_flags<=mem_rdata;work_sp<=work_sp+1;state<=POP_LO;end end
    POP_LO: beginif(mem_ready)begin pop_lo<=mem_rdata;work_sp<=work_sp+1;state<=POP_HI;end end
    POP_HI: beginif(mem_ready)begin next_flags<=pop_flags;next_pc<={mem_rdata,pop_lo};next_sp<=work_sp+1;state_write<=1;iret_complete<=1;busy<=0;state<=IDLE;end end
   endcase
  end
 end
endmodule
