"""Figures of guide 10, the resistor."""

from __future__ import annotations

from elements import (
    BAND_COLOURS,
    BAND_WIDTH,
    BLUE,
    NODE_A,
    NODE_B,
    TAN,
    band_offsets,
    bands,
    bench_supply,
    box,
    chip,
    clip,
    lead,
    meter,
    power_resistor,
    probe,
    res_h,
    res_v,
    side_hookup,
    svg,
    text,
)

YA, YB = NODE_A[1], NODE_B[1]
LEG = 'stroke="#aab2bd" stroke-width="4" fill="none" stroke-linecap="round"'
BOARD = "#1f7a4d"
CHARRED = ("#1c1917", "#0c0a09")


def _heading(title: str, subtitle: str) -> str:
    return text(24, 38, title, size=20, weight=700) + text(24, 60, subtitle, "mut", 14)


# ---------------------------------------------------------------- figure 1
def _banded(y: int, names: tuple[str, ...], labels: tuple[str, ...], body) -> str:
    """Large axial resistor with one label under each band."""
    x1, x2 = 110, 330
    o = f'  <path {LEG} d="M50 {y} H{x1} M{x2} {y} H390"/>\n'
    o += res_h(x1, x2, y, 48, bands(*names), body)
    for off, label in zip(band_offsets(len(names)), labels, strict=True):
        cx = x1 + (x2 - x1) * (off + BAND_WIDTH / 2)
        o += f'  <path class="wire" d="M{cx:.1f} {y + 27} v8" stroke-width="1.5"/>\n'
        o += text(round(cx, 1), y + 50, label, "fg", 13, "middle", 700)
    return o


