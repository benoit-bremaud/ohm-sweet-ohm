"""Figures of guide 14, the platinum resistance temperature sensor (PT1000) and its input channel."""

from __future__ import annotations

import math

from elements import (
    BLUE,
    MONO,
    Point,
    bands,
    half_meter,
    heading,
    hookup,
    res_h,
    screen,
    svg,
    text,
    verdict,
)

# Callendar-Van Dusen coefficients for 0 °C and above (IEC 60751 curve, alpha = 0.00385 /°C)
A = 3.9083e-3
B = -5.775e-7
R0 = 1000.0


def pt1000_ohms(t: float) -> float:
    """Resistance of a PT1000 at t °C, for 0 °C and above."""
    if t < 0:
        raise ValueError("the curve used here holds from 0 °C up")
    return R0 * (1 + A * t + B * t * t)


def pt1000_celsius(r: float) -> float:
    """Temperature a board computes from resistance r (inverse of pt1000_ohms), r ≥ R0."""
    if r < R0:
        raise ValueError("below 1000 Ω the sensor is under 0 °C, out of this curve")
    return (-A + math.sqrt(A * A - 4 * B * (1 - r / R0))) / (2 * B)


def fr(x: float, digits: int = 1) -> str:
    """Number with a French decimal comma."""
    return f"{round(x, digits) + 0.0:.{digits}f}".replace(".", ",")


def pulse_train(
    high: float, duty: float, periods: int = 3, cols: int = 6
) -> list[Point]:
    """Rectangular excitation in screen divisions: `high` divisions during `duty` of each period."""
    if not 0 < duty < 1:
        raise ValueError("duty must be strictly between 0 and 1")
    period = cols / periods
    pts: list[Point] = [(0.0, 0.0)]
    for k in range(periods):
        x0 = k * period + period * (1 - duty) / 2
        x1 = x0 + period * duty
        pts += [(x0, 0.0), (x0, high), (x1, high), (x1, 0.0)]
    return [*pts, (float(cols), 0.0)]


def _header(x: float, y: float, label: str) -> tuple[str, Point, Point]:
    """Two-pin header seen from above, pin 1 on the left. Returns (svg, pin 1, pin 2)."""
    o = f'  <rect x="{x}" y="{y}" width="64" height="32" rx="3" fill="#f5f0e6" stroke="#8a7f6b"/>\n'
    p1, p2 = (x + 18, y + 16), (x + 46, y + 16)
    for px, py in (p1, p2):
        o += f'  <rect x="{px - 6}" y="{py - 6}" width="12" height="12" fill="#c9a227" stroke="#7a6212"/>\n'
    o += text(x + 32, y + 50, label, "mut", 11, "middle")
    return o, p1, p2


def _board_display(x: float, y: float, line: str) -> str:
    """Read-out of the board (its screen or service tool), fixed dark colours."""
    return (
        f'  <rect x="{x}" y="{y}" width="150" height="40" rx="5" fill="#0c0e11" stroke="#11151a"/>\n'
        f'  <text x="{x + 75}" y="{y + 26}" font-size="17" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#4ade80">{line}</text>\n'
    )


# ---------------------------------------------------------------- figure 1
# value -> colour bands of a five-band 0.1 % metal-film resistor
SUBSTITUTES = {
    1000.0: ("brown", "black", "black", "brown", "violet"),
    1100.0: ("brown", "brown", "black", "brown", "violet"),
}


