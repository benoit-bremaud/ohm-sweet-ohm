"""Figures of guide 20, the ceramic capacitor (MLCC)."""

from __future__ import annotations

from elements import (
    MONO,
    chart,
    curve,
    half_meter,
    heading,
    hookup,
    mlcc,
    svg,
    text,
    tile,
    verdict,
)

BOARD = "#1f7a4d"
RED = "#dc2626"


# ---------------------------------------------------------------- figure 1
def fig_marking() -> str:
    b = heading(
        "Lire un condensateur céramique : boîtier CMS nu, disque marqué",
        "Un MLCC CMS ne porte aucun marquage ; un céramique traversant porte un code à trois chiffres",
    )
    b += text(
        24,
        100,
        "CMS (MLCC) : rien d'écrit, seule la taille se lit",
        size=15,
        weight=700,
    )
    for i, (name, size, w, h) in enumerate(
        (
            ("0402", "1,0 × 0,5 mm", 20, 10),
            ("0603", "1,6 × 0,8 mm", 32, 16),
            ("0805", "2,0 × 1,25 mm", 40, 25),
            ("1206", "3,2 × 1,6 mm", 64, 32),
        )
    ):
        cx = 110 + 180 * i
        m, _, _ = mlcc(cx, 146, w, h)
        b += m
        b += text(cx, 192, name, "blue", 13, "middle", 700)
        b += text(cx, 209, size, "mut", 12, "middle")
    b += text(
        24,
        238,
        "Corps beige ou brun, deux extrémités métallisées. La valeur se lit sur le schéma ou se mesure, composant dessoudé.",
        "mut",
        12,
    )
    b += '  <path class="grid" d="M24 258 H736"/>\n'
    b += text(
        24,
        288,
        "Traversant (disque ou goutte) : code à trois chiffres, en picofarads",
        size=15,
        weight=700,
    )
    b += '  <path d="M96 380 V436 M124 380 V436" stroke="#9aa3ad" stroke-width="3" stroke-linecap="round"/>\n'
    b += '  <circle cx="110" cy="352" r="40" fill="#c98a3c" stroke="#8a5a1c" stroke-width="1.5"/>\n'
    b += f'  <text x="110" y="358" font-size="17" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#1f2933">104K</text>\n'
    for i, (code, head, sub) in enumerate(
        (
            ("10", "deux chiffres significatifs", "ici 10"),
            ("4", "nombre de zéros", "ici 0000, en picofarads"),
            ("K", "tolérance ±10 %", "J : ±5 %, M : ±20 %"),
        )
    ):
        b += tile(200 + 184 * i, 312, code, head, sub)
    b += text(
        200,
        420,
        "104 : 10 suivi de 4 zéros = 100 000 pF = 100 nF = 0,1 µF",
        size=14,
        weight=700,
    )
    b += text(
        200,
        440,
        "Autres codes courants : 103 = 10 nF, 223 = 22 nF, 105 = 1 µF ; « 47 » seul = 47 pF.",
        "mut",
        12,
    )
    return svg(
        760,
        460,
        "Lire le marquage d'un condensateur céramique",
        "En haut, quatre condensateurs céramique CMS (MLCC) de tailles croissantes, dessinés à la même échelle : 0402 (1,0 × 0,5 mm), 0603 (1,6 × 0,8 mm), 0805 (2,0 × 1,25 mm) et 1206 (3,2 × 1,6 mm). "
        "Leur corps beige ou brun, terminé par deux extrémités métallisées, ne porte aucun marquage : la valeur se lit sur le schéma ou se mesure, composant dessoudé. "
        "En bas, un condensateur céramique traversant en forme de disque porte le code 104K. Les deux premiers chiffres, 10, sont les chiffres significatifs ; le troisième, 4, est le nombre de zéros, en picofarads ; la lettre K donne la tolérance, ±10 % (J : ±5 %, M : ±20 %). "
        "104 se lit donc 10 suivi de 4 zéros, soit 100 000 pF, 100 nF ou 0,1 µF. Autres codes courants : 103 pour 10 nF, 223 pour 22 nF, 105 pour 1 µF ; le nombre 47 seul vaut 47 pF.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def _arrow(x: float, y1: float, y2: float) -> str:
    """Vertical force arrow from y1 to y2, head at y2."""
    d = 7 if y2 > y1 else -7
    return f'  <path class="blk" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round" d="M{x} {y1} V{y2} M{x - 6} {y2 - d} L{x} {y2} L{x + 6} {y2 - d}"/>\n'


def _section() -> str:
    """Cross-section of an MLCC soldered on a board bent upwards under it."""
    o = text(
        20,
        100,
        "En coupe : la carte fléchit, la céramique casse",
        size=15,
        weight=700,
    )
    # bent board: the component sits on the stretched side
    o += f'  <path d="M30 268 Q190 228 350 268 V284 Q190 244 30 284 Z" fill="{BOARD}" stroke="#14532d"/>\n'
    for sx in (1, -1):  # solder fillets, left then right
        x = 190 - 55 * sx
        o += f'  <path d="M{x - 17 * sx} 252 L{x} 214 V240 H{x + 22 * sx} V248 Z" fill="#aeb6c0" stroke="#7d8794"/>\n'
    m, _, _ = mlcc(190, 225, 110, 30)
    o += m
    # inner electrodes, alternately tied to the left and to the right termination
    for i, y in enumerate((216, 222, 228, 234)):
        x1, x2 = (157, 212) if i % 2 == 0 else (168, 223)
        o += f'  <path d="M{x1} {y} H{x2}" stroke="#8a6d45" stroke-width="1.4"/>\n'
    o += f'  <path d="M158 240 L153 233 L156 229 L149 222 L151 217 L144 210" stroke="{RED}" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>\n'
    o += '  <path class="blk" stroke-width="1.2" fill="none" d="M150 206 L128 176"/>\n'
    o += text(24, 150, "fissure oblique, partie du bord", "no", 12, weight=700)
    o += text(24, 166, "de la terminaison, côté carte", "no", 12, weight=700)
    o += text(232, 188, "électrodes internes", "mut", 12)
    o += '  <path class="blk" stroke-width="1.2" fill="none" d="M262 193 L214 220"/>\n'
    o += _arrow(46, 292, 318) + _arrow(334, 292, 318) + _arrow(190, 314, 288)
    o += text(190, 336, "flexion de la carte", "mut", 12, "middle")
    for i, line in enumerate(
        (
            "La céramique ne plie pas : la soudure tire sur ses",
            "extrémités et le corps se fend sous une terminaison.",
            "La fissure relie des électrodes de polarités opposées :",
            "fuite, puis court-circuit, parfois des semaines après.",
        )
    ):
        o += text(20, 368 + 17 * i, line, "mut", 12)
    return o


def _board_map() -> str:
    """Top view of a board with the places where an MLCC cracks first."""
    o = text(400, 100, "Sur la carte : où chercher d'abord", size=15, weight=700)
    o += f'  <rect x="410" y="120" width="320" height="200" rx="6" fill="{BOARD}" stroke="#14532d"/>\n'
    # mounting screw, connector, break-off edge
    o += '  <circle cx="440" cy="150" r="13" fill="#c9d0d9" stroke="#7d8794" stroke-width="2"/><path d="M432 150 H448 M440 142 V158" stroke="#7d8794" stroke-width="2"/>\n'
    o += '  <rect x="500" y="296" width="110" height="34" rx="3" fill="#20242b" stroke="#7d8794"/>\n'
    o += '  <path d="M730 150 V290" stroke="#e5e7eb" stroke-width="3" stroke-dasharray="3 9"/>\n'
    for x, y, label in (
        (430, 180, "vis"),
        (524, 318, "connecteur"),
        (716, 142, "bord détouré"),
    ):
        anchor = ' text-anchor="end"' if x > 700 else ""
        o += f'  <text x="{x}" y="{y}" font-size="11"{anchor} fill="#ffffff">{label}</text>\n'
    for cx, cy, vertical, risky in (
        (474, 178, False, True),
        (540, 262, False, True),
        (704, 220, True, True),
        (580, 196, False, False),
    ):
        m, _, _ = mlcc(cx, cy, 34, 16, vertical)
        o += m
        ring = RED if risky else "#4ade80"
        o += f'  <circle cx="{cx}" cy="{cy}" r="25" fill="none" stroke="{ring}" stroke-width="2.5"/>\n'
    o += f'  <circle cx="420" cy="350" r="8" fill="none" stroke="{RED}" stroke-width="2.5"/>\n'
    o += text(436, 354, "à contrôler en premier : près d'une vis,", size=12)
    o += text(436, 370, "d'un connecteur, d'un bord détouré", size=12)
    o += '  <circle cx="420" cy="394" r="8" fill="none" stroke="#16a34a" stroke-width="2.5"/>\n'
    o += text(436, 398, "au milieu de la carte : peu exposé", size=12)
    o += text(
        400, 426, "Plus le boîtier est long (1206 et au-delà), plus il casse", "mut", 12
    )
    o += text(
        400, 442, "facilement. Carte tombée, tordue ou vissée de travers :", "mut", 12
    )
    o += text(400, 458, "soupçonner les MLCC avant tout le reste.", "mut", 12)
    return o


def fig_flex_crack() -> str:
    b = heading(
        "La panne type du MLCC : la fissure de flexion",
        "Une carte qui plie casse la céramique sous une terminaison ; rien ne se voit de dessus",
    )
    b += '  <path class="grid" d="M380 84 V464"/>\n'
    b += _section() + _board_map()
    return svg(
        760,
        480,
        "Fissure de flexion d'un condensateur céramique CMS",
        "À gauche, vue en coupe : un condensateur céramique CMS est soudé par ses deux extrémités sur une carte qui fléchit. "
        "La céramique ne plie pas : la soudure tire sur ses extrémités et le corps se fend, en oblique, à partir du bord d'une terminaison, côté carte. "
        "La fissure relie des électrodes internes de polarités opposées : une fuite apparaît, puis un court-circuit, parfois des semaines après le choc. "
        "À droite, vue de dessus d'une carte : les condensateurs à contrôler en premier, cerclés de rouge, sont près d'une vis de fixation, d'un connecteur ou d'un bord détouré ; celui du milieu de la carte, cerclé de vert, est peu exposé. "
        "Plus le boîtier est long, 1206 et au-delà, plus il casse facilement. Après une chute, une torsion ou un vissage de travers, soupçonner les MLCC avant tout le reste.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def _rail(x0: float, shorted: bool) -> str:
    """Three MLCCs in parallel between a supply rail and ground; C2 cracked if `shorted`."""
    o = f'  <path class="wire" d="M{x0 + 222} 214 H{x0 + 352} M{x0 + 222} 316 H{x0 + 352} M{x0 + 222} 316 v8 M{x0 + 213} 324 h18 M{x0 + 217} 329 h10"/>\n'
    o += text(x0 + 352, 204, "rail 3,3 V", "mut", 12, "end")
    for i, cx in enumerate((x0 + 248, x0 + 290, x0 + 332)):
        m, top, bottom = mlcc(cx, 265, 52, 24, vertical=True)
        o += f'  <path class="wire" d="M{cx} 214 V{top[1]:.1f} M{cx} {bottom[1]:.1f} V316"/>\n'
        o += m
        bad = shorted and i == 1
        if bad:
            o += f'  <path d="M{cx - 12} 259 L{cx - 4} 266 L{cx - 1} 262 L{cx + 12} 272" stroke="{RED}" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>\n'
        o += text(cx, 340, f"C{i + 1}", "no" if bad else "mut", 12, "middle", 700)
    return o


def fig_rail_short() -> str:
    b = heading(
        "Hors tension : un MLCC en court-circuit met tout le rail à zéro",
        "Sélecteur sur le bipeur, carte débranchée et déchargée, pointe rouge sur le rail, pointe noire à la masse",
    )
    b += '  <path class="grid" d="M380 84 V504"/>\n'
    for x0, lcd, flag, shorted, title, notes, cls, head, sub in (
        (
            0,
            "OL",
            "",
            False,
            "Rail sain : le bipeur se tait",
            ("Bip bref possible :", "les condensateurs", "se chargent."),
            "ok",
            "✓ pas de bip continu",
            "aucun court-circuit franc entre le rail et la masse",
        ),
        (
            380,
            "0.3",
            "•)))",
            True,
            "C2 fissuré : tout le rail sonne",
            ("Bip continu,", "0,3 Ω : rail en", "court-circuit."),
            "no",
            "✗ 0,3 Ω sur C1, sur C2 et sur C3",
            "le bipeur ne dit pas lequel : voir le niveau 3",
        ),
    ):
        o, v, com = half_meter(x0, "BEEP", lcd, "Ω", title, notes, flag)
        b += o + _rail(x0, shorted)
        b += hookup(v, com, (x0 + 230, 214), (x0 + 347, 316))
        b += verdict(x0 + 190, 478, head, sub, cls)
    b += text(
        380,
        528,
        "Des condensateurs en parallèle se mesurent ensemble : un seul en court-circuit et tous lisent la même chose.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        546,
        "Court-circuit d'un condensateur céramique sur un rail d'alimentation, au bipeur",
        "Deux multimètres, sélecteur sur le bipeur, mesurent entre un rail 3,3 V et la masse, carte débranchée et déchargée ; trois condensateurs céramique C1, C2 et C3 sont en parallèle entre ce rail et la masse. "
        "À gauche, rail sain : un bip bref est possible pendant que les condensateurs se chargent, puis l'appareil se tait et affiche OL ; il n'y a aucun court-circuit franc. "
        "À droite, C2 est fissuré : l'appareil sonne en continu et lit 0,3 Ω, la même valeur sur C1, sur C2 et sur C3, puisque les trois sont en parallèle. "
        "Le bipeur ne dit pas lequel est en cause : il faut la méthode du niveau 3, sous tension. "
        "Des condensateurs en parallèle se mesurent ensemble : un seul en court-circuit et tous lisent la même chose.",
        b,
    )


# ---------------------------------------------------------------- figure 4
BIAS = 12  # volts of the worked example
KEPT = {
    "0805": 32.6,
    "1206": 73.0,
}  # % of 4.7 µF left at BIAS (Fortunato, see the guide's sources)


def _remaining(volts: float, case: str) -> float:
    """Typical share of capacitance (in %) a 4.7 µF 16 V X7R keeps under `volts` of DC bias."""
    knee = BIAS / (100 / KEPT[case] - 1) ** 0.5
    return 100 / (1 + (volts / knee) ** 2)


def _marker(p: tuple[float, float], n: int) -> str:
    return (
        f'  <circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="10" fill="#20242b" stroke="#ffffff" stroke-width="1.5"/>\n'
        f'  <text x="{p[0]:.1f}" y="{p[1] + 4:.1f}" font-size="12" font-weight="700" text-anchor="middle" fill="#ffffff">{n}</text>\n'
    )


def fig_dc_bias() -> str:
    b = heading(
        "Classe II : la capacité fond quand la tension continue monte",
        "Allure typique d'un 4,7 µF 16 V ; les valeurs exactes sont dans les courbes du fabricant",
    )
    axes, at = chart(
        84,
        112,
        400,
        250,
        16,
        100,
        [(v, str(v)) for v in (0, 4, 8, 12, 16)],
        [(p, f"{p} %") for p in (0, 25, 50, 75, 100)],
        "tension continue aux bornes (V)",
        "capacité restante",
    )
    b += axes
    volts = [16 * i / 40 for i in range(41)]
    b += curve([at(v, 100) for v in volts], "fb")
    b += curve([at(v, _remaining(v, "1206")) for v in volts], "fa")
    b += curve([at(v, _remaining(v, "0805")) for v in volts], "fr")
    b += _marker(at(0, 100), 1) + _marker(at(BIAS, KEPT["0805"]), 2)
    for i, (cls, head, sub) in enumerate(
        (
            ("fb", "Classe I (C0G, NP0)", "stable ; petites valeurs seulement"),
            ("fa", "Classe II (X7R), boîtier 1206", "73 % à 12 V : 3,4 µF"),
            ("fr", "Classe II (X7R), boîtier 0805", "33 % à 12 V : 1,5 µF"),
        )
    ):
        y = 126 + 44 * i
        b += curve([(516, y), (546, y)], cls, 4)
        b += text(556, y + 4, head, size=13, weight=700)
        b += text(556, y + 21, sub, "mut", 12)
    for n, y, lines in (
        (
            1,
            272,
            ("Au capacimètre : presque aucune", "tension, lecture proche du marquage."),
        ),
        (
            2,
            322,
            (
                "Sur un rail 12 V : il reste un tiers,",
                "un « 4,7 µF » ne vaut plus que 1,5 µF.",
            ),
        ),
    ):
        b += _marker((528, y), n)
        b += text(548, y, lines[0], size=12)
        b += text(548, y + 16, lines[1], size=12)
    b += text(
        380,
        432,
        "Ce n'est pas une panne : c'est le comportement normal de la classe II (X5R, X7R, Y5V).",
        "warn",
        14,
        "middle",
        700,
    )
    b += text(
        380,
        452,
        "Un condensateur de remplacement se choisit donc à boîtier et tension nominale au moins égaux.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        470,
        "Capacité d'un condensateur céramique de classe II en fonction de la tension continue",
        "Graphique de la capacité restante, en pourcentage, en fonction de la tension continue aux bornes, de 0 à 16 V, pour un condensateur céramique 4,7 µF 16 V : allure typique, les valeurs exactes sont dans les courbes du fabricant. "
        "La courbe de la classe I (C0G, NP0) reste à 100 % : elle est stable, mais n'existe qu'en petites valeurs. "
        "La courbe d'un 4,7 µF 16 V de classe II (X7R) en boîtier 1206 descend à 73 % à 12 V, soit 3,4 µF. "
        "La courbe de la même valeur en boîtier 0805 descend bien plus vite : 33 % à 12 V, soit 1,5 µF. "
        "Repère 1, à 0 V : le capacimètre mesure presque sans tension, sa lecture est proche du marquage. "
        "Repère 2, à 12 V : il reste un tiers, un condensateur marqué 4,7 µF ne vaut plus que 1,5 µF sur un rail 12 V. "
        "Ce n'est pas une panne : c'est le comportement normal de la classe II (X5R, X7R, Y5V). Un condensateur de remplacement se choisit donc à boîtier et tension nominale au moins égaux.",
        b,
    )


FIGURES = {
    "lire-le-marquage": (fig_marking, []),
    "fissure-de-flexion": (fig_flex_crack, []),
    "court-circuit-sur-le-rail": (fig_rail_short, ["BEEP", "BEEP"]),
    "capacite-sous-polarisation": (fig_dc_bias, []),
}
