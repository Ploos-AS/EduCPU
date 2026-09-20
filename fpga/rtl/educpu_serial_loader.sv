// Serial loader protocol v0 parser.
// 55 AA <len-lo> <len-hi> <payload>. Payload is written at address zero upward.
module educpu_serial_loader (
    input logic clk, input logic reset,
    input logic [7:0] rx_data, input logic rx_valid,
    output logic load_mode, output logic load_valid,
    output logic [15:0] load_addr, output logic [7:0] load_data,
    input logic load_ready,
    output logic started, output logic protocol_error
);
    typedef enum logic [2:0] {SYNC55,SYNCAA,LEN_LO,LEN_HI,PAYLOAD,DONE} state_t;
    state_t state;
    logic [15:0] length, remaining;
    logic pending;

    assign load_mode = (state != DONE);
    assign load_valid = pending;

    always_ff @(posedge clk) begin
      if (reset) begin
        state<=SYNC55; length<=0; remaining<=0; load_addr<=0; load_data<=0;
        pending<=0; started<=0; protocol_error<=0;
      end else begin
        started<=0;
        if (pending && load_ready) begin
          pending<=0;
          if (remaining == 16'd1) begin state<=DONE; started<=1; remaining<=0; end
          else begin remaining<=remaining-1'b1; load_addr<=load_addr+1'b1; end
        end
        if (rx_valid && !pending) begin
          case(state)
            SYNC55: if(rx_data==8'h55) state<=SYNCAA;
            SYNCAA: if(rx_data==8'haa) state<=LEN_LO; else state<=SYNC55;
            LEN_LO: begin length[7:0]<=rx_data; state<=LEN_HI; end
            LEN_HI: begin
              length[15:8]<=rx_data;
              remaining<={rx_data,length[7:0]};
              load_addr<=0;
              if ({rx_data,length[7:0]}==0) begin protocol_error<=1; state<=SYNC55; end
              else state<=PAYLOAD;
            end
            PAYLOAD: begin load_data<=rx_data; pending<=1; end
            default: ;
          endcase
        end
      end
    end
endmodule
