"""Figures of guide 90, visual inspection of a board.

A cracked solder joint under the meter, photographing the back of a connector, reading a chip
marking, probing through a conformal coating.
"""

from __future__ import annotations

from elements import MONO, heading, lead, meter, probe, res_h, svg, text, verdict

COPPER = 'fill="#d4a017"'
SOLDER = 'fill="#c9d0d9" stroke="#8b949e"'
LEAD = 'stroke="#aab2bd" stroke-width="4" fill="none" stroke-linejoin="round" stroke-linecap="round"'
TIP_Y = 170  # end of the leads sticking out of the joints


def _board(x0: float) -> tuple[str, float, float, float]:
    """Through-hole resistor seen from the side, solder side up, left joint cracked.

    Returns (svg, x of the left lead, x of the right lead, x of the probe point on the track).
    """
    lx, rx = x0 + 150, x0 + 260
    o = f'  <rect x="{x0 + 44}" y="200" width="292" height="22" rx="3" fill="#1f7a4d"/>\n'
    o += f'  <rect x="{x0 + 56}" y="196" width="{lx - 15 - x0 - 56}" height="4" {COPPER}/>\n'
    o += text(x0 + 114, 188, "piste", "mut", 11, "middle")
    o += f'  <text x="{x0 + 300}" y="215" font-size="9" text-anchor="middle" fill="#ffffff">carte</text>\n'
    for x in (lx, rx):
        o += f'  <rect x="{x - 15}" y="196" width="30" height="4" {COPPER}/>\n'
        o += f'  <path d="M{x - 14} 196 L{x - 3} 181 H{x + 3} L{x + 14} 196 Z" {SOLDER}/>\n'
    o += f'  <path d="M{lx} {TIP_Y} V262 H{lx + 18} M{rx} {TIP_Y} V262 H{rx - 18}" {LEAD}/>\n'
    o += res_h(lx + 18, rx - 18, 262, 22)
    o += text((lx + rx) / 2, 290, "composant, sous la carte", "mut", 11, "middle")
    # ring crack: the fillet no longer touches the lead
    o += f'  <ellipse cx="{lx}" cy="182" rx="6" ry="2.2" fill="none" stroke="#111111" stroke-width="1.6"/>\n'
    o += f'  <path d="M{lx - 8} 182 L{lx - 40} 160" stroke="#b91c1c" stroke-width="1.2"/>\n'
    o += text(lx - 42, 156, "fissure", "no", 11, "end", 700)
    return o, lx, rx, x0 + 84


def _half(
    x0: float,
    sel: str,
    lcd: str,
    unit: str,
    flag: str,
    title: str,
    on_track: bool,
    verdict: tuple[str, str],
    cls: str,
) -> str:
    """One panel: the board, a meter under it, black probe left, red probe right."""
    o = text(x0 + 20, 100, title, size=15, weight=700)
    board, lx, rx, track = _board(x0)
    o += board
    m, (_, com, v) = meter(x0 + 122, 300, 0.7, sel, lcd, unit, flag)
    o += m
    black, red = ((track, 196), (lx, TIP_Y)) if on_track else ((lx, TIP_Y), (rx, TIP_Y))
    p, e = probe(*black, -0.55, -0.83, False)
    o += (
        lead(
            com,
            f"V500 C{com[0]:.1f} 532 {x0 + 24} 536 {x0 + 24} 450 V200 C{x0 + 24} 150 {x0 + 30} {e[1]:.1f} {e[0]:.1f} {e[1]:.1f}",
            False,
        )
        + p
    )
    p, e = probe(*red, 0.55, -0.83, True)
    o += (
        lead(
            v,
            f"V500 C{v[0]:.1f} 532 {x0 + 356} 536 {x0 + 356} 450 V200 C{x0 + 356} 150 {x0 + 350} {e[1]:.1f} {e[0]:.1f} {e[1]:.1f}",
            True,
        )
        + p
    )
    o += text(x0 + 190, 548, verdict[0], cls, 13, "middle", 700)
    o += text(x0 + 190, 566, verdict[1], "mut", 12, "middle")
    return o