def fig_substitution() -> str:
    b = heading(
        "Remplacer la sonde par une résistance connue",
        "Carte sous tension, sonde débranchée, résistance 0,1 % enfichée dans le connecteur de la voie",
    )
    b += '  <path class="grid" d="M380 84 V340"/>\n'
    for x0, (r, code) in zip((0, 380), SUBSTITUTES.items(), strict=True):
        t = pt1000_celsius(r)
        b += text(
            x0 + 20, 100, f"{r:.0f} Ω à la place de la PT1000", size=15, weight=700
        )
        b += f'  <rect class="panel" x="{x0 + 30}" y="200" width="320" height="120" rx="10" stroke-width="1.5"/>\n'
        b += text(x0 + 334, 222, "Carte de commande", "fg", 13, "end", 700)
        h, p1, p2 = _header(x0 + 60, 250, "connecteur T2")
        b += h
        # resistor bent over the header: one lead in each pin
        b += f'  <path stroke="#aab2bd" stroke-width="3" fill="none" d="M{p1[0]} {p1[1]} V140 M{p2[0]} {p2[1]} V140"/>\n'
        b += res_h(p1[0] - 22, p2[0] + 22, 128, 22, bands(*code), BLUE)
        b += text(x0 + 140, 132, f"{r:.0f} Ω ± 0,1 %", "blue", 13, weight=700)
        b += _board_display(x0 + 180, 252, f"T2 {fr(t)} °C")
        b += text(x0 + 255, 310, "affichage de la carte", "mut", 11, "middle")
    b += verdict(
        380,
        374,
        "La carte lit 0 °C puis ≈ 26 °C : la voie est saine, la sonde ou son câble est en cause",
        "Elle lit une autre valeur ou reste en défaut : la panne est sur la carte, dans cette voie",
        "ok",
    )
    t0, t1 = (fr(pt1000_celsius(r)) for r in SUBSTITUTES)
    return svg(
        760,
        420,
        "Substitution d'une sonde PT1000 par une résistance de précision",
        "Deux panneaux. La carte de commande est sous tension, la sonde PT1000 de la voie T2 est débranchée "
        "et une résistance à 0,1 % est enfichée dans les deux broches du connecteur T2. "
        f"À gauche, 1000 Ω : l'affichage de la carte indique {t0} °C. "
        f"À droite, 1100 Ω : il indique {t1} °C, soit environ 26 °C. "
        "Conclusion : si la carte lit ces valeurs, la voie est saine et la sonde ou son câble est en cause ; "
        "si elle lit autre chose ou reste en défaut, la panne est sur la carte, dans cette voie.",
        b,
    )


# ---------------------------------------------------------------- figures 2 and 3
def _pin_pair(x0: float, pin_left: bool) -> tuple[str, Point, Point]:
    """Input pin and ground pad of a channel; returns (svg, left point, right point)."""
    left, right = (x0 + 250, 230), (x0 + 330, 230)
    names = ("broche", "masse") if pin_left else ("masse", "broche")
    o = ""
    for (px, py), name in zip((left, right), names, strict=True):
        o += f'  <rect x="{px - 9}" y="{py - 9}" width="18" height="18" fill="#c9a227" stroke="#7a6212"/>\n'
        o += text(px, py - 18, name, "fg", 12, "middle", 700)
    return o, left, right


def fig_resistance() -> str:
    b = heading(
        "Résistance d'une entrée à la masse, dans les deux sens",
        "Carte hors tension et déchargée, sélecteur sur Ω, calibre 20 kΩ ; valeurs d'exemple",
    )
    b += '  <path class="grid" d="M380 84 V520"/>\n'
    for x0, lcd, title, notes, pin_left, head, sub in (
        (
            0,
            "12.40",
            "Rouge sur la broche",
            ("La diode de", "protection est", "bloquée."),
            True,
            "12,40 kΩ : le chemin résistif",
            "résistances de la voie, rail, charges",
        ),
        (
            380,
            "4.71",
            "Rouge sur la masse",
            ("La diode de", "protection vers", "la masse conduit."),
            False,
            "4,71 kΩ : plus bas, c'est normal",
            "la jonction s'ajoute en parallèle",
        ),
    ):
        o, v, com = half_meter(x0, "20k", lcd, "kΩ", title, notes)
        pads, left, right = _pin_pair(x0, pin_left)
        b += o + pads + hookup(v, com, left, right)
        b += verdict(x0 + 190, 478, head, sub, "ok")
    return svg(
        760,
        526,
        "Résistance entre une entrée de mesure et la masse, dans les deux sens des pointes",
        "Deux multimètres sur le calibre 20 kΩ mesurent la même entrée de mesure d'une carte hors tension et déchargée ; valeurs d'exemple. "
        "À gauche, pointe rouge sur la broche d'entrée, noire sur la masse : la diode de protection entre la masse et la broche est bloquée, "
        "l'appareil lit 12,40 kΩ, le chemin résistif de la voie. "
        "À droite, pointe rouge sur la masse, noire sur la broche : cette diode conduit et s'ajoute en parallèle, l'appareil lit 4,71 kΩ. "
        "Deux lectures différentes selon le sens des pointes sont normales sur une broche protégée par des diodes.",
        b,
    )


