"""Figures of guide 13, the fuse and the fusible resistor."""

from __future__ import annotations

from elements import MONO, Point, lead, meter, probe, svg, text


def _heading(title: str, subtitle: str) -> str:
    return text(24, 38, title, size=20, weight=700) + text(24, 60, subtitle, "mut", 14)


def _fuse(
    cx: float, cy: float, w: float, h: float, state: str
) -> tuple[str, Point, Point]:
    """Glass cartridge fuse centred on (cx, cy); `state` is "ok", "gap" or "black".

    Returns (svg, centre of the left cap, centre of the right cap).
    """
    cap = 0.2 * w
    x1, x2 = cx - w / 2, cx + w / 2
    glass = "#3b3f46" if state == "black" else "#dbeafe"
    o = f'  <rect x="{x1 + cap / 2:.1f}" y="{cy - h / 2 + 1.5:.1f}" width="{w - cap:.1f}" height="{h - 3:.1f}" fill="{glass}" fill-opacity="0.85" stroke="#7d8794"/>\n'
    if state == "ok":
        o += f'  <path d="M{x1 + cap:.1f} {cy} H{x2 - cap:.1f}" stroke="#7d8794" stroke-width="1.6"/>\n'
    elif state == "gap":
        o += f'  <path d="M{x1 + cap:.1f} {cy} H{cx - 0.1 * w:.1f} M{cx + 0.1 * w:.1f} {cy} H{x2 - cap:.1f}" stroke="#7d8794" stroke-width="1.6"/>\n'
        o += f'  <circle cx="{cx - 0.1 * w:.1f}" cy="{cy}" r="2.2" fill="#7d8794"/><circle cx="{cx + 0.1 * w:.1f}" cy="{cy}" r="2.2" fill="#7d8794"/>\n'
    for x in (x1, x2 - cap):
        o += f'  <rect x="{x:.1f}" y="{cy - h / 2:.1f}" width="{cap:.1f}" height="{h}" rx="3" fill="#c9d0d9" stroke="#7d8794" stroke-width="1.5"/>\n'
    return o, (x1 + cap / 2, cy), (x2 - cap / 2, cy)


# ---------------------------------------------------------------- figure 1
def fig_read() -> str:
    b = _heading(
        "Lire un fusible : le marquage, puis l'état du fil",
        "Le marquage est gravé sur une des capsules ; il dit par quoi remplacer, jamais par plus gros",
    )
    f, _, _ = _fuse(380, 124, 300, 44, "ok")
    b += f
    b += f'  <text x="264" y="129" font-size="10" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#1f2933">T2AL</text>\n'
    b += f'  <text x="496" y="129" font-size="10" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#1f2933">250V</text>\n'
    for i, (code, head, sub) in enumerate(
        (
            ("T", "temporisé", "F : rapide"),
            ("2A", "courant assigné", "2 A en permanence"),
            ("L", "faible pouvoir de coupure", "H : élevé, souvent céramique"),
            ("250V", "tension assignée", "tension maximale à couper"),
        )
    ):
        x = 24 + 184 * i
        b += f'  <rect x="{x}" y="176" width="60" height="34" rx="5" fill="#20242b" stroke="#7d8794"/>\n'
        b += f'  <text x="{x + 30}" y="199" font-size="17" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#ffffff">{code}</text>\n'
        b += text(x, 230, head, "blue", 13, weight=700)
        b += text(x, 247, sub, "mut", 12)
    b += '  <path class="grid" d="M24 272 H736"/>\n'
    b += text(24, 300, "Ce que montre le verre", size=15, weight=700)
    for i, (state, cls, head, sub) in enumerate(
        (
            ("ok", "ok", "Fil entier", "à confirmer au bipeur"),
            ("gap", "warn", "Fil fondu net", "surcharge lente"),
            ("black", "no", "Verre noirci", "court-circuit franc en aval"),
        )
    ):
        cx = 130 + 250 * i
        f, _, _ = _fuse(cx, 340, 150, 26, state)
        b += f
        b += text(cx, 380, head, cls, 13, "middle", 700)
        b += text(cx, 397, sub, "mut", 12, "middle")
    b += text(
        24,
        432,
        "Corps céramique, fusible CMS, résistance fusible : rien à voir de l'extérieur, seule la mesure tranche.",
        "mut",
        12,
    )
    return svg(
        760,
        450,
        "Lire le marquage et l'état d'un fusible en verre",
        "En haut, un fusible cartouche en verre dont les capsules portent le marquage T2AL250V. "
        "T : temporisé, F voudrait dire rapide. 2A : courant assigné, 2 A en permanence. L : faible pouvoir de coupure, H voudrait dire élevé, souvent avec un corps céramique. 250V : tension assignée, la tension maximale à couper. "
        "En bas, trois états visibles à travers le verre : fil entier, à confirmer au bipeur ; fil fondu net, signe d'une surcharge lente ; verre noirci, signe d'un court-circuit franc en aval. "
        "Sur un corps céramique, un fusible CMS ou une résistance fusible, rien ne se voit de l'extérieur : seule la mesure tranche.",
        b,
    )