# ---------------------------------------------------------------- figure 1
def fig_cracked_joint() -> str:
    b = heading(
        "Joint de brasure fissuré : mesurer à travers le joint",
        "Carte hors tension et déchargée, côté joints ; le joint de la patte gauche est fissuré en anneau",
    )
    b += '  <path class="grid" d="M380 84 V570"/>\n'
    b += _half(
        0,
        "20k",
        "10.0",
        "kΩ",
        "",
        "Pointes sur les deux pattes",
        False,
        ("✗ 10 kΩ, valeur normale", "le joint n'est pas sur le chemin mesuré"),
        "no",
    )
    b += _half(
        380,
        "BEEP",
        "OL",
        "Ω",
        "",
        "De la patte à la piste, en appuyant",
        True,
        (
            "✓ OL ou bip qui coupe : la fissure est trouvée",
            "au repos, le joint peut lire 0 Ω : appuyer, tapoter",
        ),
        "ok",
    )
    return svg(
        760,
        584,
        "Contrôle d'un joint de brasure fissuré au multimètre, hors tension",
        "Une résistance traversante vue de côté, côté joints en haut ; le joint de brasure de sa patte gauche est fissuré en anneau autour de la patte. "
        "À gauche, multimètre sur ohmmètre, calibre 20 kΩ, une pointe sur chaque patte : il lit 10,0 kΩ, la valeur normale, "
        "car le joint n'est pas sur le chemin mesuré. "
        "À droite, multimètre sur le bipeur, pointe rouge sur la patte gauche, pointe noire sur la piste qui part de sa pastille, en appuyant sur le composant : "
        "il affiche OL sans biper, la patte ne touche plus la piste. Au repos, un joint fissuré peut lire 0 Ω : appuyer ou tapoter pendant la mesure.",
        b,
    )


# ---------------------------------------------------------------- figure 2
HEADER_PINS = 6  # single-row pin header of the connector figure
PANEL_W = 380  # width of one panel of a two-panel figure


def flipped(x: float, x0: float) -> float:
    """x of a point once the board is turned over like a page, in the panel starting at x0."""
    return 2 * x0 + PANEL_W - x


def header_pins(x0: float, back: bool) -> dict[int, float]:
    """x of each pin of the header, by number: pin 1 on the left from above, mirrored from the back."""
    top = {n: x0 + 90 + 40 * (n - 1) for n in range(1, HEADER_PINS + 1)}
    return {n: flipped(x, x0) for n, x in top.items()} if back else top


def _connector(x0: float, back: bool) -> str:
    """One face of the board around the header: component side, or solder side once turned over."""
    pins = header_pins(x0, back)
    hole = flipped(x0 + 78, x0) if back else x0 + 78
    o = f'  <rect x="{x0 + 50}" y="130" width="280" height="150" rx="6" fill="{"#17603c" if back else "#1f7a4d"}"/>\n'
    o += f'  <circle cx="{hole}" cy="156" r="9" fill="#ffffff" stroke="#8b949e" stroke-width="2"/>\n'
    o += f'  <text x="{hole}" y="184" font-size="10" text-anchor="middle" fill="#ffffff">repère</text>\n'
    if not back:
        o += f'  <rect x="{x0 + 70}" y="205" width="240" height="34" rx="3" fill="#20242b" stroke="#7d8794"/>\n'
    for n, x in pins.items():
        if back:
            o += f'  <circle cx="{x}" cy="222" r="11" {COPPER}/>\n'
            o += f'  <circle cx="{x}" cy="222" r="7.5" {SOLDER}/>\n'
            o += f'  <circle cx="{x}" cy="222" r="2.2" fill="#5f6b7a"/>\n'
        else:
            o += f'  <rect x="{x - 5}" y="217" width="10" height="10" {COPPER}/>\n'
        o += f'  <text x="{x}" y="264" font-size="12" font-weight="700" text-anchor="middle" fill="#ffffff">{n}</text>\n'
    if back:
        # what the photo frames, and the lamp held at the side
        o += f'  <rect x="{x0 + 62}" y="198" width="256" height="76" rx="4" fill="none" stroke="#60a5fa" stroke-width="2" stroke-dasharray="7 5"/>\n'
        o += text(
            x0 + 190,
            300,
            "cadre de la photo : toutes les broches, nettes",
            "blue",
            11,
            "middle",
        )
        o += f'  <path d="M{x0 + 16} 212 h14 l8 -9 v38 l-8 -9 h-14 Z" fill="#fbbf24" stroke="#b45309"/>\n'
        o += f'  <path d="M{x0 + 42} 212 H{x0 + 58} M{x0 + 42} 222 H{x0 + 58} M{x0 + 42} 232 H{x0 + 58}" stroke="#b45309" stroke-width="1.5"/>\n'
        o += text(x0 + 16, 196, "lampe", "warn", 10)
    return o