def fig_diode() -> str:
    b = heading(
        "Mode diode sur une entrée : la diode de protection vers la masse",
        "Carte hors tension et déchargée, sélecteur sur le mode diode",
    )
    b += '  <path class="grid" d="M380 84 V520"/>\n'
    for x0, lcd, title, notes, pin_left, head, sub, cls in (
        (
            0,
            "0.552",
            "Rouge sur la masse",
            ("La diode entre", "la masse et la", "broche conduit."),
            False,
            "0,552 V : jonction silicium",
            "de 0,5 à 0,7 V à environ 1 mA",
            "ok",
        ),
        (
            380,
            "OL",
            "Rouge sur la broche",
            ("Cette diode est", "bloquée : rien ne", "passe vers la masse."),
            True,
            "OL : sens bloqué",
            "ou une valeur plus haute : diode vers le rail",
            "ok",
        ),
    ):
        o, v, com = half_meter(x0, "DIODE", lcd, "V", title, notes)
        pads, left, right = _pin_pair(x0, pin_left)
        b += o + pads + hookup(v, com, left, right)
        b += verdict(x0 + 190, 478, head, sub, cls)
    return svg(
        760,
        526,
        "Mode diode sur une entrée de mesure, dans les deux sens",
        "Deux multimètres en mode diode mesurent la même entrée de mesure d'une carte hors tension et déchargée. "
        "À gauche, pointe rouge sur la masse, noire sur la broche : la diode de protection entre la masse et la broche conduit, "
        "l'appareil lit 0,552 V, une jonction silicium, de 0,5 à 0,7 V à environ 1 mA. "
        "À droite, pointe rouge sur la broche, noire sur la masse : cette diode est bloquée, l'appareil affiche OL ; "
        "certaines cartes lisent ici une valeur plus haute, celle de la diode vers le rail d'alimentation et de ce que le rail charge.",
        b,
    )


# ---------------------------------------------------------------- figure 5
PULSE_HIGH, PULSE_DUTY = 2.5, 0.2


def fig_pulsed() -> str:
    b = heading(
        "Excitation pulsée : le multimètre moyenne, l'oscilloscope montre",
        "Carte sous tension, sonde branchée, mesure entre l'entrée de la voie et la masse",
    )
    b += '  <path class="grid" d="M380 84 V520"/>\n'
    b += text(20, 100, "Oscilloscope, pince sur la masse", size=15, weight=700)
    b += screen(30, 120, 320, 200, 6, 4, pulse_train(PULSE_HIGH, PULSE_DUTY))
    b += text(30, 344, "La voie n'est alimentée que pendant de courtes", "mut", 12)
    b += text(
        30, 360, "impulsions, puis la mesure passe à la voie suivante.", "mut", 12
    )
    b += verdict(
        190,
        478,
        "La forme réelle : impulsions et repos",
        "comparer le niveau des impulsions voie par voie",
        "ok",
    )
    o, v, com = half_meter(
        380,
        "VDC",
        "0.41",
        "V",
        "Multimètre",
        ("Une moyenne qui", "change à chaque", "lecture."),
    )
    pads, left, right = _pin_pair(380, True)
    b += o + pads + hookup(v, com, left, right)
    b += verdict(
        570,
        478,
        "Une valeur instable, sans défaut",
        "l'appareil intègre des impulsions trop brèves",
        "warn",
    )
    return svg(
        760,
        526,
        "Excitation pulsée d'une sonde : multimètre et oscilloscope",
        "Carte sous tension, sonde branchée, mesure entre l'entrée de la voie et la masse. "
        "À gauche, l'oscilloscope, pince de masse sur la masse de la carte, montre des impulsions rectangulaires brèves séparées de longs repos à 0 V : "
        "la voie n'est alimentée que pendant ces impulsions, puis la mesure passe à la voie suivante. "
        "À droite, un multimètre sur le calibre tension continue, pointe rouge sur la broche d'entrée, noire sur la masse, affiche 0,41 V, valeur d'exemple, "
        "une moyenne qui change à chaque lecture : l'appareil intègre des impulsions trop brèves, cette instabilité n'est pas un défaut. "
        "Pour comparer deux voies, comparer le niveau des impulsions à l'oscilloscope.",
        b,
    )


