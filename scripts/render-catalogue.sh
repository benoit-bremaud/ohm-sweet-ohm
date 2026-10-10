#!/usr/bin/env bash
# Renders every catalogue schematic to a cropped SVG.
# Usage: scripts/render-catalogue.sh [CATALOGUE_DIR] [OUTPUT_DIR]
# Runs inside the renderer image (docker/renderer/Dockerfile), which provides kicad-cli and inkscape.
set -euo pipefail

catalogue="${1:-catalogue}"
output="${2:-build/catalogue}"
margin_mm=2

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

count=0
multi_sheet=()
crop_failed=()
while IFS= read -r -d '' found; do
  # Paths are found from inside the catalogue, so the block's relative path never depends on how
  # CATALOGUE_DIR was written (trailing slash, absolute path, symbolic link).
  relative="$(dirname "${found#./}")"
  schematic="$catalogue/${found#./}"
  mkdir -p "$output/$relative" "$work/$relative"

  # Page-size SVG without the drawing sheet frame and title block; one file per sheet.
  kicad-cli sch export svg --exclude-drawing-sheet --no-background-color \
    -o "$work/$relative" "$schematic" >/dev/null

  # A block is a single sheet (catalogue-format.md): more SVGs mean sub-sheets that would be lost.
  sheets=("$work/$relative"/*.svg)
  if [ "${#sheets[@]}" -ne 1 ]; then
    multi_sheet+=("$relative (${#sheets[@]} sheets)")
    continue
  fi

  # Crop to the drawing plus a small margin. Inkscape exits 0 even when it fails (missing input,
  # unwritable output, malformed SVG), so the result is checked instead of the exit status.
  cropped="$output/$relative/schematic.svg"
  crop_log="$work/$relative/inkscape.log"
  inkscape "$work/$relative/schematic.svg" --export-area-drawing \
    --export-margin="$margin_mm" --export-plain-svg -o "$cropped" 2>"$crop_log" || true
  # The GtkRecentManager warning is printed on every headless run and is harmless.
  unexpected="$(grep -v -e 'GtkRecentManager' -e '^[[:space:]]*$' "$crop_log" || true)"
  if [ ! -s "$cropped" ] || ! grep -q 'viewBox=' "$cropped" || [ -n "$unexpected" ]; then
    echo "crop failed for $relative:" >&2
    echo "${unexpected:-no cropped SVG with a viewBox was produced}" >&2
    crop_failed+=("$relative")
    continue
  fi

  echo "rendered $relative"
  count=$((count + 1))
done < <(cd "$catalogue" && find . -name schematic.kicad_sch -print0 | sort -z)

if [ "${#multi_sheet[@]}" -gt 0 ]; then
  echo "multi-sheet schematics are not supported, a block must fit on one sheet:" >&2
  printf '  %s\n' "${multi_sheet[@]}" >&2
  exit 1
fi

if [ "${#crop_failed[@]}" -gt 0 ]; then
  echo "cropping failed for ${#crop_failed[@]} block(s): ${crop_failed[*]}" >&2
  exit 1
fi

if [ "$count" -eq 0 ]; then
  echo "no schematic found in $catalogue" >&2
  exit 1
fi
echo "$count schematic(s) rendered to $output"
