"""Figures of guide 22, the aluminium electrolytic capacitor."""

from __future__ import annotations

from elements import (
    MONO,
    Point,
    chart,
    clip,
    curve,
    half_meter,
    heading,
    hookup,
    svg,
    text,
    tile,
    verdict,
)

METAL = "#9aa3ad"
NAVY = "#1e3a8a"
EDGE = "#172554"
STRIPE = "#cbd5e1"
DARK = "#20242b"


def _can(
    cx: float,
    top: float,
    w: float = 74,
    h: float = 100,
    marks: tuple[str, ...] = (),
    bulge: float = 0,
    size: int = 12,
) -> tuple[str, Point, Point]:
    """Radial electrolytic capacitor seen from the side, leads pointing down.

    The light stripe with minus signs and the shorter lead are on the right: the negative side.
    `bulge` raises the top by that many pixels. Returns (svg, a point on the positive lead,
    a point on the negative lead).
    """
    xl, xr, bot = cx - w * 0.22, cx + w * 0.22, top + h
    o = f'  <path d="M{xl:.1f} {bot} V{bot + 44} M{xr:.1f} {bot} V{bot + 30}" stroke="{METAL}" stroke-width="3" stroke-linecap="round"/>\n'
    if bulge:
        o += f'  <path d="M{cx - w / 2 + 2} {top + 3} Q{cx} {top - 2 * bulge} {cx + w / 2 - 2} {top + 3} Z" fill="#94a3b8" stroke="{EDGE}" stroke-width="1.5"/>\n'
    o += f'  <rect x="{cx - w / 2}" y="{top}" width="{w}" height="{h}" rx="5" fill="{NAVY}" stroke="{EDGE}" stroke-width="1.5"/>\n'
    if not bulge:
        o += f'  <rect x="{cx - w / 2}" y="{top}" width="{w}" height="5" rx="2" fill="#94a3b8"/>\n'
    sx, sw = cx + w * 0.2, w * 0.2
    o += f'  <rect x="{sx:.1f}" y="{top + 8}" width="{sw:.1f}" height="{h - 16}" fill="{STRIPE}"/>\n'
    for k in (0.25, 0.5, 0.75):
        o += f'  <rect x="{sx + sw * 0.2:.1f}" y="{top + h * k - 1.5:.1f}" width="{sw * 0.6:.1f}" height="3" fill="{NAVY}"/>\n'
    for i, mark in enumerate(marks):
        y = top + h / 2 + 5 + (size + 5) * (i - (len(marks) - 1) / 2)
        o += f'  <text x="{cx - w * 0.15:.1f}" y="{y:.1f}" font-size="{size}" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#ffffff">{mark}</text>\n'
    return o, (xl, bot + 34), (xr, bot + 22)


def _notes(x: float, y: float, lines: tuple[str, ...], cls: str = "mut") -> str:
    return "".join(text(x, y + 17 * i, line, cls, 12) for i, line in enumerate(lines))


# ---------------------------------------------------------------- figure 1
def _smd_top() -> str:
    """Surface-mount can seen from above: the black sector marks the negative side."""
    o = f'  <rect x="430" y="125" width="120" height="120" rx="4" fill="{DARK}" stroke="#7d8794"/>\n'
    o += f'  <rect x="416" y="175" width="14" height="20" fill="{METAL}"/><rect x="550" y="175" width="14" height="20" fill="{METAL}"/>\n'
    o += '  <circle cx="490" cy="185" r="52" fill="#c9d0d9" stroke="#7d8794" stroke-width="1.5"/>\n'
    o += f'  <path d="M460 142.5 A52 52 0 0 0 460 227.5 Z" fill="{DARK}"/>\n'
    for i, mark in enumerate(("470", "25V")):
        o += f'  <text x="503" y="{181 + 20 * i}" font-size="15" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#1f2933">{mark}</text>\n'
    o += text(404, 191, "−", "fg", 18, "middle", 700)
    o += text(578, 191, "+", "no", 18, "middle", 700)
    o += text(490, 270, "secteur noir : côté négatif", "mut", 12, "middle")
    return o


