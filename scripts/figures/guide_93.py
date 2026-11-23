"""Figures of guide 93, signal tracing and comparison with a healthy board."""

from __future__ import annotations

import math

from elements import Point, half_meter, heading, hookup, screen, svg, text, verdict

STAGES = ("Préampli", "Correcteur", "Ampli", "Sortie")
BOX_W, BOX_H, BOX_Y, GAP = 120, 56, 300, 50


def sine(
    amplitude: float, cols: int = 6, rows: int = 4, periods: int = 2
) -> list[Point]:
    """Sine wave centred on the screen, in divisions; amplitude 0 is a flat trace."""
    steps = 60
    return [
        (
            cols * i / steps,
            rows / 2 + amplitude * math.sin(2 * math.pi * periods * i / steps),
        )
        for i in range(steps + 1)
    ]


def _badge(x: float, y: float, n: int) -> str:
    """Numbered marker: the order of the measurements."""
    return (
        f'  <circle cx="{x}" cy="{y}" r="11" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"/>\n'
        f'  <text x="{x}" y="{y + 4.5}" font-size="13" font-weight="700" text-anchor="middle" fill="#ffffff">{n}</text>\n'
    )


# ---------------------------------------------------------------- figure 1
def fig_tracing() -> str:
    b = heading(
        "Suivre le signal : partir du milieu de la chaîne",
        "Carte sous tension, signal présent à l'entrée, oscilloscope pince sur le 0 V",
    )
    x = 40
    outs: list[float] = []
    b += text(x - 14, BOX_Y + BOX_H / 2 + 4, "→", "fg", 18, "end", 700)
    b += text(8, BOX_Y + BOX_H + 22, "entrée", "mut", 11)
    for i, name in enumerate(STAGES):
        b += f'  <rect class="panel" x="{x}" y="{BOX_Y}" width="{BOX_W}" height="{BOX_H}" rx="8"/>\n'
        b += text(x + BOX_W / 2, BOX_Y + 24, f"Étage {i + 1}", "fg", 13, "middle", 700)
        b += text(x + BOX_W / 2, BOX_Y + 42, name, "mut", 12, "middle")
        out = x + BOX_W + GAP / 2
        outs.append(out)
        b += f'  <path class="wire" d="M{x + BOX_W} {BOX_Y + BOX_H / 2} H{x + BOX_W + GAP}"/>\n'
        b += f'  <circle class="fg" cx="{out}" cy="{BOX_Y + BOX_H / 2}" r="4"/>\n'
        x += BOX_W + GAP
    # 1: the middle of the chain, signal present; 2: one stage further, nothing
    for n, out, amp, head, cls in (
        (1, outs[1], 1.4, "présent", "ok"),
        (2, outs[2], 0.0, "absent", "no"),
    ):
        sx, sy, sw, sh = out - 70, 120, 140, 96
        b += screen(sx, sy, sw, sh, 6, 4, sine(amp))
        b += f'  <path class="grid" d="M{out} {sy + sh} V{BOX_Y + BOX_H / 2 - 6}"/>\n'
        b += _badge(sx + sw - 4, sy + 4, n)
        b += text(
            out,
            sy + sh + 22,
            f"sortie de l'étage {n + 1} : {head}",
            cls,
            12,
            "middle",
            700,
        )
    b += text(
        outs[0],
        BOX_Y + BOX_H + 22,
        "non mesuré",
        "mut",
        11,
        "middle",
    )
    b += text(outs[3], BOX_Y + BOX_H + 22, "non mesuré", "mut", 11, "middle")
    b += verdict(
        380,
        402,
        "Entrée de l'étage 3 correcte, sortie absente : la panne est dans l'étage 3",
        "ou en aval, si l'étage 4 charge sa sortie : déconnecter la charge et mesurer de nouveau",
        "no",
    )
    return svg(
        760,
        440,
        "Traçage d'un signal dans une chaîne de quatre étages",
        "Une chaîne de quatre étages, préampli, correcteur, ampli et sortie, reçoit un signal à son entrée ; la carte est sous tension, "
        "la pince de masse de l'oscilloscope est sur le 0 V. "
        "Mesure 1, au milieu de la chaîne, à la sortie de l'étage 2 : l'écran montre une sinusoïde, le signal est présent. "
        "Mesure 2, à la sortie de l'étage 3 : l'écran montre une trace plate, le signal est absent. "
        "Les sorties des étages 1 et 4 ne sont pas mesurées. "
        "Conclusion : l'entrée de l'étage 3 est correcte et sa sortie absente, la panne est dans l'étage 3, "
        "ou en aval si l'étage 4 charge sa sortie ; déconnecter la charge et mesurer de nouveau.",
        b,
    )


def _dip8(x0: float) -> tuple[str, Point, Point]:
    """Eight-pin chip seen from above. Returns (svg, pin 4 tip, pin 6 tip)."""
    left, right, top = x0 + 250, x0 + 330, 170
    o = f'  <rect x="{left}" y="{top}" width="80" height="120" rx="4" fill="#20242b" stroke="#7d8794"/>\n'
    o += f'  <path d="M{left + 32} {top} a8 8 0 0 0 16 0" fill="#3b4049" stroke="#7d8794"/>\n'
    for i in range(4):
        y = top + 15 + 30 * i
        o += f'  <rect x="{left - 12}" y="{y - 4}" width="12" height="8" fill="#c9d0d9" stroke="#7d8794"/>\n'
        o += f'  <rect x="{right}" y="{y - 4}" width="12" height="8" fill="#c9d0d9" stroke="#7d8794"/>\n'
        o += f'  <text x="{left + 10}" y="{y + 4}" font-size="9" fill="#aeb6c2">{i + 1}</text>\n'
        o += f'  <text x="{right - 10}" y="{y + 4}" font-size="9" text-anchor="end" fill="#aeb6c2">{8 - i}</text>\n'
    o += text(left - 16, top + 94, "4 : masse", "mut", 11, "end")
    return o, (left - 8, top + 105), (right + 8, top + 75)


