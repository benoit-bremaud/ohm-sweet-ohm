"""Figures of guide 12, the NTC and PTC thermistors."""

from __future__ import annotations

from elements import (
    MONO,
    NODE_A,
    NODE_B,
    Point,
    bands,
    box,
    lead,
    meter,
    probe,
    res_h,
    side_hookup,
    svg,
    text,
)

LEG = 'stroke="#aab2bd" stroke-width="4" fill="none" stroke-linecap="round"'
BEAD = ("#2f3640", "#11151a")
DISC = ("#1f5f43", "#123a29")
POLYMER = ("#e3b23c", "#9a7416")


def _heading(title: str, subtitle: str) -> str:
    return text(24, 38, title, size=20, weight=700) + text(24, 60, subtitle, "mut", 14)


def _bead(cx: float, cy: float, legs: float = 56) -> tuple[str, tuple[Point, Point]]:
    """Epoxy-bead NTC on two radial leads. Returns (svg, lead ends left and right)."""
    left, right = (cx - 15, cy + legs), (cx + 15, cy + legs)
    o = f'  <path {LEG} d="M{cx - 5} {cy} L{left[0]} {left[1]} M{cx + 5} {cy} L{right[0]} {right[1]}"/>\n'
    o += f'  <ellipse cx="{cx}" cy="{cy}" rx="13" ry="16" fill="{BEAD[0]}" stroke="{BEAD[1]}" stroke-width="1.5"/>\n'
    o += f'  <ellipse cx="{cx - 4}" cy="{cy - 6}" rx="3" ry="5" fill="#ffffff" fill-opacity="0.18"/>\n'
    return o, (left, right)


def _radial(
    cx: float, cy: float, w: float, h: float, rx: float, colour: tuple[str, str]
) -> str:
    """Radial part (disc or square wafer) on two leads, without marking."""
    o = f'  <path {LEG} d="M{cx - 10} {cy} V{cy + h / 2 + 22} M{cx + 10} {cy} V{cy + h / 2 + 22}"/>\n'
    o += f'  <rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="{rx}" fill="{colour[0]}" stroke="{colour[1]}" stroke-width="1.5"/>\n'
    return o