def apparent_error(t: float, drift: float) -> float:
    """Error in °C when the reference resistor in series with the sensor drifts by `drift` ohms.

    Model (an assumption, the firmware is unknown): the board measures the series sum of sensor
    and reference and subtracts the nominal reference, so the whole drift lands on the sensor.
    """
    return pt1000_celsius(pt1000_ohms(t) + drift) - t


def _res_sym(x1: float, x2: float, y: float, label: str, cls: str = "fg") -> str:
    """Horizontal IEC resistor symbol (rectangle) on a wire from x1 to x2, label above."""
    m = (x1 + x2) / 2
    return (
        f'  <path class="wire" d="M{x1} {y} H{m - 30} M{m + 30} {y} H{x2}"/>\n'
        f'  <rect class="panel" x="{m - 30}" y="{y - 11}" width="60" height="22" stroke-width="2.5"/>\n'
        + text(m, y - 18, label, cls, 12, "middle", 700)
    )


def _ground(x: float, y: float) -> str:
    return f'  <path class="wire" d="M{x} {y} v10 M{x - 14} {y + 10} h28 M{x - 9} {y + 16} h18 M{x - 4} {y + 22} h8"/>\n'


# ---------------------------------------------------------------- figure 6
def fig_channel() -> str:
    b = heading(
        "Une voie d'entrée PT1000 : de la sonde au convertisseur",
        "Schéma partiel type ; la source d'excitation dépend de la carte et n'est pas relevée ici",
    )
    # sensor and its connector
    b += _res_sym(40, 200, 200, "PT1000 (sonde)", "blue")
    b += text(120, 240, "carte de filtrage éventuelle", "mut", 11, "middle")
    b += text(120, 256, "entre sonde et connecteur", "mut", 11, "middle")
    b += '  <path class="wire" d="M40 200 V300 H200"/>\n'
    b += '  <rect class="panel" x="200" y="180" width="40" height="140" rx="4" stroke-width="1.5"/>\n'
    b += text(220, 172, "connecteur", "mut", 11, "middle")
    b += text(220, 205, "a", "fg", 13, "middle", 700) + text(
        220, 305, "b", "fg", 13, "middle", 700
    )
    # pin b: reference resistor to ground
    b += '  <path class="wire" d="M240 300 H300 V320"/>\n'
    b += '  <path class="wire" d="M300 320 V330"/>\n'
    b += '  <rect class="panel" x="289" y="330" width="22" height="50" stroke-width="2.5"/>\n'
    b += '  <path class="wire" d="M300 380 V392"/>\n' + _ground(300, 392)
    b += text(320, 352, "R réf 1 kΩ 0,1 %", "amber", 12, weight=700)
    b += text(320, 368, "référence de mesure", "mut", 11)
    # pin a: RC filter, multiplexer, ADC
    b += _res_sym(240, 380, 200, "R filtre (supposée)").replace(
        'stroke-width="2.5"/>', 'stroke-width="2.5" stroke-dasharray="5 4"/>'
    )
    b += '  <path class="wire" d="M380 200 H440"/>\n'
    b += (
        '  <path class="wire" d="M410 200 V236 M396 236 h28 M396 244 h28 M410 244 V256"/>\n'
        + _ground(410, 256)
    )
    b += text(430, 250, "C", "fg", 12, weight=700)
    b += '  <rect class="panel" x="440" y="150" width="120" height="120" rx="6" stroke-width="1.5"/>\n'
    b += text(500, 176, "Multiplexeur", "fg", 12, "middle", 700)
    b += text(500, 194, "analogique 4:1", "mut", 11, "middle")
    for i in range(4):
        b += text(452, 216 + 14 * i, f"S{i + 1}", "mut", 10)
    b += text(500, 262, "voies 1 à 4", "mut", 11, "middle")
    b += '  <path class="wire" d="M560 210 H600"/>\n'
    b += '  <rect class="panel" x="600" y="160" width="136" height="100" rx="6" stroke-width="1.5"/>\n'
    b += text(668, 196, "Microcontrôleur", "fg", 12, "middle", 700)
    b += text(668, 214, "entrée du CAN", "mut", 11, "middle")
    b += text(668, 232, "(convertisseur", "mut", 11, "middle")
    b += text(668, 248, "analogique-numérique)", "mut", 11, "middle")
    b += text(
        40,
        440,
        "La carte calcule la température à partir de la sonde et de R réf : une dérive de R réf",
        "fg",
        13,
    )
    b += text(
        40, 458, "fausse la température sans aucun défaut sur la sonde.", "fg", 13
    )
    return svg(
        760,
        480,
        "Schéma partiel d'une voie d'entrée PT1000",
        "Schéma partiel type d'une voie d'entrée de sonde PT1000. La sonde est branchée sur les broches a et b d'un connecteur. "
        "La broche b rejoint la masse par une résistance de référence de 1 kΩ à 0,1 %. "
        "La broche a passe par un filtre : un condensateur vers la masse, précédé d'une résistance série supposée, dessinée en pointillé, puis entre dans un multiplexeur analogique à quatre voies, "
        "dont la sortie attaque l'entrée du convertisseur analogique-numérique du microcontrôleur. "
        "La source d'excitation dépend de la carte et n'est pas représentée ; sur certains appareils, une carte de filtrage s'intercale entre la sonde et le connecteur. "
        "La carte calcule la température à partir de la sonde et de la résistance de référence : une dérive de celle-ci fausse la température sans défaut sur la sonde.",
        b,
    )


