"""Figures of guide 30, the inductor."""

from __future__ import annotations

import math

from elements import (
    MONO,
    Point,
    box,
    chart,
    curve,
    half_meter,
    heading,
    hookup,
    power_resistor,
    svg,
    text,
    verdict,
    winding,
)

METAL = "#9aa3ad"
DARK = "#20242b"
FERRITE = "#3a3f47"
COPPER = "#c8763a"

RING_PERIODS = 6  # periods of the ringing shown on each screen
RING_DECAY = {"sain": 2.5, "spire en court-circuit": 0.25}  # time constant, in periods
SERIES_OHMS = "22 kΩ"  # keeps the generator output from damping the tank
KICK_SUPPLY = 24  # volts across the coil before the switch opens
KICK_PEAK = -300  # volts at opening without a diode
KICK_CLAMP = -1.4  # volts at opening with a freewheel diode
KICK_OPEN = 3  # instant of opening, in ms


def ring(t: float, tau: float) -> float:
    """Damped oscillation at time `t` (in periods), unit amplitude, time constant `tau`."""
    return math.exp(-t / tau) * math.cos(2 * math.pi * t)


def kick(t: float, diode: bool) -> float:
    """Voltage across a 24 V coil at time `t` (ms); the switch opens at KICK_OPEN."""
    if t < KICK_OPEN:
        return KICK_SUPPLY
    if diode:
        return KICK_CLAMP if t < KICK_OPEN + 4 else 0
    return KICK_PEAK * math.exp(-(t - KICK_OPEN) / 0.4)


def _smd_inductor(cx: float, cy: float, marking: str) -> str:
    """Shielded surface-mount power inductor seen from above, its marking on the top."""
    o = f'  <rect x="{cx - 62}" y="{cy - 22}" width="124" height="44" fill="{METAL}"/>\n'
    o += f'  <rect x="{cx - 50}" y="{cy - 50}" width="100" height="100" rx="12" fill="{DARK}" stroke="#7d8794" stroke-width="1.5"/>\n'
    o += f'  <text x="{cx}" y="{cy + 9}" font-size="26" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#ffffff">{marking}</text>\n'
    return o


def _drum(
    cx: float, top: float, w: float = 74, h: float = 100
) -> tuple[str, Point, Point]:
    """Radial drum-core inductor seen from the side, leads pointing down.

    Returns (svg, a point on the left lead, a point on the right lead).
    """
    xl, xr, bot = cx - w * 0.22, cx + w * 0.22, top + h
    o = f'  <path d="M{xl:.1f} {bot} V{bot + 44} M{xr:.1f} {bot} V{bot + 44}" stroke="{METAL}" stroke-width="3" stroke-linecap="round"/>\n'
    o += f'  <rect x="{cx - w * 0.38:.1f}" y="{top + 10}" width="{w * 0.76:.1f}" height="{h - 20}" fill="{COPPER}" stroke="#8a4a1c"/>\n'
    for k in range(1, 10):
        y = top + 10 + (h - 20) * k / 10
        o += f'  <path d="M{cx - w * 0.38:.1f} {y:.1f} H{cx + w * 0.38:.1f}" stroke="#8a4a1c" stroke-width="1"/>\n'
    for y in (top, bot - 14):
        o += f'  <rect x="{cx - w / 2}" y="{y}" width="{w}" height="14" rx="4" fill="{FERRITE}" stroke="#7d8794"/>\n'
    return o, (xl, bot + 34), (xr, bot + 34)