# ---------------------------------------------------------------- figure 1
def fig_identify() -> str:
    b = _heading(
        "CTN ou CTP : le sens de variation fait la famille",
        "Trois boîtiers courants sur une carte, et l'allure de leur résistance quand la température monte",
    )
    b += '  <path class="grid" d="M410 84 V452"/>\n'
    b += text(24, 100, "Les reconnaître", size=15, weight=700)
    p, _ = _bead(64, 138, 44)
    b += p
    b += text(120, 136, "CTN de mesure", "blue", 14, weight=700)
    b += text(120, 154, "perle d'époxy, parfois au bout de deux fils", "mut", 12)
    b += text(120, 170, "marquée 103 ou non marquée : 10 kΩ à 25 °C", "mut", 12)
    b += _radial(64, 250, 54, 54, 27, DISC)
    b += f'  <text x="64" y="255" font-size="13" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#ffffff">5D-11</text>\n'
    b += text(120, 240, "CTN de puissance", "blue", 14, weight=700)
    b += text(120, 258, "disque de 11 mm en série avec une entrée", "mut", 12)
    b += text(120, 274, "5D-11 : 5 Ω à 25 °C ; secteur : hors périmètre", "mut", 12)
    b += _radial(64, 368, 46, 40, 5, POLYMER)
    b += text(120, 358, "CTP polymère", "amber", 14, weight=700)
    b += text(120, 376, "fusible réarmable, pastille jaune ou boîtier CMS", "mut", 12)
    b += text(120, 392, "à froid : d'une fraction d'ohm à quelques ohms", "mut", 12)

    b += text(430, 100, "Résistance selon la température", size=15, weight=700)
    b += '  <path class="wire" stroke-width="1.5" d="M450 126 V330 H730"/>\n'
    b += text(444, 134, "Ω", "mut", 12, "end")
    b += text(730, 348, "température →", "mut", 12, "end")
    b += '  <path d="M458 140 C510 262 610 300 724 312" fill="none" stroke="#2563eb" stroke-width="3" stroke-linecap="round"/>\n'
    b += '  <path d="M458 316 H612 C650 314 664 250 672 140" fill="none" stroke="#d97706" stroke-width="3" stroke-linecap="round"/>\n'
    b += text(500, 188, "CTN", "blue", 13, weight=700)
    b += text(684, 170, "CTP", "amber", 13, weight=700)
    b += text(
        430, 382, "CTN : la résistance baisse quand ça chauffe.", "blue", 13, weight=700
    )
    b += text(
        430,
        404,
        "CTP : presque rien à froid, puis elle bondit",
        "amber",
        13,
        weight=700,
    )
    b += text(
        430, 422, "au-delà de sa température de basculement.", "amber", 13, weight=700
    )
    return svg(
        760,
        470,
        "Reconnaître une thermistance CTN ou CTP",
        "À gauche, trois boîtiers. La CTN de mesure : une perle d'époxy, parfois au bout de deux fils, marquée 103 ou non marquée, 10 kΩ à 25 °C. "
        "La CTN de puissance : un disque noir ou vert en série avec une entrée d'alimentation (côté secteur : hors périmètre), marqué 5D-11, soit 5 Ω à 25 °C et un disque de 11 mm. "
        "La CTP polymère, ou fusible réarmable : une pastille jaune ou un boîtier CMS, d'une fraction d'ohm à quelques ohms à froid. "
        "À droite, l'allure de la résistance selon la température : celle de la CTN baisse régulièrement quand la température monte ; "
        "celle de la CTP reste presque nulle à froid, puis bondit au-delà de sa température de basculement.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def fig_warm() -> str:
    b = _heading(
        "Hors tension : la valeur à froid, puis la réaction à la chaleur",
        "Sélecteur sur Ω, calibre 20 kΩ : CTN de 10 kΩ sortie du circuit, ou un fil débranché",
    )
    b += '  <path class="grid" d="M380 84 V470"/>\n'

    def half(
        x0: float,
        title: str,
        lcd: str,
        notes: tuple[str, ...],
        warm: bool,
        verdict: tuple[str, str],
    ) -> str:
        o = text(x0 + 20, 100, title, size=15, weight=700)
        m, (_, com, v) = meter(x0 + 24, 116, 0.9, "20k", lcd, "kΩ")
        o += m
        for i, line in enumerate(notes):
            o += text(x0 + 205, 132 + 16 * i, line, "mut", 12)
        if warm:
            o += f'  <circle cx="{x0 + 282}" cy="236" r="34" fill="#f59e0b" fill-opacity="0.28" stroke="#d97706" stroke-dasharray="4 4"/>\n'
        p, ((x1, y), (x2, _)) = _bead(x0 + 282, 236)
        o += p
        # red lead inside, black lead outside: the cables do not cross
        pr, (ex, ey) = probe(x1, y - 4, -0.8, 0.6, True)
        o += (
            lead(
                v,
                f"V400 C{v[0]:.1f} 436 {ex:.1f} 446 {ex:.1f} 410 L{ex:.1f} {ey:.1f}",
                True,
            )
            + pr
        )
        pr, (ex, ey) = probe(x2, y - 4, 0.3, 0.95, False)
        o += (
            lead(
                com,
                f"V404 C{com[0]:.1f} 470 {ex:.1f} 482 {ex:.1f} 410 L{ex:.1f} {ey:.1f}",
                False,
            )
            + pr
        )
        o += text(x0 + 190, 478, verdict[0], "ok", 14, "middle", 700)
        o += text(x0 + 190, 496, verdict[1], "mut", 12, "middle")
        return o

    b += half(
        0,
        "À 25 °C : la valeur nominale",
        "10.04",
        ("La valeur dépend de", "la pièce : 12,5 kΩ", "à 20 °C, 8 kΩ à 30 °C."),
        False,
        ("✓ proche de 10 kΩ à 25 °C", "comparer à la table de la fiche technique"),
    )
    b += half(
        380,
        "Entre les doigts : la lecture baisse",
        "7.41",
        ("Pincer le corps,", "pas les pattes :", "≈ 32 °C en 20 s."),
        True,
        ("✓ baisse franche, puis retour", "une CTN saine réagit toujours à la chaleur"),
    )
    b += text(
        380,
        528,
        "✗ OL, proche de 0 Ω, ou lecture qui ne bouge pas en chauffant : thermistance à remplacer.",
        "no",
        13,
        "middle",
        700,
    )
    return svg(
        760,
        546,
        "Mesure d'une thermistance CTN à froid puis réchauffée entre les doigts",
        "Deux multimètres, sélecteur sur ohms calibre 20 kΩ, ont leurs pointes sur les deux pattes d'une CTN de 10 kΩ sortie du circuit. "
        "À gauche, à 25 °C, l'appareil lit 10,04 kΩ, la valeur nominale ; elle dépend de la température de la pièce : 12,5 kΩ à 20 °C, 8 kΩ à 30 °C. "
        "À droite, le corps de la CTN est pincé entre les doigts, sans toucher les pattes : vers 32 °C la lecture descend à 7,41 kΩ, puis remonte quand on relâche. "
        "Une lecture OL, proche de 0 Ω, ou qui ne bouge pas en chauffant désigne une thermistance à remplacer.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def fig_divider() -> str:
    b = _heading(
        "Sous tension : la CTN se juge à la tension de son pont diviseur",
        "Sélecteur sur V continu : pointe noire à la masse, pointe rouge au point milieu, là où le circuit lit la température",
    )
    m, jacks = meter(30, 80, 1, "VDC", "1.65", "V")
    b += m
    (xa, ya), (_, yb) = NODE_A, NODE_B
    b += f'  <path class="wire" d="M{xa} {ya} H350 M430 {ya} H470 M{xa} {ya} V{ya - 26} M{xa} {yb} v14 M{xa - 12} {yb + 14} h24 M{xa - 7} {yb + 20} h14 M{xa - 2} {yb + 26} h4"/>\n'
    b += res_h(350, 430, ya, 26, bands("brown", "black", "orange", "gold"))
    b += text(390, ya + 32, "R · 10 kΩ", "fg", 13, "middle", 700)
    b += box(470, ya - 25, 96, 50, "Rail 3,3 V")
    b += text(xa + 10, ya - 30, "→ entrée de mesure du microcontrôleur", "mut", 12)
    b += f'  <path class="wire" d="M{xa} {ya} V{yb}"/>\n'
    cy = (ya + yb) / 2
    b += f'  <ellipse cx="{xa}" cy="{cy}" rx="14" ry="19" fill="{BEAD[0]}" stroke="{BEAD[1]}" stroke-width="1.5"/>\n'
    b += text(xa + 24, cy - 2, "CTN · 10 kΩ à 25 °C", "blue", 13, weight=700)
    b += text(xa + 24, cy + 15, "entre le point milieu et la masse", "blue", 12)
    b += f'  <circle class="fg" cx="{xa}" cy="{ya}" r="5"/><circle class="fg" cx="{xa}" cy="{yb}" r="5"/>\n'
    b += text(xa + 22, yb + 24, "0 V (masse)", "mut", 12)
    b += side_hookup(jacks.v, jacks.com)
    b += text(590, 150, "Au point milieu, à 25 °C", size=14, weight=700)
    for i, (cls, head, sub) in enumerate(
        (
            ("ok", "✓ ≈ 1,65 V", "moitié du rail : CTN saine"),
            ("no", "✗ ≈ 3,3 V", "CTN ou fil coupé"),
            ("no", "✗ ≈ 0 V", "CTN ou câble en court-circuit"),
        )
    ):
        yy = 178 + 44 * i
        b += text(590, yy, head, cls, 13, weight=700)
        b += text(590, yy + 17, sub, "mut", 12)
    b += text(
        300,
        372,
        "Réchauffer la CTN entre les doigts : la tension doit baisser.",
        size=13,
        weight=700,
    )
    b += text(
        300,
        392,
        "Mesurer d'abord le rail : sans 3,3 V, le point milieu ne prouve rien.",
        "mut",
        12,
    )
    return svg(
        760,
        440,
        "Mesure de la tension au point milieu du pont diviseur d'une CTN",
        "Une résistance de 10 kΩ relie le rail 3,3 V au point milieu ; une CTN de 10 kΩ à 25 °C relie ce point milieu à la masse ; le point milieu part vers l'entrée de mesure du microcontrôleur. "
        "Un multimètre, sélecteur sur volts continus, a sa pointe rouge au point milieu et sa pointe noire à la masse ; il lit 1,65 V, la moitié du rail : la CTN est saine. "
        "Environ 3,3 V : CTN ou fil coupé. Environ 0 V : CTN ou câble en court-circuit. "
        "En réchauffant la CTN entre les doigts, la tension doit baisser. Mesurer d'abord le rail : sans 3,3 V, le point milieu ne prouve rien.",
        b,
    )


FIGURES = {
    "reconnaitre-ctn-et-ctp": (fig_identify, []),
    "mesure-a-froid-et-au-chaud": (fig_warm, ["20k", "20k"]),
    "pont-diviseur-sous-tension": (fig_divider, ["VDC"]),
}