# ---------------------------------------------------------------- figure 7
FUNNEL = (
    ("Connecteur", "broche b → masse", 1071, 994),
    ("Via", "bipeur, broche b → pastille", None, None),
    ("Résistance", "aux bornes de R réf", 1071, 994),
)


def fig_funnel() -> str:
    b = heading(
        "Remonter la voie suspecte, comparée à sa jumelle",
        "Hors tension, ohmmètre, mêmes points sur les deux voies ; pointes inversées : même valeur",
    )
    b += text(250, 108, "Voie suspecte", "no", 14, "middle", 700)
    b += text(400, 108, "Voie jumelle", "ok", 14, "middle", 700)
    b += text(560, 108, "Écart", "fg", 14, "middle", 700)
    for i, (stage, where, bad, good) in enumerate(FUNNEL):
        y = 128 + 74 * i
        w = 700 - 40 * i
        b += f'  <rect class="panel" x="{380 - w / 2}" y="{y}" width="{w}" height="58" rx="8" stroke-width="1.5"/>\n'
        b += text(380 - w / 2 + 14, y + 25, f"{i + 1}. {stage}", "fg", 13, weight=700)
        b += text(380 - w / 2 + 14, y + 43, where, "mut", 11)
        if bad is None or good is None:
            b += text(250, y + 35, "bip", "fg", 15, "middle")
            b += text(400, y + 35, "bip", "fg", 15, "middle")
            b += text(560, y + 35, "aucun", "mut", 14, "middle")
            continue
        b += text(250, y + 35, f"{bad} Ω", "no", 15, "middle", 700)
        b += text(400, y + 35, f"{good} Ω", "fg", 15, "middle")
        b += text(
            560, y + 35, f"+{fr(100 * (bad - good) / good)} %", "no", 14, "middle", 700
        )
    b += verdict(
        380,
        370,
        "L'écart se retrouve aux bornes de la résistance : R réf a dérivé",
        "pointes inversées, même lecture : chemin purement résistif, pas une jonction",
        "no",
    )
    return svg(
        760,
        408,
        "Entonnoir de comparaison d'une voie suspecte avec sa voie jumelle",
        "Carte hors tension et déchargée, ohmmètre, mêmes points sur la voie suspecte et sur sa voie jumelle, puis pointes inversées : même valeur, le chemin est purement résistif. "
        "Étape 1, au connecteur, broche b vers la masse : 1071 Ω contre 994 Ω. "
        "Étape 2, continuité de la broche b à la pastille de la résistance à travers le via : bip sur les deux voies, aucun écart. "
        "Étape 3, aux bornes de la résistance de référence : 1071 Ω contre 994 Ω. "
        f"L'écart, +{fr(100 * 77 / 994)} %, se retrouve aux bornes de la résistance : la résistance de référence a dérivé. "
        "Les pointes inversées donnent la même lecture : le chemin est purement résistif, ce n'est pas une jonction.",
        b,
    )


