"""Figures of guide 23, the tantalum capacitor."""

from __future__ import annotations

from elements import (
    MONO,
    Point,
    half_meter,
    heading,
    hookup,
    svg,
    text,
    tile,
    verdict,
)

METAL = "#9aa3ad"
BODY = "#f59e0b"
EDGE = "#92400e"
DARK = "#20242b"
INK = "#1f2933"


def _chip(
    cx: float,
    top: float,
    w: float = 96,
    h: float = 46,
    marks: tuple[str, ...] = (),
    burnt: bool = False,
) -> tuple[str, Point, Point]:
    """Surface-mount tantalum capacitor seen from above, positive end (the bar) on the left.

    Returns (svg, a point on the positive terminal, a point on the negative terminal).
    """
    x = cx - w / 2
    o = f'  <rect x="{x - 9}" y="{top + 8}" width="{w + 18}" height="{h - 16}" fill="{METAL}"/>\n'
    o += f'  <rect x="{x}" y="{top}" width="{w}" height="{h}" rx="4" fill="{BODY}" stroke="{EDGE}" stroke-width="1.5"/>\n'
    o += f'  <rect x="{x + 7}" y="{top + 4}" width="9" height="{h - 8}" fill="{EDGE}"/>\n'
    for i, mark in enumerate(marks):
        y = top + h / 2 + 5 + 17 * (i - (len(marks) - 1) / 2)
        o += f'  <text x="{cx + 9}" y="{y:.1f}" font-size="14" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="{INK}">{mark}</text>\n'
    if burnt:
        o += f'  <path d="M{cx - 6} {top + 6} q16 -10 24 4 q12 10 0 22 q-10 12 -26 4 q-12 -12 2 -30 Z" fill="{DARK}" opacity="0.85"/>\n'
    return o, (x - 5, top + h / 2), (x + w + 5, top + h / 2)


def _notes(x: float, y: float, lines: tuple[str, ...], cls: str = "mut") -> str:
    return "".join(text(x, y + 17 * i, line, cls, 12) for i, line in enumerate(lines))


# ---------------------------------------------------------------- figure 1
def _drop(cx: float, top: float) -> str:
    """Dipped through-hole tantalum capacitor: a bead on two leads, a plus sign above the positive one."""
    o = f'  <path d="M{cx - 14} {top + 62} V{top + 114} M{cx + 14} {top + 62} V{top + 114}" stroke="{METAL}" stroke-width="3" stroke-linecap="round"/>\n'
    o += f'  <path d="M{cx} {top} C{cx + 46} {top} {cx + 44} {top + 60} {cx + 20} {top + 72} H{cx - 20} C{cx - 44} {top + 60} {cx - 46} {top} {cx} {top} Z" fill="#ea580c" stroke="#9a3412" stroke-width="1.5"/>\n'
    for i, mark in enumerate(("47μ", "16V")):
        o += f'  <text x="{cx + 4}" y="{top + 28 + 17 * i}" font-size="13" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#ffffff">{mark}</text>\n'
    o += f'  <text x="{cx - 20}" y="{top + 64}" font-size="15" font-weight="700" text-anchor="middle" fill="#ffffff">+</text>\n'
    return o


def _alu_top(cx: float, cy: float) -> str:
    """Surface-mount aluminium electrolytic seen from above: the black sector is the negative side."""
    o = f'  <rect x="{cx - 46}" y="{cy - 46}" width="92" height="92" rx="4" fill="{DARK}" stroke="#7d8794"/>\n'
    o += f'  <rect x="{cx - 57}" y="{cy - 8}" width="11" height="16" fill="{METAL}"/><rect x="{cx + 46}" y="{cy - 8}" width="11" height="16" fill="{METAL}"/>\n'
    o += f'  <circle cx="{cx}" cy="{cy}" r="40" fill="#c9d0d9" stroke="#7d8794" stroke-width="1.5"/>\n'
    o += f'  <path d="M{cx - 23} {cy - 32.7:.1f} A40 40 0 0 0 {cx - 23} {cy + 32.7:.1f} Z" fill="{DARK}"/>\n'
    for i, mark in enumerate(("47", "16V")):
        o += f'  <text x="{cx + 10}" y="{cy - 3 + 18 * i}" font-size="13" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="{INK}">{mark}</text>\n'
    return o


