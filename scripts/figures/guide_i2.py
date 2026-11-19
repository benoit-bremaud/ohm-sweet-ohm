"""Figures of page i2, the oscilloscope presented as an instrument (anatomy, probe compensation, earth clip)."""

from __future__ import annotations

import math
from collections.abc import Sequence

from elements import Point, box, clip, curve, heading, svg, text, verdict

# Trace colours of channels 1 to 4; the screen is always dark, so they are fixed.
CHANNELS = ("#facc15", "#22d3ee", "#e879f9", "#60a5fa")
METAL = 'fill="#c9d0d9" stroke="#7d8794"'
LOW, HIGH = 1.5, 4.5  # levels of the compensation square wave, in divisions


def _badge(x: float, y: float, n: int) -> str:
    """Numbered marker tying a part of the drawing to its line of the legend."""
    return (
        f'  <circle cx="{x}" cy="{y}" r="9" fill="#b45309" stroke="#ffffff" stroke-width="1.2"/>\n'
        f'  <text x="{x}" y="{y + 4}" font-size="11" font-weight="700" text-anchor="middle" fill="#ffffff">{n}</text>\n'
    )


def _screen(
    x: float,
    y: float,
    w: float,
    h: float,
    cols: int,
    rows: int,
    trace: Sequence[Point],
    colour: str = CHANNELS[0],
) -> str:
    """Screen with its graticule of cols × rows divisions and one trace.

    `trace` is given in divisions, origin at the bottom left corner of the graticule.
    """
    dx, dy = w / cols, h / rows
    o = f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#0b1220" stroke="#7d8794"/>\n'
    lines = "".join(f"M{x + dx * i:.1f} {y} v{h} " for i in range(1, cols))
    lines += "".join(f"M{x} {y + dy * i:.1f} h{w} " for i in range(1, rows))
    o += f'  <path d="{lines.strip()}" stroke="#334155" stroke-width="0.7" fill="none"/>\n'
    d = " L".join(f"{x + dx * px:.1f} {y + h - dy * py:.1f}" for px, py in trace)
    o += f'  <path d="M{d}" stroke="{colour}" stroke-width="2" fill="none" stroke-linejoin="round" stroke-linecap="round"/>\n'
    return o


def _knob(x: float, y: float, r: float) -> str:
    """Rotary knob seen from the front, with its index mark."""
    return (
        f'  <circle cx="{x}" cy="{y}" r="{r}" fill="#9aa3ae" stroke="#5f6b7a"/>\n'
        f'  <path d="M{x} {y - r + 2} v{r * 0.6:.1f}" stroke="#20242b" stroke-width="1.6" stroke-linecap="round"/>\n'
    )


def _button(x: float, y: float, label: str, fill: str = "#4b5563") -> str:
    """Front panel key, 32 wide, centred on x."""
    return (
        f'  <rect x="{x - 16}" y="{y}" width="32" height="15" rx="3" fill="{fill}" stroke="#7d8794"/>\n'
        f'  <text x="{x}" y="{y + 10.5}" font-size="7" font-weight="700" text-anchor="middle" fill="#ffffff">{label}</text>\n'
    )


def square_wave(shape: str, periods: int = 2, span: float = 4) -> list[Point]:
    """Square wave of the compensation output as a probe shows it, in divisions.

    `shape` is "flat" (compensated), "under" (rounded edges) or "over" (overshoot).
    """
    sign = {"flat": 0.0, "under": -1.0, "over": 1.0}[shape]
    half, steps = span / 2, 20
    points: list[Point] = []
    for k in range(2 * periods):
        start, end = (LOW, HIGH) if k % 2 == 0 else (HIGH, LOW)
        for i in range(steps + 1):
            t = half * i / steps
            # the error is a fraction of the step that dies out along the plateau
            error = sign * 0.3 * (end - start) * math.exp(-t / 0.35)
            points.append((k * half + t, end + error))
    return points


