# EduCPU object format v0

M4 uses a deliberately transparent JSON object format so students can inspect code, symbols and relocations directly.

EduASM source declares linkage explicitly:

```asm
.export start
.import add_two

start:
    CALL add_two
    HALT
```

Build an object with:

```sh
eduasm -c main.eduasm -o main.eo
```

The JSON object contains `data`, exported symbols, object-local labels, imports and relocations:

```json
{
  "format": "educpu-object-v0",
  "data": "38000001",
  "exports": {"start": 0},
  "locals": {"start": 0},
  "imports": ["add_two"],
  "relocations": [
    {"offset": 1, "type": "abs16le", "symbol": "add_two"}
  ]
}
```

`abs16le` tells EduLink to write the final 16-bit symbol address little-endian at the relocation offset. References to local labels are also relocated, so an object works regardless of where the linker places it.

A complete teaching pipeline is therefore:

```text
main.eduasm ──eduasm -c──> main.eo ─┐
                                    ├── edulink ──> program.bin
math.eduasm ──eduasm -c──> math.eo ─┘
```

M4 deliberately keeps one contiguous image. Sections and richer relocation types remain deferred until they provide educational value.