def fig_connector_back() -> str:
    b = heading(
        "Photographier le dos d'un connecteur pour suivre ses broches",
        "Carte hors tension et déchargée ; la carte retournée, la gauche et la droite s'échangent",
    )
    b += f'  <path class="grid" d="M{PANEL_W} 84 V330"/>\n'
    b += text(20, 110, "Face composants", size=15, weight=700)
    b += _connector(0, False)
    b += verdict(190, 322, "Broche 1 à gauche", "du côté du repère", "fg")
    b += text(
        PANEL_W + 20,
        110,
        "Face joints, carte retournée comme une page",
        size=15,
        weight=700,
    )
    b += _connector(PANEL_W, True)
    b += verdict(
        PANEL_W + 190, 322, "Broche 1 à droite", "toujours du côté du repère", "ok"
    )
    steps = (
        "1. Choisir un repère visible des deux faces : trou de fixation, coin, encoche.",
        "2. Photographier les deux faces, lampe de côté ; écrire les numéros des broches sur la photo du dos.",
        "3. Confirmer au bipeur la broche 1, ou une broche d'extrémité, d'une face à l'autre.",
    )
    for i, step in enumerate(steps):
        b += text(24, 378 + 22 * i, step, "fg", 13)
    return svg(
        760,
        440,
        "Photographier le dos d'un connecteur pour suivre ses broches",
        "Une barrette de six broches traversantes vue sur les deux faces d'une carte hors tension. "
        "À gauche, la face composants : la broche 1 est à gauche, près d'un trou de fixation qui sert de repère. "
        "À droite, la carte retournée comme une page, face joints : les six joints de brasure sont dans l'ordre inverse, "
        "la broche 1 est à droite, toujours du côté du trou de fixation. Un cadre en pointillé montre ce que la photo doit contenir, "
        "toutes les broches, nettes ; une lampe tenue de côté éclaire en lumière rasante. "
        "Trois étapes : choisir un repère visible des deux faces, photographier les deux faces et écrire les numéros sur la photo du dos, "
        "confirmer au bipeur la broche 1, ou une broche d'extrémité, d'une face à l'autre.",
        b,
    )


# ---------------------------------------------------------------- figure 3
PART = "TS3A5017"  # orderable part of the example
PART_MARKING = "YA017"  # its top-side marking, from the datasheet
LOT = "K4"  # example lot code


def date_code(year: int, week: int) -> str:
    """Four-digit date code, two digits of the year then the week.

    Some manufacturers print the first week of a multi-week period instead of
    the calendar week (TI SNOA039C, six-week periods): the figure uses a week
    that starts such a period, so its code reads the same either way.
    """
    if not 1 <= week <= 53:
        raise ValueError(f"week {week} is not a calendar week")
    return f"{year % 100:02d}{week:02d}"


MARK_YEAR, MARK_WEEK = 2025, 30