# ---------------------------------------------------------------- figure 1
def fig_marking() -> str:
    b = heading(
        "Lire le marquage d'une inductance CMS",
        "Code à trois caractères, résultat en microhenrys (µH)",
    )
    for cx, marking, value, rule in (
        (130, "4R7", "4,7 µH", "R tient la place de la virgule"),
        (380, "100", "10 µH", "10 suivi de 0 zéro"),
        (630, "101", "100 µH", "10 suivi de 1 zéro"),
    ):
        b += _smd_inductor(cx, 160, marking)
        b += text(cx, 246, value, "blue", 18, "middle", 700)
        b += text(cx, 268, rule, "mut", 12, "middle")
    b += '  <path class="grid" d="M24 296 H736"/>\n'
    b += text(24, 326, "La règle", size=15, weight=700)
    b += text(
        24,
        350,
        "Les deux premiers chiffres donnent la valeur, le troisième le nombre de zéros à ajouter.",
        "mut",
        12,
    )
    b += text(
        24,
        368,
        "La lettre R remplace la virgule quand la valeur est inférieure à 10 µH.",
        "mut",
        12,
    )
    b += text(
        24,
        398,
        "« 100 » se lit 10 µH, pas 100 µH : en cas de doute, lire la valeur sur le schéma ou la mesurer.",
        "warn",
        12,
        weight=700,
    )
    return svg(
        760,
        420,
        "Lire le marquage à trois caractères d'une inductance CMS",
        "Trois inductances de puissance CMS vues de dessus, chacune avec son marquage. "
        "4R7 se lit 4,7 microhenrys : la lettre R tient la place de la virgule. "
        "100 se lit 10 microhenrys : 10 suivi de zéro zéro. "
        "101 se lit 100 microhenrys : 10 suivi d'un zéro. "
        "La règle : les deux premiers chiffres donnent la valeur, le troisième le nombre de zéros à ajouter, le résultat est en microhenrys. "
        "Le marquage 100 se lit 10 microhenrys et non 100 : en cas de doute, lire la valeur sur le schéma ou la mesurer.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def fig_continuity() -> str:
    b = heading(
        "Continuité du bobinage à l'ohmmètre",
        "Inductance dessoudée ou une patte levée, calibre 200 Ω ; lire d'abord la résistance des pointes seules",
    )
    b += '  <path class="grid" d="M380 84 V504"/>\n'
    for x0, lcd, title, notes, cls, head, sub in (
        (
            0,
            "0.3",
            "Bobinage continu",
            ("lecture proche de celle", "des pointes seules"),
            "ok",
            "✓ Quelques dixièmes d'ohm",
            "le fil n'est pas coupé",
        ),
        (
            380,
            "OL",
            "Bobinage coupé",
            ("aucun courant ne passe", "dans le fil"),
            "no",
            "✗ OL : bobinage coupé",
            "inductance à remplacer, cause à chercher",
        ),
    ):
        o, v, com = half_meter(x0, "200", lcd, "Ω", title, notes)
        part, left, right = _drum(x0 + 290, 196)
        b += o + part + hookup(v, com, left, right)
        b += verdict(x0 + 190, 478, head, sub, cls)
    b += text(
        380,
        528,
        "L'ohmmètre ne trouve que la coupure : une spire en court-circuit ne change presque pas la résistance.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        546,
        "Contrôler la continuité d'une inductance à l'ohmmètre",
        "Deux mesures côte à côte, multimètre sur le calibre 200 ohms, une pointe sur chaque patte d'une inductance bobinée dessoudée. "
        "À gauche, l'afficheur indique 0,3 ohm, une valeur proche de celle des pointes seules : le bobinage est continu. "
        "À droite, l'afficheur indique OL : le bobinage est coupé, l'inductance est à remplacer et la cause à chercher. "
        "L'ohmmètre ne trouve que la coupure : une spire en court-circuit ne change presque pas la résistance.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def _ring_setup() -> str:
    """Pulse generator behind its series resistor, capacitor and coil under test in parallel, oscilloscope across them."""
    o = box(40, 110, 130, 80, "Générateur", ("d'impulsions",))
    o += box(590, 110, 130, 80, "Oscilloscope", ("page i2",))
    o += '  <path class="wire" d="M170 130 H590 M170 170 H590"/>\n'
    o += (
        '  <g data-series="isolation">\n'
        + power_resistor(196, 256, 130, SERIES_OHMS, 22)
        + "  </g>\n"
    )
    o += '  <path class="wire" d="M340 130 V144 M340 156 V170 M324 144 H356 M324 156 H356"/>\n'
    o += '  <rect class="bg" x="452" y="131.5" width="16" height="37"/>\n'
    o += winding(460, 130, 170, 4)
    for x, y in ((340, 130), (340, 170), (460, 130), (460, 170)):
        o += f'  <circle class="blkf" cx="{x}" cy="{y}" r="3.5"/>\n'
    o += text(226, 100, "résistance en série", "mut", 12, "middle")
    o += text(340, 100, "condensateur", "mut", 12, "middle")
    o += text(340, 198, "0,001 à 1 µF", "mut", 12, "middle")
    o += text(460, 100, "bobinage à tester", "mut", 12, "middle")
    return o


def fig_ring_test() -> str:
    b = heading(
        "Test d'oscillation : trouver une spire en court-circuit",
        "Composant dessoudé : une impulsion, à travers une résistance, fait osciller le bobinage et son condensateur",
    )
    b += _ring_setup()
    b += '  <path class="grid" d="M24 222 H736"/>\n'
    steps = [i / 40 for i in range(RING_PERIODS * 40 + 1)]
    for x, name, cls, mark, head, sub in (
        (70, "sain", "fb", "ok", "✓ Plusieurs cycles", "bobinage sain"),
        (
            450,
            "spire en court-circuit",
            "fr",
            "no",
            "✗ Moins de deux cycles",
            "spire en court-circuit probable",
        ),
    ):
        tau = RING_DECAY[name]
        axes, at = chart(
            x,
            270,
            270,
            150,
            RING_PERIODS,
            2,
            [],
            [(1, "0")],
            "temps",
            "tension aux bornes",
        )
        b += axes
        b += (
            f'  <g data-ring="{name}">\n'
            + curve([at(t, 1 + 0.9 * ring(t, tau)) for t in steps], cls, 2.5)
            + "  </g>\n"
        )
        b += verdict(x + 135, 484, head, sub, mark)
    b += text(
        380,
        532,
        "Contrôler d'abord la continuité à l'ohmmètre. Sous 10 µH, comparer avec un composant identique reconnu bon.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        552,
        "Test d'oscillation d'un bobinage à l'oscilloscope",
        "En haut, le montage : un générateur d'impulsions attaque, à travers une résistance en série de 22 kilohms, un condensateur de 0,001 à 1 microfarad et le bobinage à tester branchés en parallèle ; un oscilloscope mesure la tension à leurs bornes. "
        "En bas, deux écrans. À gauche, la tension oscille pendant plusieurs cycles en s'amortissant lentement : le bobinage est sain. "
        "À droite, l'oscillation s'éteint en moins de deux cycles : une spire en court-circuit est probable. "
        "Contrôler d'abord la continuité à l'ohmmètre. Sous 10 microhenrys, comparer avec un composant identique reconnu bon.",
        b,
    )


# ---------------------------------------------------------------- figure 4
def fig_kick() -> str:
    b = heading(
        "Surtension à l'ouverture d'un circuit inductif",
        "Exemple publié : bobine alimentée en 24 V continu, courant coupé d'un coup à l'instant marqué",
    )
    axes, at = chart(
        70,
        120,
        410,
        240,
        10,
        360,
        [(KICK_OPEN, "ouverture")],
        [(20, "−300"), (120, "−200"), (220, "−100"), (320, "0")],
        "temps",
        "tension aux bornes de la bobine (V)",
    )
    b += axes
    steps = [i / 50 for i in range(501)]
    for diode, cls in ((False, "fr"), (True, "fb")):
        b += (
            f'  <g data-diode="{str(diode).lower()}">\n'
            + curve([at(t, 320 + kick(t, diode)) for t in steps], cls)
            + "  </g>\n"
        )
    for y, cls, head, sub in (
        (150, "fr", "Sans diode", "pointe d'environ −300 V"),
        (210, "fb", "Avec diode de roue libre", "environ −1,4 V"),
    ):
        b += curve([(516, y), (546, y)], cls, 4)
        b += text(556, y + 4, head, size=13, weight=700)
        b += text(556, y + 21, sub, "mut", 12)
    b += text(516, 280, "La bobine s'oppose à l'arrêt", "mut", 12)
    b += text(516, 297, "du courant : plus la coupure", "mut", 12)
    b += text(516, 314, "est brusque, plus la tension", "mut", 12)
    b += text(516, 331, "monte.", "mut", 12)
    b += text(
        24,
        424,
        "Bien au-dessus de 50 V : couper l'alimentation avant de débrancher une bobine, ne jamais l'ouvrir sous courant.",
        "warn",
        12,
        weight=700,
    )
    return svg(
        760,
        446,
        "Tension aux bornes d'une bobine quand on coupe son courant",
        "Courbe de la tension aux bornes d'une bobine alimentée en 24 volts continus, en fonction du temps. "
        "Avant l'ouverture, la tension vaut 24 volts. À l'ouverture, sans diode, elle plonge à environ moins 300 volts puis revient à zéro. "
        "Avec une diode de roue libre en parallèle sur la bobine, elle reste à environ moins 1,4 volt puis revient à zéro. "
        "La bobine s'oppose à l'arrêt du courant : plus la coupure est brusque, plus la tension monte. "
        "Cette pointe dépasse largement 50 volts : couper l'alimentation avant de débrancher une bobine, ne jamais l'ouvrir sous courant.",
        b,
    )


FIGURES = {
    "lire-le-marquage": (fig_marking, []),
    "continuite-a-l-ohmmetre": (fig_continuity, ["200", "200"]),
    "test-d-oscillation": (fig_ring_test, []),
    "surtension-a-l-ouverture": (fig_kick, []),
}
