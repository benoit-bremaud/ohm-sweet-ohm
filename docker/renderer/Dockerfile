# Catalogue renderer: KiCad 9 (schematic to SVG) plus Inkscape (crop to the drawing).
# Inkscape is pinned: a new version must be a deliberate change, not a side effect of a rebuild.
# See docs/architecture/decisions/0002-schematic-rendering.md.
FROM kicad/kicad:9.0.9@sha256:e638b79b0321f29395a5b783e94bb9f3c73303e8da15da27b8f5cb4b67a37729

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends inkscape=1.2.2-2+b1 \
  && rm -rf /var/lib/apt/lists/*
USER kicad
