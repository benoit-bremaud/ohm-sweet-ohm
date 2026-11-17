#!/bin/sh
# Tests of the figure generator (#101): the element library, every figure (well-formed, no
# external reference, dial on the expected position) and the committed SVGs against the
# generator, with a 90 % coverage floor on the generator. Needs uv (mise.toml) and python3.
set -eu
cd "$(dirname "$0")/.."
# COVERAGE_FILE: a private temporary file, out of the working tree and of concurrent runs.
cov=$(mktemp)
trap 'rm -f "$cov"' EXIT
PYTHONDONTWRITEBYTECODE=1 COVERAGE_FILE="$cov" \
  uvx --with pytest-cov==7.1.0 pytest@9.0.2 -q -p no:cacheprovider \
  --cov=scripts/figures --cov-config=scripts/figures/.coveragerc --cov-fail-under=90 scripts/figures