def fig_polarity() -> str:
    b = heading(
        "Tantale : le repère désigne le plus",
        "C'est l'inverse d'un électrolytique aluminium : confondre les deux, c'est monter le composant à l'envers",
    )
    b += text(24, 100, "Tantale CMS, vu de dessus", size=15, weight=700)
    chip, _, _ = _chip(120, 132, 120, 58, ("476", "16V"))
    b += chip
    b += text(42, 168, "+", "no", 18, "middle", 700)
    b += text(198, 168, "−", "fg", 18, "middle", 700)
    b += text(120, 216, "barre : côté positif", "no", 12, "middle", 700)

    b += text(290, 100, "Tantale goutte, traversant", size=15, weight=700)
    b += _drop(370, 118)
    b += text(356, 252, "+", "no", 18, "middle", 700)
    b += text(384, 252, "−", "fg", 18, "middle", 700)
    b += _notes(410, 196, ("signe + (ou barre) :", "côté positif"), "no")

    b += '  <path class="grid" d="M520 92 V280"/>\n'
    b += text(540, 100, "Aluminium CMS : l'inverse", size=15, weight=700)
    b += _alu_top(636, 172)
    b += text(564, 178, "−", "fg", 18, "middle", 700)
    b += text(708, 178, "+", "no", 18, "middle", 700)
    b += text(636, 244, "secteur noir : côté négatif", "mut", 12, "middle")

    b += '  <path class="grid" d="M24 296 H736"/>\n'
    b += text(24, 326, "Lire la valeur", size=15, weight=700)
    for i, (code, head, sub) in enumerate(
        (
            ("476", "47 suivi de 6 zéros, en pF", "47 000 000 pF = 47 µF"),
            ("47μ", "47 µF", "4μ7 = 4,7 µF ; μ47 = 0,47 µF"),
            ("16V", "tension maximale de service", "à utiliser bien en dessous"),
        )
    ):
        b += tile(24 + 240 * i, 342, code, head, sub)
    b += text(
        24,
        446,
        "Monté à l'envers ou en surtension, un tantale se met en court-circuit, chauffe et peut s'enflammer.",
        "warn",
        12,
        weight=700,
    )
    return svg(
        760,
        466,
        "Polarité et marquage d'un condensateur tantale",
        "À gauche, un condensateur tantale CMS vu de dessus, marqué 476 et 16 V : une barre à une extrémité repère le côté positif. "
        "Au centre, un condensateur tantale goutte traversant, marqué 47 µ et 16 V : un signe plus, ou une barre, repère la patte positive. "
        "À droite, pour comparer, un condensateur électrolytique aluminium CMS vu de dessus : son secteur noir repère au contraire le côté négatif. "
        "En bas, la lecture de la valeur : 476 vaut 47 suivi de 6 zéros en picofarads, soit 47 µF ; 47 µ vaut 47 µF, 4 µ 7 vaut 4,7 µF et µ 47 vaut 0,47 µF ; 16 V est la tension maximale de service, à utiliser bien en dessous. "
        "Monté à l'envers ou en surtension, un tantale se met en court-circuit, chauffe et peut s'enflammer.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def fig_short() -> str:
    b = heading(
        "Au bipeur : un tantale en panne est le plus souvent en court-circuit",
        "Carte débranchée, condensateur déchargé et dessoudé, pointe rouge sur le + (côté de la barre)",
    )
    b += '  <path class="grid" d="M380 84 V504"/>\n'
    for x0, lcd, flag, burnt, title, notes, cls, head, sub in (
        (
            0,
            "OL",
            "",
            False,
            "Sain : le bipeur se tait",
            ("Bip bref possible :", "le condensateur", "se charge."),
            "ok",
            "✓ pas de bip continu",
            "pas de court-circuit ; reste à contrôler la fuite",
        ),
        (
            380,
            "0.4",
            "•)))",
            True,
            "Claqué : bip continu",
            ("0,4 Ω dans les deux", "sens : court-circuit", "franc."),
            "no",
            "✗ 0,4 Ω, bip continu : à remplacer",
            "puis chercher la surtension ou l'inversion en cause",
        ),
    ):
        o, v, com = half_meter(x0, "BEEP", lcd, "Ω", title, notes, flag)
        chip, plus, minus = _chip(x0 + 290, 236, marks=("476", "16V"), burnt=burnt)
        b += o + chip + hookup(v, com, plus, minus)
        b += verdict(x0 + 190, 478, head, sub, cls)
    b += text(
        380,
        528,
        "En circuit, le bip continu désigne tout le rail : le tantale est le premier suspect, à confirmer une patte levée.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        546,
        "Contrôle d'un condensateur tantale au bipeur",
        "Deux multimètres, sélecteur sur le bipeur, mesurent un condensateur tantale CMS 47 µF 16 V dessoudé, pointe rouge sur le côté positif repéré par la barre, pointe noire sur le côté négatif. "
        "À gauche, condensateur sain : OL, le bipeur se tait après un bip bref possible pendant que le condensateur se charge ; pas de court-circuit, il reste à contrôler la fuite. "
        "À droite, condensateur claqué, boîtier noirci : 0,4 Ω et bip continu, court-circuit franc ; à remplacer, puis chercher la surtension ou l'inversion en cause. "
        "En circuit, le bip continu désigne tout le rail : le tantale est le premier suspect, à confirmer une patte levée.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def fig_derating() -> str:
    b = heading(
        "La tension marquée n'est pas la tension d'emploi",
        "Exemple : tantale marqué 16 V, à électrolyte solide au dioxyde de manganèse",
    )
    x0, y0, w, h = 60, 150, 600, 44

    def at(volts: float) -> float:
        return x0 + w * volts / 20

    b += text(x0, 132, "Tension appliquée dans le bon sens", size=14, weight=700)
    b += f'  <rect x="{at(0)}" y="{y0}" width="{at(8) - at(0)}" height="{h}" fill="#16a34a" opacity="0.8"/>\n'
    b += f'  <rect x="{at(8)}" y="{y0}" width="{at(16) - at(8)}" height="{h}" fill="#f59e0b" opacity="0.8"/>\n'
    b += f'  <rect x="{at(16)}" y="{y0}" width="{at(20) - at(16)}" height="{h}" fill="#dc2626" opacity="0.8"/>\n'
    for volts in (0, 4, 8, 12, 16, 20):
        b += f'  <path class="wire" d="M{at(volts)} {y0 + h} v6"/>\n'
        b += text(at(volts), y0 + h + 22, f"{volts} V", "mut", 12, "middle")
    for volts, head in (
        (4, "emploi normal"),
        (12, "marge de sécurité"),
        (18, "interdit"),
    ):
        b += f'  <text x="{at(volts)}" y="{y0 + 27}" font-size="13" font-weight="700" text-anchor="middle" fill="#ffffff">{head}</text>\n'
    for volts, cls, head, sub in (
        (5, "ok", "✓ rail 5 V", "moins de la moitié de 16 V"),
        (12, "no", "✗ rail 12 V", "trop près de 16 V : risque de claquage"),
    ):
        b += f'  <path class="wire" d="M{at(volts)} {y0 + h + 30} V{y0 + h + 52}"/>\n'
        b += text(at(volts), y0 + h + 70, head, cls, 13, "middle", 700)
        b += text(at(volts), y0 + h + 87, sub, "mut", 12, "middle")
    b += _notes(
        x0,
        318,
        (
            "Règle des fabricants : ne pas dépasser 50 % de la tension marquée (8 V pour un 16 V).",
            "Tantale à électrolyte polymère : 80 % de la tension marquée.",
        ),
        "fg",
    )
    b += '  <path class="grid" d="M24 366 H736"/>\n'
    b += text(x0, 394, "Tension appliquée à l'envers", size=14, weight=700)
    b += f'  <rect x="{at(0)}" y="408" width="{at(1) - at(0)}" height="24" fill="#f59e0b" opacity="0.8"/>\n'
    b += f'  <rect x="{at(1)}" y="408" width="{at(20) - at(1)}" height="24" fill="#dc2626" opacity="0.8"/>\n'
    b += f'  <text x="{at(10.5)}" y="425" font-size="13" font-weight="700" text-anchor="middle" fill="#ffffff">interdit</text>\n'
    b += _notes(
        x0,
        456,
        (
            "À l'envers, la limite est de 10 % de la tension marquée, sans dépasser 1 V, pour de brefs instants seulement (à 25 °C).",
            "Monté à l'envers sur un rail de 3,3 V ou plus, un tantale dépasse largement cette limite.",
        ),
    )
    return svg(
        760,
        496,
        "Tension d'emploi d'un condensateur tantale par rapport à sa tension marquée",
        "Échelle de tension de 0 à 20 V pour un condensateur tantale marqué 16 V, à électrolyte solide au dioxyde de manganèse. "
        "De 0 à 8 V, zone verte d'emploi normal ; de 8 à 16 V, zone orange de marge de sécurité ; au-delà de 16 V, zone rouge interdite. "
        "Un rail de 5 V convient : moins de la moitié de 16 V. Un rail de 12 V est trop près de 16 V : risque de claquage. "
        "Règle des fabricants : ne pas dépasser 50 % de la tension marquée, soit 8 V pour un 16 V ; pour un tantale à électrolyte polymère, 80 %. "
        "Seconde échelle, tension appliquée à l'envers : la limite est de 10 % de la tension marquée, sans dépasser 1 V, pour de brefs instants seulement, à 25 °C ; tout le reste est interdit. "
        "Monté à l'envers sur un rail de 3,3 V ou plus, un tantale dépasse largement cette limite.",
        b,
    )


FIGURES = {
    "polarite-et-marquage": (fig_polarity, []),
    "court-circuit-au-bipeur": (fig_short, ["BEEP", "BEEP"]),
    "tension-de-service": (fig_derating, []),
}