# ---------------------------------------------------------------- figure 8
DRIFT_T, DRIFT = 20.0, 71.0


def fig_drift() -> str:
    rpt = pt1000_ohms(DRIFT_T)
    seen = pt1000_celsius(rpt + DRIFT)
    err = apparent_error(DRIFT_T, DRIFT)
    b = heading(
        "Une référence qui dérive de 7 % : environ 20 °C d'erreur",
        "Calcul d'exemple, en supposant que la carte retranche la valeur nominale de R réf",
    )
    rows = (
        ("Sonde PT1000 à 20 °C", f"{fr(rpt)} Ω", "fg"),
        ("R réf réelle (nominale 1000 Ω)", f"{fr(1000 + DRIFT, 0)} Ω", "no"),
        ("Somme mesurée par la carte", f"{fr(rpt + 1000 + DRIFT)} Ω", "fg"),
        ("Moins la valeur nominale de R réf", "− 1000,0 Ω", "fg"),
        ("Résistance attribuée à la sonde", f"{fr(rpt + DRIFT)} Ω", "no"),
        ("Température affichée", f"{fr(seen)} °C", "no"),
    )
    for i, (label, value, cls) in enumerate(rows):
        y = 112 + 34 * i
        b += text(60, y, label, "fg", 14)
        b += text(560, y, value, cls, 15, "end", 700)
    b += '  <path class="grid" d="M60 298 H560"/>\n'
    b += text(60, 326, "Erreur", "fg", 15, weight=700)
    b += text(560, 326, f"+{fr(err)} °C", "no", 17, "end", 700)
    b += text(
        60,
        366,
        "Règle : une PT1000 varie d'environ 3,85 Ω par degré ; chaque ohm de dérive en série",
        "mut",
        12,
    )
    b += text(60, 384, "avec elle ajoute environ un quart de degré.", "mut", 12)
    return svg(
        760,
        408,
        "Effet d'une dérive de la résistance de référence sur la température lue",
        "Calcul d'exemple, en supposant que la carte mesure la somme de la sonde et de la résistance de référence puis retranche la valeur nominale de celle-ci. "
        f"Sonde PT1000 à 20 °C : {fr(rpt)} Ω. Résistance de référence réelle : {fr(1000 + DRIFT, 0)} Ω au lieu de 1000 Ω. "
        f"La carte attribue {fr(rpt + DRIFT)} Ω à la sonde et affiche {fr(seen)} °C, soit une erreur de +{fr(err)} °C. "
        "Règle : une PT1000 varie d'environ 3,85 Ω par degré, chaque ohm de dérive en série ajoute environ un quart de degré.",
        b,
    )


