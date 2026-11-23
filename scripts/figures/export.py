"""Export the figures of one guide as PNG, and pair each with its field photo (`just figures-png`).

Usage: python3 scripts/figures/export.py <guide folder> <output dir> [photo dir]

Every `<guide folder>/*.svg` becomes `<output dir>/<name>.png` (Inkscape). When `<photo dir>/<name>.jpg`
exists, `<output dir>/<name>-planche.png` puts the photo on the left and the figure on the right
(ImageMagick). The output and the photos stay out of the repository: photos of a client's board are not
published.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

WIDTH = 1520  # PNG width in pixels: twice the 760-unit figures


def png_command(svg: Path, png: Path) -> list[str]:
    """Inkscape command rendering `svg` to `png` at WIDTH pixels."""
    return [
        "inkscape",
        str(svg),
        "--export-type=png",
        f"--export-width={WIDTH}",
        f"--export-filename={png}",
    ]


def plate_command(photo: Path, png: Path, plate: Path) -> list[str]:
    """ImageMagick command joining `photo` (left) and `png` (right) at the same height."""
    return [
        "magick",
        str(photo),
        str(png),
        "-resize",
        "x1080",
        "-background",
        "white",
        "-gravity",
        "center",
        "-splice",
        "24x0",
        "+append",
        str(plate),
    ]


def plan(guide: Path, out: Path, photos: Path | None) -> list[list[str]]:
    """Commands exporting every figure of `guide`, then a plate for each figure that has a photo."""
    commands = []
    for svg in sorted(guide.glob("*.svg")):
        png = out / f"{svg.stem}.png"
        commands.append(png_command(svg, png))
        photo = photos / f"{svg.stem}.jpg" if photos else None
        if photo and photo.is_file():
            commands.append(plate_command(photo, png, out / f"{svg.stem}-planche.png"))
    return commands


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3):
        sys.stderr.write(__doc__ or "")
        return 2
    guide, out = Path(argv[0]), Path(argv[1])
    if not guide.is_dir():
        sys.stderr.write(f"no such guide folder: {guide}\n")
        return 2
    out.mkdir(parents=True, exist_ok=True)
    for command in plan(guide, out, Path(argv[2]) if len(argv) == 3 else None):
        subprocess.run(command, check=True, capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
