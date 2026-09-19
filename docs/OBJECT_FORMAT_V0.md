# EduCPU object format v0

M4 uses a deliberately transparent JSON object format so learners can inspect object code, symbols and relocations without a binary-format parser.

Example:

```json
{
  "format": "educpu-object-v0",
  "data": "38000001",
  "exports": {"start": 0},
  "relocations": [
    {"offset": 1, "type": "abs16le", "symbol": "function"}
  ]
}
```

- `data`: section bytes as hexadecimal.
- `exports`: symbol names to offsets within the object.
- `relocations`: places the linker must patch.
- `abs16le`: write the final 16-bit symbol address little-endian at `offset`.

M4 initially uses one contiguous code/data image. Sections, alignment and richer relocation types are intentionally deferred until they teach something needed by EduC.