# ---------------------------------------------------------------- figure 9
def fig_coating() -> str:
    b = heading(
        "Mesurer à travers un vernis de tropicalisation",
        "Carte hors tension et déchargée ; pointe fine sur la pastille, jamais sur le corps du composant",
    )
    # board cross-section: substrate, pad, component, coating
    b += '  <rect x="40" y="300" width="400" height="34" fill="#2f6b3a" stroke="#1d4426"/>\n'
    b += '  <rect x="110" y="290" width="70" height="10" fill="#c9a227" stroke="#7a6212"/>\n'
    b += '  <rect x="300" y="290" width="70" height="10" fill="#c9a227" stroke="#7a6212"/>\n'
    b += '  <rect x="160" y="258" width="160" height="32" rx="3" fill="#20242b" stroke="#7d8794"/>\n'
    b += '  <path d="M40 300 V292 H104 Q110 282 120 284 L156 256 Q240 244 324 256 L360 284 Q370 282 376 292 H440 V300" fill="#93c5fd" fill-opacity="0.45" stroke="#2563eb" stroke-width="1.5"/>\n'
    b += text(440, 276, "vernis", "blue", 12, "end", 700)
    b += text(
        240, 356, "pastille        composant        pastille", "mut", 11, "middle"
    )
    # needle tip alone (no meter here): steel needle then red handle, tip on the pad
    b += '  <path d="M130 288 L114 262" stroke="#c0c7d0" stroke-width="2.5" stroke-linecap="round"/>\n'
    b += '  <path d="M114 262 L84 212" stroke="#dc2626" stroke-width="12" stroke-linecap="round"/>\n'
    b += text(60, 170, "pointe-aiguille inclinée,", "fg", 12)
    b += text(60, 186, "sur la pastille", "fg", 12)
    notes = (
        ("Repérer", "une lampe UV fait souvent briller le vernis"),
        ("Acrylique", "se dissout à l'alcool isopropylique, localement"),
        ("Silicone", "ne se dissout pas : gratter sur la pastille seule"),
        ("Outil", "stylo fibre de verre ou scalpel, pastille seule"),
        ("Jamais", "près des broches à pas fin"),
        ("Après", "revernir la zone (stylo de vernis)"),
    )
    for i, (head, sub) in enumerate(notes):
        y = 120 + 44 * i
        b += text(480, y, head, "warn" if head == "Jamais" else "fg", 13, weight=700)
        b += text(480, y + 17, sub, "mut", 12)
    return svg(
        760,
        400,
        "Mesure à travers un vernis de tropicalisation",
        "Coupe d'une carte recouverte de vernis de tropicalisation : un composant CMS sur deux pastilles, le tout sous une couche de vernis. "
        "Une pointe-aiguille rouge, inclinée, traverse le vernis sur la pastille, jamais sur le corps du composant ; carte hors tension et déchargée. "
        "À droite, les règles : une lampe UV fait souvent briller le vernis ; un vernis acrylique se dissout localement à l'alcool isopropylique ; "
        "un vernis silicone ne se dissout pas, on le gratte sur la pastille seule ; outil : stylo fibre de verre ou scalpel, sur la pastille seule ; "
        "jamais près des broches à pas fin ; après la réparation, revernir la zone au stylo de vernis.",
        b,
    )


FIGURES = {
    "substitution": (fig_substitution, []),
    "resistance-deux-sens": (fig_resistance, ["20k", "20k"]),
    "mode-diode-entree": (fig_diode, ["DIODE", "DIODE"]),
    "excitation-pulsee": (fig_pulsed, ["VDC"]),
    "schema-voie": (fig_channel, []),
    "entonnoir-voie-jumelle": (fig_funnel, []),
    "derive-reference": (fig_drift, []),
    "mesure-sous-vernis": (fig_coating, []),
}
