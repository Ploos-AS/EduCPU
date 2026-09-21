// EduCPU serial loader protocol v1: versioned frame + CRC-16/CCITT-FALSE.
// Frame: 55 AA 01 len_lo len_hi payload crc_lo crc_hi.
module educpu_serial_loader_v1(
 input logic clk,input logic reset,input logic [7:0] rx_data,input logic rx_valid,
 output logic load_mode,output logic load_valid,output logic [15:0] load_addr,
 output logic [7:0] load_data,input logic load_ready,
 output logic started,output logic protocol_error,output logic accepted
);
 typedef enum logic [3:0] {S55,SAA,SVER,SLENL,SLENH,SPAY,SCRCLO,SCRCHI,SDONE,SERR} st_t;
 st_t st; logic [15:0] len_q,remaining_q,crc_q; logic [7:0] crc_lo_q;
 function automatic [15:0] crc_byte(input [15:0] c,input [7:0] d);
   integer i; reg [15:0] x;
   begin x=c^({d,8'h00}); for(i=0;i<8;i=i+1) x=x[15]?((x<<1)^16'h1021):(x<<1); crc_byte=x; end
 endfunction
 assign load_mode=(st!=SDONE);
 assign load_valid=(st==SPAY)&&rx_valid;
 assign load_data=rx_data;
 always_ff @(posedge clk) begin
  if(reset) begin st<=S55;len_q<=0;remaining_q<=0;load_addr<=0;crc_q<=16'hffff;started<=0;protocol_error<=0;accepted<=0;crc_lo_q<=0; end
  else begin
   started<=0; accepted<=0;
   if(rx_valid) case(st)
    S55: if(rx_data==8'h55) st<=SAA;
    SAA: if(rx_data==8'haa) st<=SVER; else st<=S55;
    SVER: if(rx_data==8'h01) begin crc_q<=crc_byte(16'hffff,rx_data);st<=SLENL;end else begin protocol_error<=1;st<=SERR;end
    SLENL: begin len_q[7:0]<=rx_data;crc_q<=crc_byte(crc_q,rx_data);st<=SLENH;end
    SLENH: begin
      len_q[15:8]<=rx_data;crc_q<=crc_byte(crc_q,rx_data);
      remaining_q<={rx_data,len_q[7:0]};load_addr<=0;
      if({rx_data,len_q[7:0]}==0) begin protocol_error<=1;st<=SERR;end else st<=SPAY;
    end
    SPAY: begin
      crc_q<=crc_byte(crc_q,rx_data);
      if(remaining_q==1) st<=SCRCLO; else begin remaining_q<=remaining_q-1'b1;load_addr<=load_addr+1'b1;end
    end
    SCRCLO: begin crc_lo_q<=rx_data;st<=SCRCHI;end
    SCRCHI: begin
      $display("V1_CRC calculated=%04h received=%02h%02h",crc_q,rx_data,crc_lo_q);
      if({rx_data,crc_lo_q}==crc_q) begin accepted<=1;started<=1;st<=SDONE;end else begin protocol_error<=1;st<=SERR;end
    end
    default: ;
   endcase
  end
 end
endmodule