def _half(
    x0: float,
    sel: str,
    lcd: str,
    unit: str,
    flag: str,
    title: str,
    notes: tuple[str, ...],
) -> tuple[str, Point, Point, Point, Point]:
    """Half-figure: title, meter, notes and a fuse. Returns (svg, V jack, COM jack, left cap, right cap)."""
    o = text(x0 + 20, 100, title, size=15, weight=700)
    m, (_, com, v) = meter(x0 + 24, 116, 0.9, sel, lcd, unit, flag)
    o += m
    for i, line in enumerate(notes):
        o += text(x0 + 205, 132 + 16 * i, line, "mut", 12)
    return o, v, com, (x0 + 237, 230), (x0 + 327, 230)


def _hookup(
    v: Point, com: Point, red_tip: Point, black_tip: Point, slant: float
) -> str:
    """Red lead inside, black lead outside: the cables do not cross."""
    pr, (ex, ey) = probe(*red_tip, -slant, 0.9, True)
    o = (
        lead(
            v,
            f"V400 C{v[0]:.1f} 436 {ex:.1f} 446 {ex:.1f} 410 L{ex:.1f} {ey:.1f}",
            True,
        )
        + pr
    )
    pr, (ex, ey) = probe(*black_tip, 0.3, 0.95, False)
    return (
        o
        + lead(
            com,
            f"V404 C{com[0]:.1f} 470 {ex:.1f} 482 {ex:.1f} 410 L{ex:.1f} {ey:.1f}",
            False,
        )
        + pr
    )


