#!/bin/sh
# Tests of the figure generator (#101): the element library, every figure (well-formed, no
# external reference, dial on the expected position) and the committed SVGs against the
# generator. Needs uv (mise.toml) and python3.
set -eu
cd "$(dirname "$0")/.."
PYTHONDONTWRITEBYTECODE=1 uvx pytest@9.0.2 -q -p no:cacheprovider scripts/figures
