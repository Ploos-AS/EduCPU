from pathlib import Path

from eduasm import assemble_text
from educpu import CPU
from educ import compile_source, compile_trace, parse, Program, Function, VarDecl, Return, Call, Name
from educ_semantic import analyze, SemanticError
from educ_ir import lower
from educ_codegen import generate
from eduasm import assemble_object
from edulink import link

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "course" / "examples" / "lesson01-number-formats.eduasm"


def test_lesson01_number_formats_assemble_identically():
    data, _, rows = assemble_text(FIXTURE.read_text())
    # MOVI is opcode, register, immediate. All three immediate bytes must be 0x2A.
    assert data == bytes([
        0x11, 0x00, 0x2A,
        0x11, 0x01, 0x2A,
        0x11, 0x02, 0x2A,
        0x01,
    ])
    assert [row[1][-1] for row in rows[:3]] == [0x2A, 0x2A, 0x2A]


def test_lesson01_number_formats_execute_as_same_value():
    data, _, _ = assemble_text(FIXTURE.read_text())
    cpu = CPU()
    cpu.mem[:len(data)] = data
    cpu.run()
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.r[:3] == [42, 42, 42]


def test_lesson02_logic_fixture():
    source = ROOT / "course" / "examples" / "lesson02-logic.eduasm"
    data, _, _ = assemble_text(source.read_text())
    cpu = CPU()
    cpu.mem[:len(data)] = data
    cpu.run()
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.r[0] == 0xCC
    assert cpu.r[1] == 0xAA
    assert cpu.r[2] == 0x88  # AND
    assert cpu.r[3] == 0xEE  # OR
    assert cpu.r[4] == 0x66  # XOR
    assert cpu.r[5] == 0x33  # NOT


def test_lesson03_cpu_cycle_fixture():
    source = ROOT / "course" / "examples" / "lesson03-cpu-cycle.eduasm"
    data, _, _ = assemble_text(source.read_text())
    cpu = CPU()
    cpu.mem[:len(data)] = data
    cpu.run()
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.r[0] == 30
    assert cpu.r[1] == 20
    assert cpu.pc == len(data)
    assert cpu.flags == 0


def test_lesson04_machine_state_step_by_step():
    source = ROOT / "course" / "examples" / "lesson04-machine-state.eduasm"
    data, _, _ = assemble_text(source.read_text())
    cpu = CPU()
    cpu.mem[:len(data)] = data

    assert (cpu.r[0], cpu.r[1], cpu.pc, cpu.sp, cpu.flags) == (0, 0, 0, 0xFF00, 0)
    cpu.step()
    assert (cpu.r[0], cpu.pc, cpu.flags) == (5, 3, 0)
    cpu.step()
    assert (cpu.r[1], cpu.pc, cpu.flags) == (5, 6, 0)
    cpu.step()
    assert cpu.r[0] == 0
    assert cpu.pc == 9
    assert cpu.flags == (CPU.Z | CPU.C)
    assert cpu.sp == 0xFF00
    cpu.step()
    assert cpu.halted
    assert cpu.pc == len(data)


def test_lesson05_exact_machine_code():
    source = ROOT / "course" / "examples" / "lesson05-machine-code.eduasm"
    data, _, rows = assemble_text(source.read_text())
    assert data == bytes([
        0x11, 0x00, 0x2A,
        0x11, 0x01, 0x01,
        0x20, 0x00, 0x01,
        0x01,
    ])
    assert [(pc, len(encoded)) for pc, encoded, _, _ in rows] == [
        (0x0000, 3), (0x0003, 3), (0x0006, 3), (0x0009, 1)
    ]


def test_lesson05_little_endian_address_encoding():
    data, _, _ = assemble_text("JMP 0x1234\n")
    assert data == bytes([0x30, 0x34, 0x12])


def test_lesson06_labels_and_execution():
    source = ROOT / "course" / "examples" / "lesson06-eduasm.eduasm"
    data, labels, rows = assemble_text(source.read_text())
    assert labels["loop"] == 0x0003
    assert data == bytes([
        0x11, 0x00, 0x03,
        0x23, 0x00, 0x01,
        0x32, 0x03, 0x00,
        0x01,
    ])
    cpu = CPU()
    cpu.mem[:len(data)] = data
    cpu.run()
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.r[0] == 0
    assert cpu.pc == len(data)


