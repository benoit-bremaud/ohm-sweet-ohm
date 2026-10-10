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
while IFS= read -r -d '' schematic; do
  block_dir="$(dirname "$schematic")"
  relative="${block_dir#"$catalogue"/}"
  mkdir -p "$output/$relative" "$work/$relative"

  # Page-size SVG without the drawing sheet frame and title block.
  kicad-cli sch export svg --exclude-drawing-sheet --no-background-color \
    -o "$work/$relative" "$schematic" >/dev/null

  # Crop to the drawing plus a small margin.
  inkscape "$work/$relative/schematic.svg" --export-area-drawing \
    --export-margin="$margin_mm" --export-plain-svg \
    -o "$output/$relative/schematic.svg" 2>/dev/null

  echo "rendered $relative"
  count=$((count + 1))
done < <(find "$catalogue" -name schematic.kicad_sch -print0 | sort -z)

if [ "$count" -eq 0 ]; then
  echo "no schematic found in $catalogue" >&2
  exit 1
fi
echo "$count schematic(s) rendered to $output"