def fig_marking() -> str:
    b = heading(
        "Lire un condensateur électrolytique : la valeur et le sens",
        "Composant polarisé : la patte négative est repérée sur le boîtier, et le sens de montage sur la carte",
    )
    b += text(24, 100, "Boîtier radial, traversant", size=15, weight=700)
    can, _, _ = _can(120, 120, 100, 140, ("470µF", "25V", "105°C"), size=14)
    b += can
    b += text(98, 322, "+", "no", 18, "middle", 700)
    b += text(142, 310, "−", "fg", 18, "middle", 700)
    b += '  <path class="grid" d="M172 170 H196 M150 286 H196"/>\n'
    b += _notes(202, 166, ("bande claire à signes − :", "côté de la patte négative"))
    b += _notes(202, 282, ("patte la plus courte :", "négative (composant neuf)"))
    b += text(420, 100, "Boîtier CMS, vu de dessus", size=15, weight=700)
    b += _smd_top()
    b += '  <path class="grid" d="M24 340 H736"/>\n'
    b += text(24, 370, "Trois indications à relever", size=15, weight=700)
    for i, (code, head, sub) in enumerate(
        (
            ("470µF", "capacité", "en microfarads"),
            ("25V", "tension maximale de service", "à ne jamais dépasser"),
            ("105°C", "température maximale", "85 °C ou 105 °C le plus souvent"),
        )
    ):
        b += tile(24 + 240 * i, 386, code, head, sub)
    b += text(
        24,
        490,
        "Monté à l'envers, il chauffe, gonfle et peut s'ouvrir brutalement : vérifier deux fois le sens avant de souder.",
        "warn",
        12,
        weight=700,
    )
    return svg(
        760,
        510,
        "Lire le marquage et la polarité d'un condensateur électrolytique",
        "À gauche, un condensateur électrolytique radial vu de côté, marqué 470 µF, 25 V et 105 °C : une bande claire portant des signes moins court le long du boîtier du côté de la patte négative, qui est aussi la plus courte sur un composant neuf ; l'autre patte est le plus. "
        "À droite, un condensateur électrolytique CMS vu de dessus, marqué 470 et 25 V : un secteur noir sur le dessus du boîtier repère le côté négatif. "
        "En bas, les trois indications à relever : la capacité en microfarads, la tension maximale de service à ne jamais dépasser, et la température maximale, 85 °C ou 105 °C le plus souvent. "
        "Monté à l'envers, le condensateur chauffe, gonfle et peut s'ouvrir brutalement : vérifier deux fois le sens avant de souder.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def fig_visual_clues() -> str:
    b = heading(
        "Ce que l'œil peut voir : trois signes qui condamnent",
        "Carte hors tension et déchargée. Comparer chaque condensateur à ses voisins de même modèle",
    )
    cases = (
        (110, 0, "ok", "Aspect normal", "dessus plat, pied propre"),
        (290, 9, "no", "Dessus bombé", "la pression interne a monté"),
        (470, 6, "no", "Dépôt brun ou roux", "l'électrolyte est sorti"),
        (650, 0, "no", "Fond repoussé", "le bouchon sort du boîtier"),
    )
    for cx, bulge, cls, head, sub in cases:
        lifted = head == "Fond repoussé"
        can, _, _ = _can(cx, 138 if lifted else 150, 80, 110, ("470µF", "25V"), bulge)
        b += can
        if lifted:
            b += f'  <rect x="{cx - 34}" y="248" width="68" height="13" rx="3" fill="{DARK}" stroke="#7d8794"/>\n'
        if head.startswith("Dépôt"):
            b += f'  <path d="M{cx - 20} 147 q8 -12 20 -8 q14 -6 20 8 q-2 6 -8 4 l-3 10 l-4 -9 q-14 5 -25 -5 Z" fill="#92400e" stroke="#78350f"/>\n'
        b += text(cx, 326, head, cls, 14, "middle", 700)
        b += text(cx, 344, sub, "mut", 12, "middle")
    b += '  <rect class="panel" x="30" y="272" width="700" height="12" rx="3"/>\n'
    b += '  <rect class="panel" x="30" y="368" width="700" height="62" rx="8"/>\n'
    b += _notes(
        46,
        392,
        (
            "Un aspect normal n'innocente pas : un condensateur dont l'ESR a monté ne montre souvent rien.",
            "Une colle brune ou noire au pied d'un condensateur sert à le tenir : ce n'est pas de l'électrolyte.",
        ),
    )
    return svg(
        760,
        446,
        "Indices visuels d'un condensateur électrolytique défaillant",
        "Quatre condensateurs électrolytiques radiaux soudés sur une carte, vus de côté. "
        "Le premier a un aspect normal : dessus plat, pied propre. "
        "Le deuxième a le dessus bombé : la pression interne a monté. "
        "Le troisième porte un dépôt brun ou roux sur le dessus : l'électrolyte est sorti. "
        "Le quatrième a le fond repoussé : le bouchon de caoutchouc sort du boîtier, qui s'est soulevé de la carte. "
        "Les trois derniers sont à remplacer. Un aspect normal n'innocente pas : un condensateur dont l'ESR a monté ne montre souvent rien. "
        "Une colle brune ou noire au pied d'un condensateur sert à le tenir : ce n'est pas de l'électrolyte.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def fig_ohmmeter_charge() -> str:
    b = heading(
        "Hors circuit, à l'ohmmètre : le condensateur doit se charger",
        "Condensateur déchargé, une patte dessoudée, pointe rouge sur le +, pointe noire sur le − (côté de la bande)",
    )
    b += '  <path class="grid" d="M380 84 V504"/>\n'
    for x0, lcd, title, notes, cls, head, sub in (
        (
            0,
            "86.3",
            "Sain : la lecture monte",
            ("La lecture part de bas", "et grimpe jusqu'à OL."),
            "ok",
            "✓ Monte, puis OL : il se charge",
            "il stocke de l'énergie ; son ESR reste inconnue",
        ),
        (
            380,
            "OL",
            "Desséché : aucune montée",
            ("OL tout de suite, sur", "une grosse valeur."),
            "no",
            "✗ OL d'emblée : plus de capacité",
            "électrolyte évaporé ou connexion interne coupée",
        ),
    ):
        o, v, com = half_meter(x0, "200k", lcd, "kΩ", title, notes)
        can, plus, minus = _can(x0 + 290, 196, marks=("470µF", "25V"))
        b += o + can + hookup(v, com, (plus[0], plus[1] - 6), (minus[0], minus[1] - 2))
        b += verdict(x0 + 190, 478, head, sub, cls)
    b += text(
        380,
        528,
        "Une valeur basse qui ne monte pas : fuite ou court-circuit. Ce test ne mesure ni la capacité ni l'ESR.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        546,
        "Charge d'un condensateur électrolytique à l'ohmmètre",
        "Deux multimètres, sélecteur sur l'ohmmètre calibre 200 kΩ, mesurent un condensateur électrolytique 470 µF 25 V hors circuit et déchargé, pointe rouge sur la patte positive, pointe noire sur la patte négative, du côté de la bande. "
        "À gauche, condensateur sain : la lecture part de bas, ici 86,3 kΩ, et grimpe jusqu'à OL ; le condensateur se charge, il stocke de l'énergie, mais son ESR reste inconnue. "
        "À droite, condensateur desséché : OL tout de suite, sans aucune montée ; il n'a plus de capacité, électrolyte évaporé ou connexion interne coupée. "
        "Une valeur basse qui ne monte pas signale une fuite ou un court-circuit. Ce test ne mesure ni la capacité ni l'ESR.",
        b,
    )


# ---------------------------------------------------------------- figure 4
def _sawtooth(top: float, low: float) -> list[Point]:
    """Rail voltage over 40 ms behind a full-wave rectifier: a fast refill every 10 ms, then a slow sag."""
    pts: list[Point] = [(0, low + (top - low) * 0.4)]
    for k in range(4):
        t0 = 10 * k
        pts += [(t0 + 2, top), (t0 + 10, low)]
    return pts


def fig_ripple() -> str:
    b = heading(
        "Sous tension : un condensateur de filtrage usé laisse plonger le rail",
        "Rail 12 V derrière un redresseur, adaptateur alternatif 50 Hz : le condensateur est rechargé 100 fois par seconde",
    )
    axes, at = chart(
        70,
        120,
        410,
        240,
        40,
        14,
        [(t, str(t)) for t in (0, 10, 20, 30, 40)],
        [(v, str(v)) for v in (0, 4, 8, 12)],
        "temps (ms)",
        "tension du rail (V)",
    )
    b += axes
    b += curve([at(t, v) for t, v in _sawtooth(12, 8.5)], "fr")
    b += curve([at(t, v) for t, v in _sawtooth(12, 11.6)], "fb")
    for y, cls, head, sub in (
        (140, "fb", "condensateur sain", "ondulation faible : 0,4 V"),
        (188, "fr", "condensateur usé", "creux de 3,5 V à chaque période"),
    ):
        b += curve([(516, y), (546, y)], cls, 4)
        b += text(556, y + 4, head, size=13, weight=700)
        b += text(556, y + 21, sub, "mut", 12)
    b += _notes(
        516,
        250,
        (
            "Entre deux recharges, le condensateur",
            "alimente seul la carte. Usé, il se vide",
            "trop vite : régulateur qui décroche,",
            "ronflement, redémarrages.",
        ),
        "fg",
    )
    b += _notes(
        516,
        336,
        (
            "Le voltmètre en continu n'affiche que",
            "la moyenne : il ne voit pas les creux.",
        ),
    )
    return svg(
        760,
        420,
        "Ondulation d'un rail filtré par un condensateur électrolytique sain ou usé",
        "Graphique de la tension d'un rail 12 V en fonction du temps, sur 40 millisecondes, derrière un redresseur alimenté par un adaptateur alternatif 50 Hz : le condensateur de filtrage est rechargé 100 fois par seconde, toutes les 10 millisecondes. "
        "Avec un condensateur sain, la tension dessine de petites dents de scie entre 12 V et 11,6 V : ondulation faible, 0,4 V. "
        "Avec un condensateur usé, elle plonge de 12 V à 8,5 V entre deux recharges : des creux de 3,5 V à chaque période. "
        "Entre deux recharges, le condensateur alimente seul la carte ; usé, il se vide trop vite, ce qui donne un régulateur qui décroche, un ronflement, des redémarrages. "
        "Le voltmètre en continu n'affiche que la moyenne : il ne voit pas les creux.",
        b,
    )


# ---------------------------------------------------------------- figure 5
def _esr_meter(x0: float, reading: str) -> str:
    """Dedicated ESR meter with its two clips on the capacitor leads, capacitor left on its board."""
    o = f'  <rect x="{x0 + 24}" y="120" width="150" height="150" rx="10" fill="#eab308" stroke="#a16207" stroke-width="1.5"/>\n'
    o += f'  <rect x="{x0 + 32}" y="128" width="134" height="134" rx="7" fill="{DARK}"/>\n'
    o += f'  <text x="{x0 + 99}" y="150" font-size="12" font-weight="700" text-anchor="middle" fill="#ffffff">ESR-mètre</text>\n'
    o += f'  <rect x="{x0 + 42}" y="160" width="114" height="46" rx="4" fill="#c8d4b0" stroke="#7d8794"/>\n'
    o += f'  <text x="{x0 + 128}" y="194" font-size="26" font-weight="700" text-anchor="end" font-family="{MONO}" fill="#1f2933">{reading}</text>\n'
    o += f'  <text x="{x0 + 134}" y="194" font-size="14" font-weight="700" font-family="{MONO}" fill="#1f2933">Ω</text>\n'
    o += f'  <circle cx="{x0 + 70}" cy="238" r="7" fill="#dc2626" stroke="#ffffff"/><circle cx="{x0 + 128}" cy="238" r="7" fill="#0b0d10" stroke="#ffffff"/>\n'
    can, plus, minus = _can(x0 + 290, 150, marks=("470µF", "25V"))
    o += can
    o += f'  <rect class="panel" x="{x0 + 236}" y="282" width="108" height="12" rx="3"/>\n'
    px, py = plus[0], 266.0
    mx, my = minus[0], 266.0
    o += f'  <path d="M{x0 + 70} 238 C{x0 + 70} 330 {x0 + 200} 320 {x0 + 215} 280 S{px - 30:.1f} {py} {px - 6:.1f} {py}" fill="none" stroke="#dc2626" stroke-width="3.5" stroke-linecap="round"/>\n'
    o += f'  <path d="M{x0 + 128} 238 C{x0 + 128} 352 {x0 + 366} 352 {x0 + 366} 300 S{mx + 30:.1f} {my} {mx + 6:.1f} {my}" fill="none" stroke="{DARK}" stroke-width="3.5" stroke-linecap="round"/>\n'
    return o + clip(px, py, True) + clip(mx, my, False)


def fig_esr() -> str:
    b = heading(
        "L'ESR-mètre : la mesure qui démasque un électrolytique usé",
        "Carte hors tension, condensateur déchargé et laissé en place : mesure de sa résistance série",
    )
    b += '  <path class="grid" d="M380 84 V392"/>\n'
    for x0, reading, title, cls, head, sub in (
        (
            0,
            "0.09",
            "Sain : ESR très basse",
            "ok",
            "✓ 0,09 Ω : une fraction d'ohm",
            "comme un condensateur neuf de même valeur",
        ),
        (
            380,
            "4.7",
            "Usé : ESR montée",
            "no",
            "✗ 4,7 Ω : à remplacer",
            "sa capacité peut encore être bonne",
        ),
    ):
        b += text(x0 + 20, 100, title, size=15, weight=700)
        b += _esr_meter(x0, reading)
        b += verdict(x0 + 190, 366, head, sub, cls)
    b += _notes(
        24,
        418,
        (
            "Référence : un condensateur neuf identique, ou la valeur de sa fiche technique.",
            "Un condensateur en court-circuit lit lui aussi une ESR très basse : le bipeur le dit.",
            "Une faible résistance en parallèle sur la carte fausse la lecture vers le bas.",
        ),
    )
    return svg(
        760,
        470,
        "Mesure de l'ESR d'un condensateur électrolytique en circuit",
        "Deux ESR-mètres, pinces sur les deux pattes d'un condensateur électrolytique 470 µF 25 V laissé en place sur sa carte, hors tension et déchargé ; l'appareil mesure la résistance série du condensateur en alternatif. "
        "À gauche, condensateur sain : 0,09 Ω, une fraction d'ohm, comme un condensateur neuf de même valeur. "
        "À droite, condensateur usé : 4,7 Ω, à remplacer, alors que sa capacité peut encore être bonne. "
        "La référence est un condensateur neuf identique, ou la valeur de sa fiche technique. "
        "Un condensateur en court-circuit lit lui aussi une ESR très basse : le bipeur le dit. Une faible résistance en parallèle sur la carte fausse la lecture vers le bas.",
        b,
    )


FIGURES = {
    "lire-le-marquage-et-la-polarite": (fig_marking, []),
    "indices-visuels": (fig_visual_clues, []),
    "charge-a-l-ohmmetre": (fig_ohmmeter_charge, ["200k", "200k"]),
    "ondulation-sur-le-rail": (fig_ripple, []),
    "mesure-esr": (fig_esr, []),
}