# ---------------------------------------------------------------- figure 1
def fig_anatomy() -> str:
    b = heading(
        "Anatomie d'un oscilloscope numérique de paillasse",
        "Sept organes à connaître ; l'écran montre le signal carré de la sortie de compensation",
    )
    # case and feet
    b += '  <rect x="64" y="342" width="34" height="10" rx="3" fill="#20242b"/>\n'
    b += '  <rect x="352" y="342" width="34" height="10" rx="3" fill="#20242b"/>\n'
    b += '  <rect x="40" y="96" width="370" height="250" rx="14" fill="#2b3038" stroke="#7d8794" stroke-width="1.5"/>\n'
    # screen: 1 kHz square wave, 200 µs/div, trigger on the rising edge at mid-screen
    sx, sy, sw, sh = 54, 110, 216, 144
    low, high = 2.5, 5.5
    edges = (1, 3.5, 6, 8.5, 11)
    trace: list[Point] = [(0, low)]
    for i, e in enumerate(edges):
        trace += [(e, low), (e, high)] if i % 2 == 0 else [(e, high), (e, low)]
    trace.append((12, high))
    b += _screen(sx, sy, sw, sh, 12, 8, trace)
    div = sw / 12
    ty = sy + sh - div * 4
    # trigger markers: level on the left edge, instant at the top
    b += f'  <path d="M{sx} {ty - 5} l8 5 l-8 5 Z" fill="#f97316"/>\n'
    b += f'  <path d="M{sx + 6 * div - 5} {sy} l5 8 l5 -8 Z" fill="#f97316"/>\n'
    b += f'  <text x="{sx + 6}" y="{sy + sh - 6}" font-size="8" font-weight="700" fill="{CHANNELS[0]}">CH1 1 V/div</text>\n'
    b += f'  <text x="{sx + sw - 6}" y="{sy + sh - 6}" font-size="8" font-weight="700" text-anchor="end" fill="#e6edf3">200 µs/div</text>\n'
    # front panel: run keys, then one column per group of controls
    cols = (300, 340, 380)
    b += _button(cols[0], 110, "AUTO")
    b += _button(cols[1], 110, "RUN", "#15803d")
    b += _button(cols[2], 110, "SINGLE")
    for cx, name in zip(cols, ("VERTICAL", "HORIZ.", "TRIGGER"), strict=True):
        b += f'  <text x="{cx}" y="148" font-size="7" font-weight="700" text-anchor="middle" fill="#c9d1d9">{name}</text>\n'
        b += _knob(cx, 166, 8)
    b += _knob(cols[0], 200, 12)
    b += _knob(cols[1], 200, 12)
    b += _button(cols[2], 193, "MODE")
    # inputs: one BNC socket per channel, then the compensation output
    bnc = (76, 130, 184, 238)
    for i, cx in enumerate(bnc):
        b += f'  <text x="{cx}" y="280" font-size="8" font-weight="700" text-anchor="middle" fill="{CHANNELS[i]}">CH{i + 1}</text>\n'
        b += f'  <circle cx="{cx}" cy="302" r="11" {METAL}/>\n'
        b += f'  <circle cx="{cx}" cy="302" r="6" fill="#20242b"/>\n'
        b += f'  <circle cx="{cx}" cy="302" r="2" fill="#d9b88c"/>\n'
    b += '  <path d="M322 286 h5 v-7 h7 v7 h5 v-7 h7" stroke="#c9d1d9" stroke-width="1.2" fill="none"/>\n'
    b += f'  <rect x="324" y="294" width="7" height="14" rx="1.5" {METAL}/>\n'
    b += f'  <rect x="338" y="294" width="7" height="14" rx="1.5" {METAL}/>\n'
    # probe plugged in channel 1, lying under the instrument
    b += '  <path class="blk" stroke-width="4" fill="none" stroke-linecap="round" d="M76 302 V370 C76 420 150 430 222 430"/>\n'
    b += '  <circle cx="76" cy="302" r="9" fill="#4b5563" stroke="#7d8794"/>\n'
    b += '  <rect x="220" y="426" width="18" height="8" rx="2" fill="#20242b" stroke="#7d8794" stroke-width="0.6"/>\n'
    b += '  <rect x="236" y="421" width="66" height="18" rx="5" fill="#4b5563" stroke="#7d8794"/>\n'
    b += '  <rect x="250" y="424" width="16" height="6" rx="1.5" fill="#f97316"/>\n'
    b += '  <path d="M302 423 L322 427 V433 L302 437 Z" fill="#4b5563" stroke="#7d8794" stroke-linejoin="round"/>\n'
    b += '  <path d="M322 430 H338 q5 0 5 5 t-5 5" stroke="#9aa3ae" stroke-width="2.2" fill="none" stroke-linecap="round"/>\n'
    b += '  <path class="blk" stroke-width="3" fill="none" stroke-linecap="round" d="M290 439 C290 466 322 472 352 460"/>\n'
    b += clip(356, 466, False)
    # markers on the drawing
    for n, (px, py) in enumerate(
        (
            (sx + sw - 14, sy + 14),
            (cols[0], 228),
            (cols[1], 228),
            (cols[2], 228),
            (270, 302),
            (366, 302),
            (270, 406),
        ),
        start=1,
    ):
        b += _badge(px, py, n)
    # legend
    for n, (head, sub) in enumerate(
        (
            ("Écran et graticule", "8 divisions en hauteur, 12 en largeur"),
            ("Réglages verticaux", "volts par division, position"),
            ("Réglages horizontaux", "temps par division (base de temps)"),
            ("Déclenchement", "niveau, front, mode AUTO ou NORMAL"),
            ("Entrées BNC", "une par voie, masses communes"),
            ("Sortie de compensation", "signal carré pour régler la sonde"),
            ("Sonde et pince de masse", "commutateur ×1 / ×10 sur le corps"),
        ),
        start=1,
    ):
        y = 76 + 44 * n
        b += _badge(446, y - 5, n)
        b += text(464, y, head, size=14, weight=700)
        b += text(464, y + 17, sub, "mut", 12)
    return svg(
        760,
        500,
        "Anatomie d'un oscilloscope numérique de paillasse",
        "Oscilloscope à quatre voies, écran affichant un signal carré jaune. Repères : "
        "1 écran et graticule de 8 divisions sur 12, 2 réglages verticaux, 3 réglages horizontaux, "
        "4 déclenchement, 5 entrées BNC des voies 1 à 4, 6 sortie de compensation, "
        "7 sonde branchée sur la voie 1, avec son commutateur ×1 / ×10 et sa pince de masse.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def fig_compensation() -> str:
    b = heading(
        "Régler la compensation d'une sonde ×10",
        "Pointe sur la sortie de compensation, vis de la sonde tournée jusqu'à obtenir un sommet plat",
    )
    for x0, shape, title, cls, head, sub in (
        (
            40,
            "under",
            "Sous-compensée",
            "no",
            "✗ fronts arrondis",
            "les fréquences hautes sont sous-estimées",
        ),
        (
            280,
            "flat",
            "Compensée",
            "ok",
            "✓ sommet plat",
            "la sonde est accordée à cette entrée",
        ),
        (
            520,
            "over",
            "Surcompensée",
            "no",
            "✗ dépassement",
            "les fréquences hautes sont surestimées",
        ),
    ):
        b += text(x0, 104, title, size=15, weight=700)
        b += _screen(x0, 118, 200, 150, 8, 6, square_wave(shape))
        b += verdict(x0 + 100, 300, head, sub, cls)
    return svg(
        760,
        340,
        "Régler la compensation d'une sonde ×10",
        "Trois écrans montrant le même signal carré. À gauche, sonde sous-compensée : les fronts "
        "sont arrondis. Au centre, sonde compensée : le sommet est plat. À droite, sonde "
        "surcompensée : un dépassement suit chaque front.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def fig_earth_clip() -> str:
    b = heading(
        "La pince de masse est reliée à la terre",
        "Pointe en bleu, pince de masse en noir ; carte dont le 0 V est relié à la terre par son alimentation",
    )
    b += '  <path class="grid" d="M380 84 V440"/>\n'
    for x0, wrong, title, cls, head, sub in (
        (
            0,
            False,
            "Pince sur le 0 V",
            "ok",
            "✓ aucun courant dans la pince",
            "le 0 V est déjà au potentiel de la terre",
        ),
        (
            380,
            True,
            "Pince sur le +12 V",
            "no",
            "✗ court-circuit par la terre",
            "le +12 V rejoint le 0 V par la pince et les deux terres",
        ),
    ):
        nx = x0 + 250  # column of the board's nodes
        top, mid, bottom, earth = 150, 220, 292, 400
        b += text(x0 + 20, 104, title, size=15, weight=700)
        b += f'  <rect class="panel" x="{x0 + 214}" y="124" width="146" height="196" rx="8" stroke-width="1.5"/>\n'
        # board: +12 V, R1, node A, load, 0 V, and its supply on the right
        b += curve([(nx, top), (nx, bottom)], "blk", 2)
        b += curve(
            [(nx, top), (x0 + 322, top), (x0 + 322, bottom), (nx, bottom)], "blk", 2
        )
        # protective earth: bar, mains cord of the oscilloscope, earth link of the supply
        b += curve([(x0 + 24, earth), (x0 + 356, earth)], "blk", 4)
        b += curve([(x0 + 84, 188), (x0 + 84, earth)], "blk", 2)
        b += curve([(nx, bottom), (nx, earth)], "blk", 2)
        # probe: the tip reads a node, the clip is the oscilloscope's ground
        tip, ground = ((nx, mid), (nx, top)) if wrong else ((nx, top), (nx, bottom))
        upper, lower = (ground, tip) if wrong else (tip, ground)
        for target, y in ((upper, top), (lower, 172)):
            cls_wire = "fb" if target is tip else "blk"
            b += curve(
                [(x0 + 144, y), (x0 + 196, y), (x0 + 196, target[1]), target]
                if target[1] != y
                else [(x0 + 144, y), target],
                cls_wire,
            )
        if wrong:
            b += (
                f'  <path class="flow fr" d="M{x0 + 322} 200 V{top} H{x0 + 84} '
                f'V{earth} H{nx} V{bottom} H{x0 + 322} V244"/>\n'
            )
        b += box(x0 + 24, 124, 120, 64, "Oscilloscope", ("masse = châssis",))
        b += box(x0 + 296, 200, 52, 44, "12 V")
        for y1, name in ((162, "R1"), (236, "charge")):
            b += f'  <rect class="bg blk" x="{nx - 9}" y="{y1}" width="18" height="44" rx="3" stroke-width="1.5"/>\n'
            b += text(nx + 14, y1 + 26, name, "mut", 11)
        for y, name in ((top, "+12 V"), (mid, "A"), (bottom, "0 V")):
            b += f'  <circle class="blkf" cx="{nx}" cy="{y}" r="4"/>\n'
            b += text(
                nx + 10, y - 8 if y != bottom else y + 18, name, size=12, weight=700
            )
        b += f'  <circle class="blue" cx="{tip[0]}" cy="{tip[1]}" r="5"/>\n'
        b += clip(ground[0] - 12, ground[1], False)
        b += text(x0 + 92, 300, "cordon secteur", "mut", 11)
        b += text(nx + 8, 366, "terre de", "mut", 11)
        b += text(nx + 8, 380, "l'alimentation", "mut", 11)
        b += text(x0 + 24, earth + 20, "Terre de l'installation", "mut", 12)
        b += verdict(x0 + 190, 462, head, sub, cls)
    return svg(
        760,
        500,
        "La pince de masse est reliée à la terre",
        "Deux montages. L'oscilloscope est relié à la terre par son cordon secteur, la carte par "
        "son alimentation. À gauche, pointe sur le +12 V et pince sur le 0 V : aucun courant dans "
        "la pince. À droite, pointe sur le point A et pince sur le +12 V : le +12 V est "
        "court-circuité au 0 V par la pince, le châssis de l'oscilloscope et la terre.",
        b,
    )


# Figure name -> (function, expected multimeter dial positions)
FIGURES = {
    "anatomie": (fig_anatomy, []),
    "compensation-sonde": (fig_compensation, []),
    "pince-de-masse": (fig_earth_clip, []),
}
