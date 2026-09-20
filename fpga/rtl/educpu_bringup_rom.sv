// Read-only boot overlay for physical bring-up.
// Program at reset vector:
//   MOVI R0, 0x2a
//   MOVI R1, 0x2a
//   CMP  R0, R1
//   JNZ  fail
//   HALT
// fail:
//   invalid opcode -> TRAP
module educpu_bringup_rom (
    input  logic [15:0] addr,
    output logic [7:0] data,
    output logic        hit
);
    always_comb begin
        hit = (addr < 16'd14);
        case (addr)
            16'd0:  data = 8'h11; // MOVI
            16'd1:  data = 8'h00; // R0
            16'd2:  data = 8'h2a;
            16'd3:  data = 8'h11; // MOVI
            16'd4:  data = 8'h01; // R1
            16'd5:  data = 8'h2a;
            16'd6:  data = 8'h24; // CMP
            16'd7:  data = 8'h00; // R0
            16'd8:  data = 8'h01; // R1
            16'd9:  data = 8'h32; // JNZ
            16'd10: data = 8'h0d; // fail = 0x000d
            16'd11: data = 8'h00;
            16'd12: data = 8'h01; // HALT
            16'd13: data = 8'hff; // invalid opcode -> TRAP
            default:data = 8'hff;
        endcase
    end
endmodule
