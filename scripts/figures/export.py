"""Export the figures of one guide as PNG, and pair each with its field photo (`just figures-png`).

Usage: python3 scripts/figures/export.py <guide folder> <output dir> [photo dir]
Needs Inkscape (PNG) and ImageMagick 7 (`magick`, plates) on the PATH.

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
        "--export-background=white",
        "--export-background-opacity=1",
        f"--export-filename={png}",
    ]


def plate_command(photo: Path, png: Path, plate: Path) -> list[str]:
    """ImageMagick command: `photo` on the left, a 24 px white gutter, `png` on the right, same height."""
    return [
        "magick",
        str(photo),
        "-resize",
        "x1080",
        "-background",
        "white",
        "-gravity",
        "east",
        "-splice",
        "24x0",
        "(",
        str(png),
        "-resize",
        "x1080",
        ")",
        "-alpha",
        "remove",
        "+append",
        "+repage",
        str(plate),
    ]


def plan(guide: Path, out: Path, photos: Path | None) -> list[list[str]]:
    """Commands exporting every figure of `guide`, each followed by its plate when it has a photo."""
    commands = []
    # arbre-N.svg are the decision trees drawn for the site, not figures
    for svg in sorted(
        p for p in guide.glob("*.svg") if not p.stem.startswith("arbre-")
    ):
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
    photos = Path(argv[2]) if len(argv) == 3 else None
    if photos and not photos.is_dir():
        sys.stderr.write(f"no such photo folder: {photos}\n")
        return 2
    out.mkdir(parents=True, exist_ok=True)
    for command in plan(guide, out, photos):
        try:
            subprocess.run(command, check=True)
        except (OSError, subprocess.CalledProcessError) as error:
            sys.stderr.write(f"export failed: {' '.join(command)}: {error}\n")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
