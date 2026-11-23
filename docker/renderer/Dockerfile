# Catalogue renderer: KiCad 9 (schematic to SVG) plus Inkscape (crop to the drawing).
# Inkscape is pinned: a new version must be a deliberate change, not a side effect of a rebuild.
# See docs/architecture/decisions/0002-schematic-rendering.md.
FROM kicad/kicad:10.0.8@sha256:3f4a01786dfbe803a65f345c3342b765db9add913f5e9448f8356793714ddc34

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends inkscape=1.2.2-2+b1 \
  && rm -rf /var/lib/apt/lists/*
USER kicad