def _package(
    x: float, y: float, w: float, h: float, lines: tuple[str, ...], size: float
) -> str:
    """Small-outline package seen from above, pin 1 bottom left beside the dot, marking centred."""
    o = ""
    n = 8
    for i in range(n):
        px = x + w * (i + 0.5) / n
        for py in (y - h * 0.16, y + h):
            o += f'  <rect x="{px - w * 0.022:.1f}" y="{py:.1f}" width="{w * 0.044:.1f}" height="{h * 0.16:.1f}" fill="#c9d0d9"/>\n'
    o += f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#20242b" stroke="#7d8794"/>\n'
    o += f'  <circle cx="{x + w * 0.08:.1f}" cy="{y + h * 0.8:.1f}" r="{h * 0.06:.1f}" fill="#5f6b7a"/>\n'
    for i, line in enumerate(lines):
        ly = y + h * 0.5 + size * (i - (len(lines) - 1) / 2) * 1.25 + size * 0.35
        o += f'  <text x="{x + w / 2}" y="{ly:.1f}" font-size="{size}" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#d7dce2">{line}</text>\n'
    return o


def fig_chip_marking() -> str:
    code = date_code(MARK_YEAR, MARK_WEEK)
    lines = (PART_MARKING, f"{code} {LOT}")
    b = heading(
        "Lire le marquage d'un circuit intégré",
        "Carte hors tension ; loupe ou photo rapprochée, lampe tenue de côté",
    )
    b += _package(50, 116, 300, 130, lines, 30)
    b += text(74, 284, "1", "no", 13, "middle", 700)
    b += text(88, 284, "broche 1, à côté du point", "mut", 12)
    # lighting: the same chip lit from the front, then from the side
    b += text(420, 104, "Lumière de face", size=14, weight=700)
    b += _package(420, 124, 140, 62, lines, 14)
    b += '  <ellipse cx="490" cy="155" rx="56" ry="24" fill="#ffffff" fill-opacity="0.88"/>\n'
    b += verdict(490, 222, "✗ reflet", "le marquage disparaît", "no")
    b += text(590, 104, "Lumière rasante", size=14, weight=700)
    b += _package(590, 124, 140, 62, lines, 14)
    b += verdict(660, 222, "✓ gravure lisible", "tourner lampe ou carte", "ok")
    rows = (
        (
            PART_MARKING,
            f"référence, souvent abrégée : la fiche technique donne le code (ici {PART})",
        ),
        (
            code,
            f"code de date, par exemple l'année puis la semaine (ici {MARK_YEAR}, semaine {MARK_WEEK})",
        ),
        (LOT, "code de lot : traçabilité ; il ne dit rien de la référence"),
    )
    for i, (mark, meaning) in enumerate(rows):
        y = 326 + 28 * i
        b += f'  <text class="blue" x="24" y="{y}" font-size="15" font-weight="700" font-family="{MONO}">{mark}</text>\n'
        b += text(100, y, meaning, "fg", 13)
    b += text(
        24,
        414,
        "Le format des codes de date et de lot dépend du fabricant ; un logo peut s'y ajouter.",
        "mut",
        12,
    )
    return svg(
        760,
        432,
        "Lecture du marquage d'un circuit intégré",
        f"Un circuit intégré vu de dessus, la broche 1 en bas à gauche à côté d'un point. Il porte deux lignes : {PART_MARKING}, puis {code} {LOT}. "
        f"{PART_MARKING} est la référence, souvent abrégée : la fiche technique donne le code, ici celui du {PART}. "
        f"{code} est un code de date, par exemple l'année puis la semaine, ici {MARK_YEAR}, semaine {MARK_WEEK}. "
        f"{LOT} est un code de lot, qui sert à la traçabilité et ne dit rien de la référence. "
        "À droite, le même boîtier sous deux éclairages : en lumière de face, un reflet efface le marquage ; "
        "en lumière rasante, la gravure se lit. Le format des codes de date et de lot dépend du fabricant.",
        b,
    )


# ---------------------------------------------------------------- figure 4
TERMINAL = (160, 176)  # x range of the left metal termination of the coated part
PART_TOP = 258
NEEDLE_TIP = (168, PART_TOP)