def test_lesson07_flags_drive_branches():
    source = ROOT / "course" / "examples" / "lesson07-flags-branches.eduasm"
    data, labels, _ = assemble_text(source.read_text())
    cpu = CPU()
    cpu.mem[:len(data)] = data
    cpu.run()
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.r[0] == 0
    assert cpu.r[1] == 0
    assert cpu.flags == (CPU.Z | CPU.C)
    assert cpu.pc == len(data)
    assert labels["wrapped"] > 0
    assert labels["done"] < len(data)


def test_lesson08_stack_intermediate_states():
    source = ROOT / "course" / "examples" / "lesson08-stack.eduasm"
    data, _, _ = assemble_text(source.read_text())
    cpu = CPU()
    cpu.mem[:len(data)] = data

    cpu.step()
    cpu.step()
    assert cpu.sp == 0xFF00

    cpu.step()
    assert cpu.sp == 0xFEFF
    assert cpu.mem[0xFEFF] == 0x11

    cpu.step()
    assert cpu.sp == 0xFEFE
    assert cpu.mem[0xFEFE] == 0x22
    assert cpu.mem[0xFEFF] == 0x11

    cpu.step()
    assert cpu.r[2] == 0x22
    assert cpu.sp == 0xFEFF

    cpu.step()
    assert cpu.r[3] == 0x11
    assert cpu.sp == 0xFF00

    cpu.step()
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.pc == len(data)
    # POP moves SP; it does not erase the old stack bytes.
    assert cpu.mem[0xFEFE] == 0x22
    assert cpu.mem[0xFEFF] == 0x11


def test_lesson09_call_ret_abi_stack_layout():
    source = ROOT / "course" / "examples" / "lesson09-call-ret-abi.eduasm"
    data, labels, _ = assemble_text(source.read_text())
    cpu = CPU()
    cpu.mem[:len(data)] = data

    cpu.step()  # MOVI R0,20
    cpu.step()  # MOVI R1,22
    return_pc = cpu.pc + 3
    assert cpu.sp == 0xFF00

    cpu.step()  # CALL add
    assert cpu.pc == labels["add"]
    assert cpu.sp == 0xFEFE
    assert cpu.mem[0xFEFE] == (return_pc & 0xFF)
    assert cpu.mem[0xFEFF] == ((return_pc >> 8) & 0xFF)

    cpu.step()  # ADD R0,R1
    assert cpu.r[0] == 42

    cpu.step()  # RET
    assert cpu.pc == return_pc
    assert cpu.sp == 0xFF00

    cpu.step()  # HALT
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.r[0] == 42
    assert cpu.pc == return_pc + 1


def test_lesson10_real_compiler_pipeline_executes():
    source = ROOT / "course" / "examples" / "lesson10-compiler.educ"
    tree, ir, asm, obj, data, symbols = compile_source(
        source.read_text(), str(source)
    )
    assert tree.functions
    assert ir.functions
    assert ".export main" in asm
    assert obj["format"] == "educpu-object-v0"

    cpu = CPU()
    cpu.mem[:len(data)] = data
    cpu.pc = symbols["main"]
    halt = len(data)
    cpu.mem[halt] = 0x01
    cpu.sp -= 1
    cpu.mem[cpu.sp] = (halt >> 8) & 0xFF
    cpu.sp -= 1
    cpu.mem[cpu.sp] = halt & 0xFF
    cpu.run()

    assert cpu.r[0] == 42
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.sp == 0xFF00


def test_lesson11_real_ast_and_semantic_analysis():
    source = ROOT / "course" / "examples" / "lesson11-ast-semantics.educ"
    tree = parse(source.read_text())
    assert isinstance(tree, Program)
    assert [fn.name for fn in tree.functions] == ["add", "main"]

    add, main = tree.functions
    assert isinstance(add, Function)
    assert add.return_type == "byte"
    assert add.params == [("byte", "a"), ("byte", "b")]
    assert isinstance(add.body[0], Return)

    decl = main.body[0]
    assert isinstance(decl, VarDecl)
    assert decl.type == "byte" and decl.name == "answer"
    assert isinstance(decl.value, Call)
    assert decl.value.name == "add"
    assert isinstance(main.body[1], Return)
    assert isinstance(main.body[1].value, Name)
    assert main.body[1].value.name == "answer"

    signatures = analyze(tree)
    assert signatures["add"].return_type == "byte"
    assert signatures["main"].return_type == "byte"

    bad = parse("byte main(){return missing+2;}")
    try:
        analyze(bad)
    except SemanticError as exc:
        assert "unknown variable: missing" in str(exc)
    else:
        raise AssertionError("semantic analysis accepted an unknown variable")


