#!/bin/sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
EXPECTED="$ROOT/fpga/conformance/expected.txt"
ACTUAL="${TMPDIR:-/tmp}/educpu-fpga-reference-vectors.$$"
trap 'rm -f "$ACTUAL"' EXIT
python3 "$ROOT/fpga/conformance/reference_vectors.py" > "$ACTUAL"
diff -u "$EXPECTED" "$ACTUAL"
echo "EduCPU FPGA reference-vector generation PASS"