def fig_coating() -> str:
    b = heading(
        "Mesurer à travers un vernis de tropicalisation",
        "Carte hors tension et déchargée ; pointe fine sur la terminaison métallique du composant",
    )
    # board cross-section: substrate, pads, component, coating
    b += '  <rect x="40" y="300" width="400" height="34" fill="#2f6b3a" stroke="#1d4426"/>\n'
    b += '  <rect x="110" y="290" width="70" height="10" fill="#c9a227" stroke="#7a6212"/>\n'
    b += '  <rect x="300" y="290" width="70" height="10" fill="#c9a227" stroke="#7a6212"/>\n'
    b += f'  <rect x="{TERMINAL[0]}" y="{PART_TOP}" width="160" height="32" rx="3" fill="#20242b" stroke="#7d8794"/>\n'
    b += f'  <rect x="{TERMINAL[0]}" y="{PART_TOP}" width="{TERMINAL[1] - TERMINAL[0]}" height="32" fill="#c0c7d0" stroke="#7d8794"/>\n'
    b += f'  <rect x="304" y="{PART_TOP}" width="16" height="32" fill="#c0c7d0" stroke="#7d8794"/>\n'
    # solder fillets between each termination and its pad
    b += '  <path d="M160 270 V290 H146 Z M320 270 V290 H334 Z" fill="#aeb6c0" stroke="#7d8794"/>\n'
    b += '  <path d="M40 300 V292 H104 Q110 282 120 284 L156 256 Q240 244 324 256 L360 284 Q370 282 376 292 H440 V300" fill="#93c5fd" fill-opacity="0.45" stroke="#2563eb" stroke-width="1.5"/>\n'
    b += text(440, 276, "vernis", "blue", 12, "end", 700)
    b += text(145, 356, "pastille", "mut", 11, "middle")
    b += text(240, 356, "composant", "mut", 11, "middle")
    b += text(335, 356, "pastille", "mut", 11, "middle")
    # needle alone (no meter here): steel needle then red handle, tip on the left termination
    tx, ty = NEEDLE_TIP
    b += f'  <path d="M{tx} {ty} L{tx - 28} {ty - 34}" stroke="#c0c7d0" stroke-width="2.5" stroke-linecap="round"/>\n'
    b += f'  <path d="M{tx - 28} {ty - 34} L{tx - 58} {ty - 84}" stroke="#dc2626" stroke-width="12" stroke-linecap="round"/>\n'
    b += text(40, 130, "pointe-aiguille inclinée,", "fg", 12)
    b += text(40, 146, "sur la terminaison", "fg", 12)
    notes = (
        ("Repérer", "lampe UV-A, si le vernis est fluorescent"),
        ("Terminaison", "sinon la pastille : la lecture inclut le joint"),
        ("Dégager", "localement, selon la fiche du vernis"),
        ("Lire", "comparer à un composant identique"),
        ("Jamais", "sur le corps, ni près des broches à pas fin"),
        ("Après", "revernir la zone au pinceau, laisser sécher"),
    )
    for i, (head, sub) in enumerate(notes):
        y = 120 + 44 * i
        b += text(480, y, head, "warn" if head == "Jamais" else "fg", 13, weight=700)
        b += text(480, y + 17, sub, "mut", 12)
    return svg(
        760,
        400,
        "Mesure à travers un vernis de tropicalisation",
        "Coupe d'une carte recouverte de vernis de tropicalisation : un composant monté en surface sur deux pastilles, le tout sous une couche de vernis. "
        "Une pointe-aiguille, inclinée, traverse le vernis jusqu'à la terminaison métallique du composant ; carte hors tension et déchargée. "
        "À droite, les règles : une lampe UV-A fait briller le vernis s'il est fluorescent ; faute d'atteindre la terminaison, la pastille, mais la lecture inclut alors le joint de brasure ; "
        "dégager localement selon la fiche technique du vernis ; comparer à un composant identique ; "
        "jamais sur le corps du composant ni près des broches à pas fin ; après la réparation, revernir la zone au pinceau et laisser sécher.",
        b,
    )


FIGURES = {
    "joint-fissure": (fig_cracked_joint, ["20k", "BEEP"]),
    "photo-connecteur": (fig_connector_back, []),
    "marquage-puce": (fig_chip_marking, []),
    "mesure-sous-vernis": (fig_coating, []),
}
