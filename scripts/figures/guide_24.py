"""Figures of guide 24, the supercapacitor."""

from __future__ import annotations

from math import exp, log

from elements import (
    MONO,
    Point,
    chart,
    curve,
    half_meter,
    heading,
    hookup,
    power_resistor,
    svg,
    text,
    verdict,
)

METAL = "#9aa3ad"
SLEEVE = "#14532d"
EDGE = "#052e16"
STRIPE = "#d1d5db"


def _cell(
    cx: float, top: float, w: float = 92, h: float = 58
) -> tuple[str, Point, Point]:
    """Supercapacitor seen from the side, leads pointing down, marked 1 F 5.5 V.

    The light stripe with minus signs is on the right: the negative side.
    Returns (svg, a point on the positive lead, a point on the negative lead).
    """
    xl, xr, bot = cx - 24, cx + 24, top + h
    o = f'  <path d="M{xl} {bot} V{bot + 44} M{xr} {bot} V{bot + 44}" stroke="{METAL}" stroke-width="3" stroke-linecap="round"/>\n'
    o += f'  <rect x="{cx - w / 2}" y="{top}" width="{w}" height="{h}" rx="7" fill="{SLEEVE}" stroke="{EDGE}" stroke-width="1.5"/>\n'
    sx, sw = cx + w * 0.26, w * 0.16
    o += f'  <rect x="{sx:.1f}" y="{top + 6}" width="{sw:.1f}" height="{h - 12}" fill="{STRIPE}"/>\n'
    for k in (0.3, 0.5, 0.7):
        o += f'  <rect x="{sx + sw * 0.2:.1f}" y="{top + h * k - 1.5:.1f}" width="{sw * 0.6:.1f}" height="3" fill="{SLEEVE}"/>\n'
    for i, mark in enumerate(("1F", "5.5V")):
        o += f'  <text x="{cx - w * 0.12:.1f}" y="{top + h / 2 - 3 + 17 * i:.1f}" font-size="13" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#ffffff">{mark}</text>\n'
    return o, (xl, bot + 30), (xr, bot + 34)


def _notes(x: float, y: float, lines: tuple[str, ...], cls: str = "mut") -> str:
    return "".join(text(x, y + 17 * i, line, cls, 12) for i, line in enumerate(lines))


def _decay(v0: float, tau: float, xmax: float, steps: int = 60) -> list[Point]:
    """Points of v0 × exp(−t / tau) from 0 to xmax."""
    return [
        (xmax * k / steps, v0 * exp(-xmax * k / steps / tau)) for k in range(steps + 1)
    ]


def _level(at, xmax: float, volts: float, label: str) -> str:
    """Dashed horizontal line across a chart at `volts`, labelled at its right end when `label` is set."""
    (x1, y), (x2, _) = at(0, volts), at(xmax, volts)
    line = f'  <path class="blk" stroke-width="1" stroke-dasharray="4 4" fill="none" d="M{x1:.1f} {y:.1f} H{x2:.1f}"/>\n'
    return (
        line + text(x2 - 4, round(y - 5, 1), label, "mut", 11, "end") if label else line
    )


def _dot(p: Point, cls: str) -> str:
    return f'  <circle class="{cls}" cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4.5" fill="#ffffff" stroke-width="2.5"/>\n'


