# Catalogue renderer: KiCad 9 (schematic to SVG) plus Inkscape (crop to the drawing).
# Inkscape is pinned: a new version must be a deliberate change, not a side effect of a rebuild.
# See docs/architecture/decisions/0002-schematic-rendering.md.
FROM kicad/kicad:10.0.6@sha256:18693567392b80da435f9fa952ce3a3e534c66eb5a6033f5b9c80aa3b19dd3ec

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends inkscape=1.2.2-2+b1 \
  && rm -rf /var/lib/apt/lists/*
USER kicad