def fig_read() -> str:
    b = _heading(
        "Lire la valeur : anneaux de couleur et marquage CMS",
        "Toujours lire la valeur attendue avant de mesurer : c'est elle qui donne le calibre et le verdict",
    )
    b += '  <path class="grid" d="M440 84 V452"/>\n'
    b += text(24, 96, "Résistance à anneaux", size=15, weight=700)
    b += text(24, 116, "4 anneaux : 2 chiffres, multiplicateur, tolérance", "mut", 12)
    b += _banded(
        152, ("brown", "black", "orange", "gold"), ("1", "0", "× 1 000", "± 5 %"), TAN
    )
    b += text(110, 224, "10 × 1 000 = 10 kΩ à ± 5 %", "blue", 13, weight=700)
    b += text(24, 254, "5 anneaux : 3 chiffres, multiplicateur, tolérance", "mut", 12)
    b += _banded(
        290,
        ("yellow", "violet", "black", "red", "brown"),
        ("4", "7", "0", "× 100", "± 1 %"),
        BLUE,
    )
    b += text(110, 362, "470 × 100 = 47 kΩ à ± 1 %", "blue", 13, weight=700)
    # digit of each colour
    digits = list(BAND_COLOURS)[:10]
    for i, name in enumerate(digits):
        x = 24 + 40 * i
        ink = "#1f2933" if name in ("yellow", "white", "orange", "grey") else "#ffffff"
        b += f'  <rect x="{x}" y="386" width="36" height="24" rx="4" fill="{BAND_COLOURS[name]}" stroke="#8b949e"/>\n'
        b += f'  <text x="{x + 18}" y="403" font-size="13" font-weight="700" text-anchor="middle" fill="{ink}">{i}</text>\n'
    for x, name, label in (
        (24, "gold", "or : × 0,1 ou ± 5 %"),
        (224, "silver", "argent : × 0,01 ou ± 10 %"),
    ):
        b += f'  <rect x="{x}" y="424" width="20" height="16" rx="3" fill="{BAND_COLOURS[name]}" stroke="#8b949e"/>\n'
        b += text(x + 28, 437, label, "fg", 12)
    b += text(
        24,
        478,
        "L'anneau de tolérance est à l'écart des autres : commencer la lecture par l'autre bout. "
        "Tolérance : marron ± 1 %, rouge ± 2 %.",
        "mut",
        12,
    )
    # chip markings
    b += text(460, 96, "Résistance CMS, marquage imprimé", size=15, weight=700)
    for i, (marking, value, how) in enumerate(
        (
            ("103", "10 × 10³ = 10 kΩ", "2 chiffres puis le nombre de zéros"),
            ("4702", "470 × 10² = 47 kΩ", "4 chiffres : séries à 1 %"),
            ("4R7", "4,7 Ω", "R à la place de la virgule"),
            ("01C", "100 × 100 = 10 kΩ", "EIA-96 : 01 → 100, C → × 100"),
            ("0", "cavalier 0 Ω", "un pont, pas une résistance"),
        )
    ):
        y = 136 + 62 * i
        b += chip(492, y, marking, 64, 32)
        b += text(538, y - 3, value, "blue", 13, weight=700)
        b += text(538, y + 14, how, "mut", 12)
    b += text(460, 436, "Boîtier 0402 et plus petit : souvent aucun", "mut", 12)
    b += text(460, 452, "marquage, lire le schéma ou mesurer.", "mut", 12)
    return svg(
        760,
        496,
        "Lire la valeur d'une résistance : anneaux de couleur et marquage CMS",
        "À gauche, deux résistances à anneaux. Quatre anneaux marron, noir, orange, or : 1, 0, multiplicateur 1 000, tolérance 5 %, soit 10 kΩ. "
        "Cinq anneaux jaune, violet, noir, rouge, marron sur un corps bleu : 4, 7, 0, multiplicateur 100, tolérance 1 %, soit 47 kΩ. "
        "Chiffre de chaque couleur : noir 0, marron 1, rouge 2, orange 3, jaune 4, vert 5, bleu 6, violet 7, gris 8, blanc 9 ; "
        "or : multiplicateur 0,1 ou tolérance 5 % ; argent : multiplicateur 0,01 ou tolérance 10 %. "
        "À droite, cinq résistances CMS : 103 vaut 10 kΩ, 4702 vaut 47 kΩ, 4R7 vaut 4,7 Ω, 01C vaut 10 kΩ en code EIA-96, 0 est un cavalier 0 Ω.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def _pad(x: float, y: float) -> str:
    return (
        f'  <circle cx="{x}" cy="{y}" r="9" fill="#d4a017"/>'
        f'<circle cx="{x}" cy="{y}" r="5" fill="#c9d0d9"/>\n'
    )


def _axial_tile(cx: float, cy: float, colours: list[str], body, halo: str) -> str:
    o = halo
    o += f'  <path {LEG} d="M{cx - 50} {cy} H{cx + 50}"/>\n'
    o += _pad(cx - 50, cy) + _pad(cx + 50, cy)
    return o + res_h(cx - 34, cx + 34, cy, 24, colours, body)


def _joint(x: float, y: float, cracked: bool) -> str:
    """Solder joint of a through-hole lead seen from above."""
    o = f'  <circle cx="{x}" cy="{y}" r="24" fill="#d4a017"/>\n'
    o += f'  <circle cx="{x}" cy="{y}" r="20" fill="#c9d0d9" stroke="#8b949e"/>\n'
    if cracked:
        o += f'  <circle cx="{x}" cy="{y}" r="11" fill="none" stroke="#20242b" stroke-width="3"/>\n'
    else:
        o += f'  <path d="M{x - 12} {y - 8} a14 14 0 0 1 12 -8" stroke="#ffffff" stroke-opacity="0.7" stroke-width="2.5" fill="none" stroke-linecap="round"/>\n'
    return o + f'  <circle cx="{x}" cy="{y}" r="6" fill="#8b949e" stroke="#5f6b7a"/>\n'


def fig_clues() -> str:
    b = _heading(
        "Indices visuels : ce que la résistance montre avant toute mesure",
        "Carte hors tension et déchargée, loupe et bon éclairage",
    )
    grey = ["#2a2522"] * 4
    tiles = (
        (
            "Saine",
            ("anneaux nets,", "vernis intact"),
            ("warn", "peut être ouverte", "quand même : mesurer"),
        ),
        (
            "Brunie",
            ("a chauffé longtemps,", "carte roussie dessous"),
            ("warn", "mesurer, puis chercher", "pourquoi elle chauffe"),
        ),
        (
            "Carbonisée",
            ("corps noirci ou fendu,", "anneaux illisibles"),
            ("no", "ouverte : chercher le", "court-circuit en aval"),
        ),
        (
            "CMS fissurée",
            ("trait fin en travers,", "carte qui a fléchi"),
            ("no", "ouverte ou", "intermittente"),
        ),
        (
            "Soudure fissurée",
            ("anneau sombre", "autour de la patte"),
            ("no", "panne intermittente :", "refaire la soudure"),
        ),
    )
    for i, (name, look, (cls, v1, v2)) in enumerate(tiles):
        x0 = 24 + 144 * i
        cx, cy = x0 + 68, 144
        b += f'  <rect x="{x0}" y="84" width="136" height="120" rx="6" fill="{BOARD}"/>\n'
        if i == 0:
            b += _axial_tile(cx, cy, bands("brown", "black", "orange", "gold"), TAN, "")
        elif i == 1:
            halo = f'  <ellipse cx="{cx}" cy="{cy}" rx="52" ry="30" fill="#4a2c0f" fill-opacity="0.6"/>\n'
            b += _axial_tile(
                cx,
                cy,
                bands("brown", "black", "orange", "gold"),
                ("#b08a5a", "#6b4f2a"),
                halo,
            )
            b += f'  <ellipse cx="{cx}" cy="{cy}" rx="20" ry="11" fill="#3b2208" fill-opacity="0.5"/>\n'
        elif i == 2:
            halo = f'  <ellipse cx="{cx}" cy="{cy}" rx="56" ry="34" fill="#0c0a09" fill-opacity="0.65"/>\n'
            b += _axial_tile(cx, cy, grey, CHARRED, halo)
            b += f'  <path d="M{cx - 6} {cy - 12} l5 7 l-6 5 l7 6 l-4 6" stroke="#a8a29e" stroke-width="1.8" fill="none" stroke-linejoin="round"/>\n'
        elif i == 3:
            for px in (cx - 28, cx + 28):
                b += f'  <rect x="{px - 11}" y="{cy - 20}" width="22" height="40" rx="2" fill="#d4a017"/>\n'
            b += chip(cx, cy, "103", 60, 30)
            b += f'  <path d="M{cx - 14} {cy - 15} l3 8 l-4 6 l4 7 l-2 9" stroke="#f8fafc" stroke-width="1.6" fill="none" stroke-linejoin="round"/>\n'
        else:
            b += _joint(cx - 34, cy - 8, False) + _joint(cx + 34, cy - 8, True)
            b += f'  <text x="{cx - 34}" y="196" font-size="10" text-anchor="middle" fill="#ffffff">saine</text>\n'
            b += f'  <text x="{cx + 34}" y="196" font-size="10" text-anchor="middle" fill="#ffffff">fissurée</text>\n'
        b += text(cx, 228, name, "fg", 14, "middle", 700)
        for j, line in enumerate(look):
            b += text(cx, 248 + 16 * j, line, "mut", 12, "middle")
        b += text(cx, 290, v1, cls, 12, "middle", 700)
        b += text(cx, 306, v2, cls, 12, "middle", 700)
    b += text(
        24,
        338,
        "L'odeur de brûlé et une trace de suie sur le composant voisin comptent aussi. L'aspect oriente, la mesure tranche.",
        "mut",
        12,
    )
    return svg(
        760,
        356,
        "Indices visuels d'une résistance en défaut",
        "Cinq vues de résistances sur une carte. Saine : anneaux nets et vernis intact, mais elle peut être ouverte quand même, il faut mesurer. "
        "Brunie : elle a chauffé longtemps, la carte est roussie dessous ; mesurer puis chercher pourquoi elle chauffe. "
        "Carbonisée : corps noirci ou fendu, anneaux illisibles ; elle est ouverte, chercher le court-circuit en aval. "
        "Résistance CMS fissurée : un trait fin en travers du corps après une flexion de la carte ; ouverte ou intermittente. "
        "Soudure fissurée : un anneau sombre autour de la patte, comparé à une soudure saine ; panne intermittente, refaire la soudure.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def fig_out() -> str:
    b = _heading(
        "Hors circuit : les deux erreurs qui faussent la lecture",
        "Composant sorti de la carte ou une patte levée, valeur attendue lue avant de mesurer",
    )
    b += '  <path class="grid" d="M380 84 V516"/>\n'

    def half(x0, title, sel, lcd, unit, part, notes, fingers, verdict) -> str:
        o = text(x0 + 20, 100, title, size=15, weight=700)
        m, (_, com, v) = meter(x0 + 24, 116, 0.9, sel, lcd, unit)
        o += m
        for i, line in enumerate(notes):
            o += text(x0 + 205, 138 + 16 * i, line, "mut", 12)
        y = 214
        o += f'  <path {LEG} d="M{x0 + 214} {y} H{x0 + 346}"/>\n' + part(x0, y)
        if fingers:
            for fx in (x0 + 222, x0 + 338):
                o += f'  <ellipse cx="{fx}" cy="{y - 4}" rx="13" ry="21" fill="#f2c6a0" stroke="#c99a73"/>\n'
                o += f'  <path d="M{fx - 7} {y - 16} a8 7 0 0 1 14 0" stroke="#c99a73" stroke-width="1.5" fill="#fbe3cf"/>\n'
        # red lead inside, black lead outside: the cables do not cross
        p, (ex, ey) = probe(x0 + 222, y, -0.3, 0.95, True)
        o += (
            lead(
                v,
                f"V400 C{v[0]:.1f} 436 {ex:.1f} 440 {ex:.1f} 380 L{ex:.1f} {ey:.1f}",
                True,
            )
            + p
        )
        p, (ex, ey) = probe(x0 + 338, y, 0.3, 0.95, False)
        o += (
            lead(
                com,
                f"V404 C{com[0]:.1f} 466 {ex:.1f} 476 {ex:.1f} 390 L{ex:.1f} {ey:.1f}",
                False,
            )
            + p
        )
        o += text(x0 + 190, 492, verdict[0], "no", 14, "middle", 700)
        o += text(x0 + 190, 510, verdict[1], "mut", 12, "middle")
        return o

    b += half(
        0,
        "Sous 10 Ω : compter les cordons",
        "200",
        "0.8",
        "Ω",
        lambda x0, y: power_resistor(x0 + 240, x0 + 320, y, "0,47 Ω"),
        ("Pointes en court-circuit :", "0,3 Ω, la résistance", "des cordons."),
        False,
        (
            "✗ 0,8 Ω lus pour 0,47 Ω",
            "retrancher les 0,3 Ω des cordons, ou touche REL : 0,5 Ω",
        ),
    )
    b += half(
        380,
        "Au-dessus de 100 kΩ : pas les doigts",
        "2M",
        "0.833",
        "MΩ",
        lambda x0, y: res_h(
            x0 + 240, x0 + 320, y, 28, bands("brown", "black", "green", "gold")
        ),
        (
            "Deux doigts sur les pointes :",
            "le corps, quelques MΩ,",
            "se met en parallèle.",
        ),
        True,
        (
            "✗ 0,83 MΩ lus pour 1 MΩ",
            "ne toucher qu'une pointe, ou utiliser des pinces : 1,00 MΩ",
        ),
    )
    return svg(
        760,
        530,
        "Mesure hors circuit : résistance des cordons et doigts sur les pointes",
        "Deux multimètres mesurent une résistance sortie de la carte, une pointe sur chaque patte. "
        "À gauche, sélecteur sur le calibre 200 Ω, résistance de 0,47 Ω : l'appareil lit 0,8 Ω, car les cordons ajoutent 0,3 Ω ; "
        "il faut retrancher la valeur lue pointes en court-circuit ou utiliser la touche REL. "
        "À droite, sélecteur sur le calibre 2 MΩ, résistance de 1 MΩ tenue avec un doigt sur chaque pointe : l'appareil lit 0,833 MΩ, "
        "car le corps se met en parallèle ; il ne faut toucher qu'une pointe ou utiliser des pinces.",
        b,
    )


# ---------------------------------------------------------------- figure 4
def fig_in() -> str:
    b = _heading(
        "En circuit : une lecture au-dessus de la nominale condamne la résistance",
        "Sélecteur sur Ω, calibre 200 kΩ : R1 est marquée 100 kΩ ± 5 %, l'appareil lit 148,3 kΩ",
    )
    m, jacks = meter(30, 80, 1, "200k", "148.3", "kΩ")
    b += m
    b += f'  <path class="wire" d="M300 {YA} H545 V165 M300 {YB} H545 V245"/>\n'
    b += res_v(390, YA, YB, colours=bands("brown", "black", "yellow", "gold"))
    b += f'  <circle class="fg" cx="300" cy="{YA}" r="5"/><circle class="fg" cx="300" cy="{YB}" r="5"/>\n'
    b += text(390, 112, "R1 · 100 kΩ", "blue", 13, "middle", 700)
    b += text(390, 306, "mesurée", "blue", 12, "middle")
    b += box(480, 165, 130, 80, "Reste du circuit", ("chemins parallèles", "inconnus"))
    b += text(626, 190, "Un chemin parallèle", "mut", 12)
    b += text(626, 206, "ne peut que faire", "mut", 12)
    b += text(626, 222, "baisser la lecture.", "mut", 12)
    b += side_hookup(jacks.v, jacks.com, polarity=False)
    b += text(300, 358, "Que vaut la lecture stabilisée ?", size=14, weight=700)
    b += '  <rect x="300" y="368" width="240" height="24" rx="5" fill="#f59e0b"/>\n'
    b += '  <rect x="540" y="368" width="60" height="24" fill="#16a34a"/>\n'
    b += '  <rect x="600" y="368" width="140" height="24" rx="5" fill="#dc2626"/>\n'
    b += '  <text x="670" y="385" font-size="12" font-weight="700" text-anchor="middle" fill="#ffffff">lecture ici : 148 kΩ</text>\n'
    b += text(300, 410, "En dessous de 95 kΩ", size=13, weight=700)
    b += text(300, 426, "rien de prouvé : lever une patte", "mut", 12)
    b += text(570, 410, "95 à 105 kΩ", size=13, anchor="middle", weight=700)
    b += text(570, 426, "probablement saine", "mut", 12, "middle")
    b += text(740, 410, "Au-dessus", size=13, anchor="end", weight=700)
    b += text(740, 426, "défectueuse", "mut", 12, "end")
    b += text(
        24,
        458,
        "Conditions : carte hors tension, nœud déchargé, pointes sur les pattes propres, lecture stable et retrouvée pointes inversées.",
        "mut",
        12,
    )
    return svg(
        760,
        476,
        "Mesure en circuit : une lecture au-dessus de la valeur nominale est concluante",
        "Un multimètre, sélecteur sur ohms calibre 200 kΩ, a ses pointes sur les deux pattes d'une résistance R1 soudée, marquée 100 kΩ à 5 %. "
        "Le reste du circuit relie les mêmes nœuds par des chemins parallèles inconnus, qui ne peuvent que faire baisser la lecture. "
        "L'appareil lit 148,3 kΩ, au-dessus de 105 kΩ : la résistance est défectueuse. "
        "Échelle de lecture : en dessous de 95 kΩ, rien de prouvé, lever une patte ; de 95 à 105 kΩ, probablement saine ; au-dessus, défectueuse.",
        b,
    )


# ---------------------------------------------------------------- figure 5
def fig_drop() -> str:
    b = _heading(
        "Sous tension : la chute de tension donne le courant",
        "Sélecteur sur V continu, pointes sur les deux pattes de la résistance série, carte sur alimentation limitée",
    )
    m, (_, com, v) = meter(30, 80, 1, "VDC", "2.35", "V")
    b += m
    b += text(300, 100, "I = U / R = 2,35 V / 10 Ω = 235 mA", "blue", 15, weight=700)
    b += text(
        300, 124, "Attendu sur ce rail : 50 mA. La charge consomme trop.", "fg", 13
    )
    b += text(
        300,
        146,
        "P = U × I = 0,55 W dans une résistance de 0,25 W :",
        "no",
        13,
        weight=700,
    )
    b += text(300, 164, "elle brunit, puis elle s'ouvre.", "no", 13, weight=700)
    y = 250
    b += box(300, y - 40, 90, 80, "Alim. 12 V", ("limitée", "à 300 mA"))
    b += box(640, y - 40, 90, 80, "Charge", ("en défaut",))
    b += f'  <path class="wire" d="M390 {y} H470 M550 {y} H640"/>\n'
    b += res_h(470, 550, y, 28, bands("brown", "black", "black", "gold"))
    b += text(510, y - 24, "R = 10 Ω · 0,25 W", "fg", 13, "middle", 700)
    b += f'  <path class="flow fb" d="M398 {y - 9} H458 M562 {y - 9} H632"/>\n'
    b += text(428, y - 18, "I →", "blue", 12, "middle", 700)
    b += text(597, y - 18, "I →", "blue", 12, "middle", 700)
    p, e = probe(460, y + 2, -0.4, 0.92, True)
    b += lead(v, f"V394 C165 430 {e[0]:.1f} 440 {e[0]:.1f} {e[1]:.1f}", True) + p
    p, e = probe(560, y + 2, 0.4, 0.92, False)
    b += lead(com, f"V398 C120 462 {e[0]:.1f} 470 {e[0]:.1f} {e[1]:.1f}", False) + p
    b += text(444, y + 22, "+", "no", 16, "end", 700)
    b += text(578, y + 22, "−", "fg", 16, weight=700)
    b += text(612, 340, "Remplacer la résistance", "mut", 12)
    b += text(612, 356, "sans réparer l'aval,", "mut", 12)
    b += text(612, 372, "c'est la rebrûler.", "mut", 12)
    return svg(
        760,
        470,
        "Mesurer la chute de tension aux bornes d'une résistance pour connaître le courant",
        "Un multimètre, sélecteur sur volts continus, a sa pointe rouge côté alimentation et sa pointe noire côté charge d'une résistance série de 10 Ω, 0,25 W. "
        "La carte est alimentée en 12 V par une alimentation limitée à 300 mA. L'appareil lit 2,35 V : le courant vaut 2,35 V divisé par 10 Ω, soit 235 mA, "
        "alors que 50 mA sont attendus. La résistance dissipe 0,55 W, plus du double de sa puissance : elle brunit puis s'ouvre. "
        "Le défaut est dans la charge, en aval.",
        b,
    )


# ---------------------------------------------------------------- figure 6
def fig_kelvin() -> str:
    b = _heading(
        "Mesure 4 fils (Kelvin) : une faible valeur sans l'erreur des cordons",
        "Résistance sortie du circuit ; alimentation limitée à 1 A, multimètre sur V continu",
    )
    s, minus, plus = bench_supply(150, 84, "0.35", "1.000", "CC")
    b += s
    y = 322
    b += f'  <path {LEG} d="M118 {y} H195 M335 {y} H412"/>\n'
    b += power_resistor(195, 335, y, "0,1 Ω · 5 W", 34)
    b += f'  <path class="blk" stroke-width="4" fill="none" stroke-linecap="round" d="M{minus[0]} {minus[1]} C{minus[0]} 268 135 262 135 {y - 12}"/>\n'
    b += f'  <path stroke="#dc2626" stroke-width="4" fill="none" stroke-linecap="round" d="M{plus[0]} {plus[1]} C{plus[0]} 268 395 262 395 {y - 12}"/>\n'
    b += clip(135, y, False) + clip(395, y, True)
    b += f'  <path class="flow fa" d="M380 {y - 10} H346 M184 {y - 10} H150"/>\n'
    b += text(265, y - 26, "← I = 1 A", "amber", 12, "middle", 700)
    m, (_, com, v) = meter(202, 378, 0.7, "VDC", "0.100", "V")
    b += m
    p, (ex, ey) = probe(178, y + 2, -0.5, 0.87, False)
    b += (
        lead(
            com,
            f"V596 C{com[0]:.1f} 626 96 630 96 548 V446 C96 412 118 {ey + 22:.1f} {ex:.1f} {ey:.1f}",
            False,
        )
        + p
    )
    p, (ex, ey) = probe(352, y + 2, 0.5, 0.87, True)
    b += (
        lead(
            v,
            f"V596 C{v[0]:.1f} 626 434 630 434 548 V446 C434 412 412 {ey + 22:.1f} {ex:.1f} {ey:.1f}",
            True,
        )
        + p
    )
    b += text(360, y + 26, "+", "no", 16, weight=700)
    b += text(170, y + 26, "−", "fg", 16, "end", 700)
    for i, (num, line, sub) in enumerate(
        (
            (
                "1",
                "Forcer un courant connu",
                "limite réglée à 1,000 A, voyant CC allumé",
            ),
            (
                "2",
                "Lire la tension sur les pattes",
                "pointes entre les pinces, au ras du corps",
            ),
            ("3", "Calculer R = U / I", "0,100 V / 1,000 A = 0,100 Ω"),
        )
    ):
        yy = 112 + 50 * i
        b += f'  <circle class="blue" cx="482" cy="{yy - 4}" r="10"/>\n'
        b += f'  <text x="482" y="{yy}" font-size="12" font-weight="700" text-anchor="middle" fill="#ffffff">{num}</text>\n'
        b += text(500, yy, line, "fg", 14, weight=700)
        b += text(
            500,
            yy + 18,
            sub,
            "blue" if i == 2 else "mut",
            12,
            weight=700 if i == 2 else None,
        )
    b += '  <rect class="panel" x="466" y="262" width="274" height="126" rx="8" stroke-width="1.5"/>\n'
    b += text(480, 286, "Pourquoi 4 fils ?", size=13, weight=700)
    for i, line in enumerate(
        (
            "Le courant passe par les pinces.",
            "Le voltmètre ne prélève presque rien :",
            "ses cordons et ses contacts ne",
            "faussent pas la tension lue.",
            "En 2 fils, l'ohmmètre aurait lu 0,4 Ω.",
        )
    ):
        b += text(480, 306 + 17 * i, line, "mut", 12)
    b += text(466, 420, "Puissance dissipée : P = R × I² = 0,1 W.", "fg", 12)
    b += text(466, 438, "Rester sous la puissance de la pièce,", "mut", 12)
    b += text(466, 454, "couper la sortie avant de déplacer une pince.", "mut", 12)
    return svg(
        760,
        648,
        "Mesure 4 fils d'une résistance de faible valeur avec une alimentation limitée et un voltmètre",
        "Une alimentation de laboratoire en limitation de courant, voyant CC allumé, affiche 0,35 V et 1,000 A ; ses deux pinces crocodile tiennent les extrémités des pattes d'une résistance de 0,1 Ω, 5 W. "
        "Un multimètre, sélecteur sur volts continus, a ses deux pointes sur les pattes, entre les pinces et au ras du corps, pointe rouge du côté de la pince positive ; il lit 0,100 V. "
        "La résistance vaut la tension divisée par le courant : 0,100 V divisé par 1,000 A, soit 0,100 Ω. "
        "Le courant passe par les pinces, le voltmètre ne prélève presque rien : la résistance des cordons et des contacts ne fausse pas la mesure. "
        "En deux fils, l'ohmmètre aurait lu 0,4 Ω.",
        b,
    )


FIGURES = {
    "lire-la-valeur": (fig_read, []),
    "indices-visuels": (fig_clues, []),
    "mesure-hors-circuit": (fig_out, ["200", "2M"]),
    "mesure-en-circuit": (fig_in, ["200k"]),
    "chute-de-tension": (fig_drop, ["VDC"]),
    "kelvin-4-fils": (fig_kelvin, ["VDC"]),
}
