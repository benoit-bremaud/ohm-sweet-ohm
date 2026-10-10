# Catalogue renderer: KiCad 9 (schematic to SVG) plus Inkscape (crop to the drawing).
# See docs/architecture/decisions/0002-schematic-rendering.md.
FROM kicad/kicad:9.0.9@sha256:e638b79b0321f29395a5b783e94bb9f3c73303e8da15da27b8f5cb4b67a37729

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends inkscape \
  && rm -rf /var/lib/apt/lists/*
USER kicad
