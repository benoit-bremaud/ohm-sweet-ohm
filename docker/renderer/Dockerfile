# Catalogue renderer: KiCad 9 (schematic to SVG) plus Inkscape (crop to the drawing).
# Inkscape is pinned: a new version must be a deliberate change, not a side effect of a rebuild.
# See docs/architecture/decisions/0002-schematic-rendering.md.
FROM kicad/kicad:10.0.7@sha256:3224d1bf143185ecc1bd3a1082a36f37f0f4e59d707983a16515a845e3737fc6

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends inkscape=1.2.2-2+b1 \
  && rm -rf /var/lib/apt/lists/*
USER kicad