# ---------------------------------------------------------------- figure 2
def fig_continuity() -> str:
    b = _heading(
        "Hors tension : le bipeur d'une capsule à l'autre",
        "Sélecteur sur le bipeur, carte débranchée et déchargée, une pointe sur chaque capsule du fusible",
    )
    b += '  <path class="grid" d="M380 84 V520"/>\n'
    for x0, lcd, flag, state, title, notes, cls, verdict in (
        (
            0,
            "0.2",
            "•)))",
            "ok",
            "Fusible bon : il sonne",
            ("Quelques dixièmes", "d'ohm, pointes", "comprises."),
            "ok",
            (
                "✓ bip continu, proche des pointes en court-circuit",
                "le fusible conduit",
            ),
        ),
        (
            380,
            "OL",
            "",
            "gap",
            "Fusible fondu : silence",
            ("Pas de bip, OL :", "le circuit est", "ouvert."),
            "no",
            ("✗ OL, pas de bip", "chercher la cause avant de remplacer"),
        ),
    ):
        o, v, com, left, right = _half(x0, "BEEP", lcd, "Ω", flag, title, notes)
        f, _, _ = _fuse(x0 + 282, 230, 110, 24, state)
        b += o + f + _hookup(v, com, left, right, 0.45)
        b += text(x0 + 190, 478, verdict[0], cls, 14, "middle", 700)
        b += text(x0 + 190, 496, verdict[1], "mut", 12, "middle")
    return svg(
        760,
        526,
        "Contrôle d'un fusible au bipeur, hors tension",
        "Deux multimètres, sélecteur sur le bipeur, ont une pointe sur chaque capsule d'un fusible, carte débranchée et déchargée. "
        "À gauche, fusible bon : l'appareil sonne en continu et lit 0,2 Ω, quelques dixièmes d'ohm pointes comprises. "
        "À droite, fusible fondu : pas de bip, l'appareil affiche OL, le circuit est ouvert ; chercher la cause avant de remplacer.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def fig_voltage() -> str:
    b = _heading(
        "Sous tension : comparer la tension en amont et en aval",
        "Sélecteur sur V continu, pointe noire à la masse, pointe rouge sur une capsule puis sur l'autre",
    )
    b += '  <path class="grid" d="M380 84 V470"/>\n'
    for x0, lcd, title, notes, upstream in (
        (
            0,
            "12.03",
            "En amont : le rail est là",
            ("Capsule côté", "alimentation :", "12 V attendus."),
            True,
        ),
        (
            380,
            "0.00",
            "En aval : plus rien",
            ("Capsule côté", "charge : 0 V,", "le fusible est ouvert."),
            False,
        ),
    ):
        o, v, com, left, right = _half(x0, "VDC", lcd, "V", "", title, notes)
        f, _, _ = _fuse(x0 + 282, 230, 110, 24, "gap")
        gx, gy = x0 + 340, 316
        b += o
        b += f'  <path class="wire" d="M{x0 + 205} 230 H{x0 + 227} M{x0 + 337} 230 H{x0 + 362} M{gx - 22} {gy} H{gx + 22} M{gx} {gy} v8 M{gx - 9} {gy + 8} h18 M{gx - 5} {gy + 13} h10"/>\n'
        b += f
        b += text(x0 + 228, 212, "amont", "mut", 12, "middle")
        b += text(x0 + 336, 212, "aval", "mut", 12, "middle")
        b += text(gx + 6, gy - 8, "0 V", "mut", 12, "middle")
        b += _hookup(v, com, left if upstream else right, (gx - 12, gy), 0.5)
    b += text(
        380,
        492,
        "✗ Tension en amont, rien en aval : fusible ouvert.",
        "no",
        14,
        "middle",
        700,
    )
    b += text(
        380,
        514,
        "✓ Même tension des deux côtés : le fusible conduit, chercher ailleurs.",
        "ok",
        13,
        "middle",
        700,
    )
    b += text(
        380,
        536,
        "Un fusible ne fond pas sans raison : chercher le court-circuit en aval avant de remettre sous tension.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        554,
        "Mesure de la tension de part et d'autre d'un fusible sous tension",
        "Deux multimètres, sélecteur sur volts continus, ont leur pointe noire à la masse. "
        "À gauche, la pointe rouge touche la capsule côté alimentation, en amont du fusible : l'appareil lit 12,03 V, le rail est présent. "
        "À droite, la pointe rouge touche la capsule côté charge, en aval : l'appareil lit 0,00 V. Une tension en amont et rien en aval : le fusible est ouvert. "
        "La même tension des deux côtés signifierait que le fusible conduit et qu'il faut chercher ailleurs. "
        "Un fusible ne fond pas sans raison : chercher le court-circuit en aval avant de remettre sous tension.",
        b,
    )


FIGURES = {
    "lire-un-fusible": (fig_read, []),
    "bipeur-hors-tension": (fig_continuity, ["BEEP", "BEEP"]),
    "tension-amont-et-aval": (fig_voltage, ["VDC", "VDC"]),
}
