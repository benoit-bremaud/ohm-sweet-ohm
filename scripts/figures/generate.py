"""Generate the SVG figures of the troubleshooting guides (`just figures`).

Usage: python3 scripts/figures/generate.py [--check]

Without option, (re)write every figure next to its guide. With --check, write nothing and
exit 1 when a committed figure is missing or differs from what the generator produces.
"""

from __future__ import annotations

import sys
from pathlib import Path

import guide_00
import guide_01
import guide_02
import guide_10
import guide_11
import guide_12
import guide_13
import guide_20
import guide_21

ROOT = Path(__file__).resolve().parents[2] / "troubleshooting"

# Guide folder -> {figure name: (function returning the SVG, expected multimeter dial positions)}
GUIDES = {
    "00_securite": guide_00.FIGURES,
    "01_multimetre": guide_01.FIGURES,
    "02_pieges_en_circuit": guide_02.FIGURES,
    "10_resistance": guide_10.FIGURES,
    "11_potentiometre": guide_11.FIGURES,
    "12_thermistance": guide_12.FIGURES,
    "13_fusible": guide_13.FIGURES,
    "20_condensateur_ceramique": guide_20.FIGURES,
    "21_condensateur_film": guide_21.FIGURES,
}


def render() -> dict[Path, str]:
    """Return the content of every figure, keyed by its path."""
    return {
        ROOT / folder / f"{name}.svg": draw()
        for folder, figures in GUIDES.items()
        for name, (draw, _) in figures.items()
    }


def stale(figures: dict[Path, str]) -> list[Path]:
    """Paths whose file is missing or differs from the generated content."""
    return [
        path
        for path, content in figures.items()
        if not path.is_file() or path.read_text(encoding="utf-8") != content
    ]


def main(argv: list[str]) -> int:
    if argv not in ([], ["--check"]):
        sys.stderr.write(__doc__ or "")
        return 2
    figures = render()
    if argv:
        outdated = stale(figures)
        for path in outdated:
            sys.stderr.write(f"stale figure, run `just figures`: {path}\n")
        return 1 if outdated else 0
    for path, content in figures.items():
        path.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