# ---------------------------------------------------------------- figure 2
def fig_compare() -> str:
    b = heading(
        "Comparer avec une carte saine : même point, même mode",
        "Hors tension et déchargées, mode diode, pointe rouge sur la masse (broche 4), noire sur la broche 6",
    )
    b += '  <path class="grid" d="M380 84 V520"/>\n'
    for x0, lcd, title, notes, cls, head, sub in (
        (
            0,
            "0.548",
            "Carte saine",
            ("La diode de", "protection de la", "broche conduit."),
            "ok",
            "✓ 0,548 V : la référence",
            "noter chaque broche dans un tableau",
        ),
        (
            380,
            "0.012",
            "Carte en panne",
            ("Presque 0 V :", "la broche est", "reliée à la masse."),
            "no",
            "✗ 0,012 V : écart net",
            "broche 6 en court-circuit avec la masse",
        ),
    ):
        o, v, com = half_meter(x0, "DIODE", lcd, "V", title, notes)
        chip, pin4, pin6 = _dip8(x0)
        b += o + chip + hookup(v, com, pin4, pin6)
        b += verdict(x0 + 190, 478, head, sub, cls)
    return svg(
        760,
        526,
        "Comparaison d'une broche entre une carte saine et une carte en panne",
        "Deux multimètres en mode diode mesurent la même broche du même circuit intégré à huit broches, sur deux cartes identiques "
        "hors tension et déchargées : pointe rouge sur la broche 4, la masse, pointe noire sur la broche 6. "
        "Sur la carte saine, l'appareil lit 0,548 V : la diode de protection de la broche conduit, c'est la référence à noter dans un tableau. "
        "Sur la carte en panne, il lit 0,012 V : écart net, la broche 6 est en court-circuit avec la masse.",
        b,
    )


# ---------------------------------------------------------------- figure 3
# Same measurement on four identical channels; the third departs in two rows.
CHANNEL_ROWS = (
    ("Tension à vide, sous tension (V)", (2.68, 2.66, 2.71, 2.64), 2),
    ("Ω broche → masse, rouge sur la broche (kΩ)", (12.40, 12.38, 3.05, 12.41), 2),
    ("Mode diode, rouge sur la masse (V)", (0.552, 0.549, 0.214, 0.551), 3),
)


def odd_channel(values: tuple[float, ...], tol: float = 0.05) -> int | None:
    """Index of the one channel more than `tol` (relative) away from the median, else None."""
    med = sorted(values)[len(values) // 2]
    off = [i for i, v in enumerate(values) if abs(v - med) > tol * abs(med)]
    return off[0] if len(off) == 1 else None


def fig_channels() -> str:
    b = heading(
        "Comparer quatre voies identiques : la voie qui diffère",
        "Même mesure, mêmes points, même appareil, même calibre et même polarité sur chaque voie",
    )
    x_label, x_col, col_w, top, row_h = 24, 330, 100, 96, 56
    for c in range(4):
        b += text(
            x_col + col_w * c + col_w / 2,
            top + 20,
            f"Voie {c + 1}",
            "fg",
            14,
            "middle",
            700,
        )
    for r, (label, values, digits) in enumerate(CHANNEL_ROWS):
        y = top + 40 + row_h * r
        b += f'  <rect class="panel" x="{x_label - 8}" y="{y}" width="{x_col + col_w * 4 - x_label + 8}" height="{row_h - 8}" rx="6"/>\n'
        b += text(x_label, y + 30, label, "fg", 13)
        odd = odd_channel(values)
        for c, v in enumerate(values):
            cls = "no" if c == odd else "fg"
            weight = 700 if c == odd else None
            b += text(
                x_col + col_w * c + col_w / 2,
                y + 30,
                f"{v:.{digits}f}".replace(".", ","),
                cls,
                14,
                "middle",
                weight,
            )
    b += verdict(
        380,
        340,
        "Deux lignes désignent la voie 3 : la chercher entre son connecteur et le microcontrôleur",
        "la tension à vide ne la distingue pas : une seule mesure ne suffit pas",
        "no",
    )
    return svg(
        760,
        384,
        "Comparaison de la même mesure sur quatre voies identiques",
        "Un tableau compare quatre voies d'entrée identiques d'une même carte, mesurées aux mêmes points avec le même appareil, "
        "le même calibre et la même polarité. Tension à vide, sous tension : 2,68, 2,66, 2,71 et 2,64 V, aucune voie ne se distingue. "
        "Résistance de la broche à la masse, pointe rouge sur la broche : 12,40, 12,38, 3,05 et 12,41 kΩ, la voie 3 diffère. "
        "Mode diode, pointe rouge sur la masse : 0,552, 0,549, 0,214 et 0,551 V, la voie 3 diffère encore. "
        "Conclusion : deux lignes désignent la voie 3, à chercher entre son connecteur et le microcontrôleur ; "
        "la tension à vide ne la distinguait pas, une seule mesure ne suffit pas.",
        b,
    )


FIGURES = {
    "tracage": (fig_tracing, []),
    "comparaison": (fig_compare, ["DIODE", "DIODE"]),
    "voies-identiques": (fig_channels, []),
}