def test_lesson12_real_ir_codegen_pipeline_executes():
    source = ROOT / "course" / "examples" / "lesson12-ir-codegen.educ"
    tree = parse(source.read_text())
    ir = lower(tree)
    assert [fn.name for fn in ir.functions] == ["add_two", "main"]

    add_two = ir.functions[0]
    ops = [ins.op for ins in add_two.instructions]
    assert "const" in ops
    assert "add" in ops
    assert "copy" in ops
    assert "ret" in ops

    main = ir.functions[1]
    assert "call" in [ins.op for ins in main.instructions]

    asm = generate(ir)
    assert ".export add_two" in asm
    assert ".export main" in asm
    assert "ENTER " in asm
    assert "STORES [" in asm
    assert "LOADS " in asm
    assert "CALL add_two" in asm

    obj, _ = assemble_object(asm)
    data, symbols, _ = link([obj])
    cpu = CPU()
    cpu.mem[:len(data)] = data
    cpu.pc = symbols["main"]
    halt = len(data)
    cpu.mem[halt] = 0x01
    cpu.sp -= 1
    cpu.mem[cpu.sp] = (halt >> 8) & 0xFF
    cpu.sp -= 1
    cpu.mem[cpu.sp] = halt & 0xFF
    cpu.run()

    assert cpu.r[0] == 42
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.sp == 0xFF00


def test_lesson13_objects_relocations_and_linking():
    main_source = ROOT / "course" / "examples" / "lesson13-main.eduasm"
    math_source = ROOT / "course" / "examples" / "lesson13-math.eduasm"

    main_obj, _ = assemble_object(main_source.read_text())
    math_obj, _ = assemble_object(math_source.read_text())

    assert main_obj["exports"]["main"] == 0
    assert main_obj["imports"] == ["add_two"]
    relocs = [r for r in main_obj["relocations"] if r["symbol"] == "add_two"]
    assert len(relocs) == 1
    assert relocs[0]["type"] == "abs16le"
    assert math_obj["exports"]["add_two"] == 0

    data, symbols, bases = link([main_obj, math_obj])
    assert bases == [0, len(bytes.fromhex(main_obj["data"]))]
    assert symbols["main"] == 0
    assert symbols["add_two"] == bases[1]

    reloc = relocs[0]
    target = data[reloc["offset"]] | (data[reloc["offset"] + 1] << 8)
    assert target == symbols["add_two"]

    cpu = CPU()
    cpu.mem[:len(data)] = data
    cpu.pc = symbols["main"]
    cpu.run()

    assert cpu.r[0] == 42
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.sp == 0xFF00


def test_lesson14_compile_trace_and_runtime_state_transitions():
    source = ROOT / "course" / "examples" / "lesson14-end-to-end.educ"
    text = source.read_text()
    trace = compile_trace(text, str(source))
    tree, ir, asm, obj, data, symbols = compile_source(text, str(source))

    assert trace["format"] == "educpu-compile-trace-v0"
    assert trace["source"]["text"] == text
    assert trace["ast"]["node"] == "Program"
    assert "func byte main()" in trace["ir"]
    assert ".export main" in trace["assembly"]
    assert bytes.fromhex(trace["machine"]["bytes"]) == data
    assert trace["machine"]["symbols"]["main"] == symbols["main"]
    assert trace["machine"]["instructions"]
    assert all("address" in x and "bytes" in x and "assembly" in x
               for x in trace["machine"]["instructions"])

    cpu = CPU()
    cpu.mem[:len(data)] = data
    cpu.pc = symbols["main"]
    halt = len(data)
    cpu.mem[halt] = 0x01
    cpu.sp -= 1
    cpu.mem[cpu.sp] = (halt >> 8) & 0xFF
    cpu.sp -= 1
    cpu.mem[cpu.sp] = halt & 0xFF

    states = []
    while not cpu.halted and cpu.trap is None:
        before = (cpu.pc, cpu.sp, tuple(cpu.r))
        cpu.step()
        after = (cpu.pc, cpu.sp, tuple(cpu.r))
        states.append((before, after))

    assert states
    assert any(before != after for before, after in states)
    assert any(before[1] != after[1] for before, after in states)
    assert cpu.r[0] == 42
    assert cpu.halted
    assert cpu.trap is None
    assert cpu.sp == 0xFF00