# ---------------------------------------------------------------- figure 1
def fig_discharge() -> str:
    b = heading(
        "Décharger un supercondensateur : des minutes, pas des secondes",
        "Exemple : 1 F chargé à 5,5 V, déchargé dans une résistance de 100 Ω 2 W",
    )
    o, v, com = half_meter(
        0,
        "VDC",
        "0.04",
        "V",
        "Résistance en place, voltmètre aux bornes",
        ("Laisser la résistance", "branchée pendant", "toute la décharge."),
    )
    cell, plus, minus = _cell(290, 236)
    b += o
    b += f'  <path class="wire" d="M246 200 H226 V{plus[1] - 16} H{plus[0]} M334 200 H354 V{minus[1] - 20} H{minus[0]}"/>\n'
    b += power_resistor(246, 334, 200, "100 Ω 2 W")
    b += cell + hookup(v, com, plus, minus)
    b += text(plus[0] - 10, plus[1] + 4, "+", "no", 16, "end", 700)
    b += text(minus[0] + 10, minus[1] + 2, "−", "fg", 16, weight=700)
    b += verdict(
        190, 478, "✓ 0,04 V : on peut mesurer", "revérifier avant chaque mesure", "ok"
    )

    tau = 100 / 60  # R × C = 100 s, in minutes
    axes, at = chart(
        450,
        150,
        270,
        210,
        10,
        6,
        [(t, str(t)) for t in (0, 2, 4, 6, 8, 10)],
        [(u, str(u)) for u in (0, 1, 2, 3, 4, 5)],
        "temps (minutes)",
        "tension aux bornes (V)",
    )
    b += text(410, 100, "La tension pendant la décharge", size=15, weight=700)
    b += axes + _level(at, 10, 1, "")
    b += curve([at(t, u) for t, u in _decay(5.5, tau, 10)], "fb")
    t1, t5 = tau * log(5.5), 5 * tau
    b += _dot(at(t1, 1), "fb") + _dot(at(t5, 5.5 * exp(-5)), "fb")
    b += text(at(t1, 1)[0] + 10, at(t1, 1)[1] - 22, "moins de 1 V", size=12, weight=700)
    b += text(at(t1, 1)[0] + 10, at(t1, 1)[1] - 7, "après 3 minutes", "mut", 12)
    b += text(
        at(t5, 0)[0], at(t5, 0)[1] - 64, "0,04 V", size=12, anchor="middle", weight=700
    )
    b += text(at(t5, 0)[0], at(t5, 0)[1] - 49, "après 8 minutes", "mut", 12, "middle")
    b += _notes(
        410,
        428,
        (
            "Au départ : 55 mA et 0,3 W dans la résistance.",
            "Durée pour tomber sous 1 % : 5 × R × C = 500 s.",
            "Un 1 000 µF, dans la même résistance : 0,5 s.",
        ),
        "fg",
    )
    b += text(
        380,
        528,
        "Jamais de tournevis ni de fil en court-circuit : la résistance fixe le courant, le voltmètre dit quand c'est fini.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        546,
        "Décharge d'un supercondensateur dans une résistance",
        "À gauche, un supercondensateur 1 F 5,5 V avec une résistance de 100 Ω 2 W branchée entre ses deux pattes ; un multimètre, sélecteur sur volts continus, pointe rouge sur la patte positive et pointe noire sur la patte négative, lit 0,04 V : on peut mesurer, en revérifiant avant chaque mesure. La résistance reste branchée pendant toute la décharge. "
        "À droite, le graphique de la tension aux bornes en fonction du temps : partie de 5,5 V, elle passe sous 1 V après 3 minutes et atteint 0,04 V après 8 minutes. "
        "Au départ, 55 mA et 0,3 W dans la résistance ; la durée pour tomber sous 1 % vaut 5 fois R fois C, soit 500 secondes. Un condensateur de 1 000 µF, dans la même résistance, se vide en 0,5 seconde. "
        "Jamais de tournevis ni de fil en court-circuit : la résistance fixe le courant, le voltmètre dit quand c'est fini.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def fig_capacity() -> str:
    b = heading(
        "Mesurer la capacité au chronomètre",
        "Supercondensateur chargé à 5 V, puis déchargé dans 1 kΩ : chronométrer le passage de 4 V à 2 V",
    )
    axes, at = chart(
        70,
        120,
        410,
        240,
        20,
        6,
        [(t, str(t)) for t in (0, 5, 10, 15, 20)],
        [(u, str(u)) for u in (0, 1, 2, 3, 4, 5)],
        "temps (minutes)",
        "tension aux bornes (V)",
    )
    b += axes + _level(at, 20, 4, "départ : 4 V") + _level(at, 20, 2, "arrêt : 2 V")
    for farads, cls, dy in ((0.5, "fr", -16), (1, "fb", -8)):
        tau = 1000 * farads / 60  # R × C, in minutes
        b += curve([at(t, u) for t, u in _decay(5, tau, 20)], cls)
        t4, t2 = tau * log(5 / 4), tau * log(5 / 2)
        b += _dot(at(t4, 4), cls) + _dot(at(t2, 2), cls)
        y = at(0, 0)[1] + dy
        b += curve([(at(t4, 0)[0], y), (at(t2, 0)[0], y)], cls, 5)
    for y, cls, head, sub in (
        (140, "fb", "sain : 11 min 33 s (693 s)", "693 / (0,69 × 1 000) = 1 F"),
        (188, "fr", "usé : 5 min 47 s (347 s)", "347 / (0,69 × 1 000) = 0,5 F"),
    ):
        b += curve([(516, y), (546, y)], cls, 4)
        b += text(556, y + 4, head, size=13, weight=700)
        b += text(556, y + 21, sub, "mut", 12)
    b += text(516, 252, "C = durée / (0,69 × R)", size=14, weight=700)
    b += _notes(
        516,
        274,
        (
            "durée en secondes, R en ohms,",
            "C en farads",
        ),
    )
    b += _notes(
        516,
        324,
        (
            "Fin de vie : 30 % de capacité",
            "perdus, soit moins de 0,7 F",
            "pour un 1 F.",
        ),
        "fg",
    )
    b += text(
        380,
        428,
        "Le capacimètre du multimètre ne sait pas lire un farad : sa plus grande gamme s'arrête bien avant.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        446,
        "Mesure de la capacité d'un supercondensateur par le temps de décharge",
        "Graphique de la tension aux bornes d'un supercondensateur chargé à 5 V puis déchargé dans une résistance de 1 kΩ, sur 20 minutes. On chronomètre le passage de 4 V à 2 V. "
        "Supercondensateur sain de 1 F : 11 minutes 33 secondes, soit 693 secondes ; 693 divisé par 0,69 fois 1 000 donne 1 F. "
        "Supercondensateur usé : 5 minutes 47 secondes, soit 347 secondes, ce qui donne 0,5 F. "
        "Formule : C égale la durée divisée par 0,69 fois R, durée en secondes, R en ohms, C en farads. "
        "Fin de vie : 30 % de capacité perdus, soit moins de 0,7 F pour un 1 F. "
        "Le capacimètre du multimètre ne sait pas lire un farad : sa plus grande gamme s'arrête bien avant.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def fig_self_discharge() -> str:
    b = heading(
        "Autodécharge : un supercondensateur reste chargé des semaines",
        "Supercondensateur 5,5 V chargé, puis laissé seul, rien de branché à ses bornes",
    )
    axes, at = chart(
        70,
        120,
        410,
        240,
        600,
        6,
        [(t, str(t)) for t in (0, 100, 200, 300, 400, 500, 600)],
        [(u, str(u)) for u in (0, 1, 2, 3, 4, 5)],
        "temps (heures)",
        "tension aux bornes (V)",
    )
    b += axes + _level(at, 600, 3, "3 V")
    for tau, cls in ((24 / log(5.5 / 3), "fr"), (600 / log(5.5 / 3), "fb")):
        b += curve([at(t, u) for t, u in _decay(5.5, tau, 600, 200)], cls)
    b += _dot(at(600, 3), "fb") + _dot(at(24, 3), "fr")
    for y, cls, head, sub in (
        (140, "fb", "sain", "encore 3 V après 600 h (25 jours)"),
        (188, "fr", "défectueux (exemple)", "sous 3 V en une journée"),
    ):
        b += curve([(516, y), (546, y)], cls, 4)
        b += text(556, y + 4, head, size=13, weight=700)
        b += text(556, y + 21, sub, "mut", 12)
    b += _notes(
        516,
        250,
        (
            "Symptôme : l'horloge ou les",
            "réglages se perdent après une",
            "coupure bien plus courte que",
            "prévu.",
        ),
        "fg",
    )
    b += _notes(
        516,
        336,
        (
            "Mesure : charger, isoler, puis",
            "relever la tension après 1 h,",
            "24 h et une semaine.",
        ),
    )
    b += text(
        380,
        428,
        "Débranchée depuis des semaines, une carte peut encore porter un supercondensateur chargé : vérifier au voltmètre.",
        "warn",
        12,
        "middle",
        700,
    )
    return svg(
        760,
        446,
        "Autodécharge d'un supercondensateur sain ou défectueux",
        "Graphique de la tension aux bornes d'un supercondensateur 5,5 V chargé puis laissé seul, sur 600 heures. "
        "Supercondensateur sain : la tension descend lentement, il reste encore 3 V après 600 heures, soit 25 jours. "
        "Supercondensateur défectueux, à titre d'exemple : la tension passe sous 3 V en une journée. "
        "Symptôme : l'horloge ou les réglages se perdent après une coupure bien plus courte que prévu. "
        "Mesure : charger, isoler, puis relever la tension après 1 heure, 24 heures et une semaine. "
        "Débranchée depuis des semaines, une carte peut encore porter un supercondensateur chargé : vérifier au voltmètre.",
        b,
    )


FIGURES = {
    "decharge-sur-resistance": (fig_discharge, ["VDC"]),
    "mesure-de-capacite": (fig_capacity, []),
    "autodecharge": (fig_self_discharge, []),
}
