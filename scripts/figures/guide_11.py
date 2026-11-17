"""Figures of guide 11, the potentiometer."""

from __future__ import annotations

import math

from elements import MONO, Point, lead, meter, probe, svg, text

TRACK_END = 150  # the track runs from -150° to +150°, clockwise from the top


def _heading(title: str, subtitle: str) -> str:
    return text(24, 38, title, size=20, weight=700) + text(24, 60, subtitle, "mut", 14)


def _pot(
    cx: float, cy: float, r: float, turn: float
) -> tuple[str, tuple[Point, Point, Point]]:
    """See-through rotary potentiometer seen from the shaft side, wiper at `turn` (0 to 1).

    0 puts the wiper on the track end of terminal 1, 1 on the end of terminal 3.
    Each terminal lug carries its number. Returns (svg, lug ends 1, 2 (wiper), 3).
    """
    rt = 0.68 * r

    def pt(a: float, rr: float) -> Point:
        return cx + rr * math.sin(math.radians(a)), cy - rr * math.cos(math.radians(a))

    ty = cy + 1.45 * r
    t1, t2, t3 = (cx - 0.55 * r, ty), (cx, ty), (cx + 0.55 * r, ty)
    (ax, ay), (bx, by) = pt(-TRACK_END, rt), pt(TRACK_END, rt)
    wx, wy = pt(-TRACK_END + 2 * TRACK_END * turn, rt)
    lug = 0.27 * r
    o = ""
    for i, (x, _) in enumerate((t1, t2, t3), start=1):
        o += f'  <rect x="{x - lug / 2:.1f}" y="{cy + 0.8 * r:.1f}" width="{lug:.1f}" height="{0.75 * r:.1f}" rx="2" fill="#c9d0d9" stroke="#7d8794"/>\n'
        o += f'  <text x="{x:.1f}" y="{cy + 1.24 * r:.1f}" font-size="{max(11, 0.2 * r):.1f}" font-weight="700" text-anchor="middle" fill="#1f2933">{i}</text>\n'
    o += f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="#e7dcc8" stroke="#8a6d45" stroke-width="2"/>\n'
    # links from the track ends and from the wiper hub to their terminals
    o += (
        f'  <path d="M{ax:.1f} {ay:.1f} L{t1[0]:.1f} {cy + 0.9 * r:.1f} M{bx:.1f} {by:.1f} L{t3[0]:.1f} {cy + 0.9 * r:.1f}'
        f' M{cx} {cy} V{cy + 0.9 * r:.1f}" stroke="#7d8794" stroke-width="{0.07 * r:.1f}" fill="none" stroke-linecap="round"/>\n'
    )
    o += f'  <path d="M{ax:.1f} {ay:.1f} A{rt:.1f} {rt:.1f} 0 1 1 {bx:.1f} {by:.1f}" stroke="#2a2522" stroke-width="{0.17 * r:.1f}" fill="none"/>\n'
    o += f'  <path d="M{cx} {cy} L{wx:.1f} {wy:.1f}" stroke="#2563eb" stroke-width="{0.09 * r:.1f}" stroke-linecap="round"/>\n'
    o += f'  <circle cx="{wx:.1f}" cy="{wy:.1f}" r="{0.1 * r:.1f}" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"/>\n'
    o += f'  <circle cx="{cx}" cy="{cy}" r="{0.2 * r:.1f}" fill="#aab2bd" stroke="#5f6b7a" stroke-width="1.5"/>\n'
    return o, (t1, t2, t3)


# ---------------------------------------------------------------- figure 1
def fig_identify() -> str:
    b = _heading(
        "Trois bornes : deux bouts de piste et un curseur",
        "Potentiomètre vu côté axe, capot retiré : le curseur glisse sur la piste résistive",
    )
    b += '  <path class="grid" d="M410 84 V430"/>\n'
    p, terminals = _pot(250, 205, 84, 0.3)
    b += p
    b += text(250, 104, "piste résistive (carbone ou cermet)", "mut", 12, "middle")
    b += text(24, 180, "curseur", "blue", 13, weight=700)
    b += text(24, 196, "(contact mobile)", "blue", 12)
    (x1, y), (x2, _), (x3, _) = terminals
    b += text(x1 - 16, y + 20, "bout de piste", "mut", 12, "end")
    b += text(x2, y + 20, "curseur", "blue", 12, "middle", 700)
    b += text(x3 + 16, y + 20, "bout de piste", "mut", 12)
    b += text(24, 386, "Entre 1 et 3 : la résistance totale, fixe.", size=13)
    b += text(24, 406, "Entre 2 et 1, entre 2 et 3 : varient avec l'axe,", size=13)
    b += text(24, 424, "leur somme fait le total.", size=13)
    b += text(430, 100, "Lire le marquage", size=15, weight=700)
    for i, (marking, value, how) in enumerate(
        (
            ("B10K", "10 kΩ, loi linéaire", "lettre : loi de variation"),
            ("A50K", "50 kΩ, loi logarithmique", "réglage de volume"),
            ("103", "10 × 10³ = 10 kΩ", "ajustable : code à 3 chiffres"),
            ("W103", "10 kΩ, multitour", "25 tours de vis, sans butée franche"),
        )
    ):
        y = 124 + 62 * i
        b += f'  <rect x="430" y="{y}" width="76" height="34" rx="5" fill="#20242b" stroke="#7d8794"/>\n'
        b += f'  <text x="468" y="{y + 23}" font-size="17" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#ffffff">{marking}</text>\n'
        b += text(520, y + 14, value, "blue", 13, weight=700)
        b += text(520, y + 31, how, "mut", 12)
    b += text(
        430, 388, "A et B ont changé de sens selon l'époque", "warn", 12, weight=700
    )
    b += text(430, 404, "et l'origine : vérifier à mi-course,", "warn", 12, weight=700)
    b += text(430, 420, "linéaire = la moitié du total.", "warn", 12, weight=700)
    return svg(
        760,
        446,
        "Bornes et marquage d'un potentiomètre",
        "À gauche, un potentiomètre rotatif vu côté axe, capot retiré : une piste résistive en arc relie la borne 1 à la borne 3, "
        "et un curseur, contact mobile porté par l'axe et relié à la borne 2 du milieu, glisse sur cette piste. "
        "Entre les bornes 1 et 3 se lit la résistance totale, fixe ; entre la borne 2 et chacune des deux autres, une résistance qui varie avec l'axe et dont la somme fait le total. "
        "À droite, quatre marquages : B10K, 10 kΩ à loi linéaire ; A50K, 50 kΩ à loi logarithmique pour un réglage de volume ; "
        "103, ajustable de 10 kΩ ; W103, ajustable multitour de 10 kΩ, 25 tours de vis sans butée franche. "
        "Les lettres A et B ont changé de sens selon l'époque et l'origine : vérifier à mi-course, un modèle linéaire y lit la moitié du total.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def fig_track() -> str:
    b = _heading(
        "Hors tension : d'abord la piste, entre les bornes 1 et 3",
        "Sélecteur sur Ω, calibre 20 kΩ : potentiomètre marqué B10K, l'appareil lit 9,62 kΩ",
    )
    m, (_, com, v) = meter(30, 80, 1, "20k", "9.62", "kΩ")
    b += m
    p, terminals = _pot(450, 196, 72, 0.3)
    b += p
    (x1, y), _, (x3, _) = terminals
    pr, (ex, ey) = probe(x1 - 4, y - 8, -0.9, 0.45, True)
    b += lead(v, f"V394 C{v[0]:.1f} 426 {ex - 60:.1f} 420 {ex:.1f} {ey:.1f}", True) + pr
    pr, (ex, ey) = probe(x3 + 4, y - 8, 0.9, 0.45, False)
    b += (
        lead(
            com,
            f"V398 C{com[0]:.1f} 452 {ex + 30:.1f} 462 {ex:.1f} {ey:.1f}",
            False,
        )
        + pr
    )
    b += text(566, 136, "Lecture stabilisée", size=14, weight=700)
    for i, (cls, head, sub) in enumerate(
        (
            ("ok", "✓ 8 à 12 kΩ", "piste entière (± 20 %)"),
            ("no", "✗ OL", "piste ou borne coupée"),
            ("no", "✗ bien au-dessus", "piste brûlée ou usée"),
        )
    ):
        yy = 164 + 44 * i
        b += text(566, yy, head, cls, 13, weight=700)
        b += text(566, yy + 17, sub, "mut", 12)
    b += text(
        24, 478, "Tourner l'axe ne doit pas changer cette lecture.", size=13, weight=700
    )
    b += text(
        24,
        498,
        "Carte hors tension et déchargée ; en circuit, les chemins parallèles ne peuvent que faire baisser la lecture (fiche 02).",
        "mut",
        12,
    )
    return svg(
        760,
        516,
        "Mesure de la résistance totale d'un potentiomètre entre ses bornes extrêmes",
        "Un multimètre, sélecteur sur ohms calibre 20 kΩ, a une pointe sur la borne 1 et l'autre sur la borne 3 d'un potentiomètre marqué B10K ; il lit 9,62 kΩ. "
        "De 8 à 12 kΩ, soit la tolérance de 20 %, la piste est entière. OL : piste ou borne coupée. Bien au-dessus de 12 kΩ : piste brûlée ou usée. "
        "Tourner l'axe ne doit pas changer cette lecture.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def _sweep(x: float, y: float, w: float, h: float, dropouts: bool) -> str:
    """Small chart of the reading against the shaft rotation."""
    o = f'  <path class="wire" stroke-width="1.5" d="M{x} {y} V{y + h} H{x + w}"/>\n'
    pts = [(x + 6, y + h - 4), (x + w - 6, y + 6)]
    if dropouts:
        (x0, y0), (x1, y1) = pts
        pts = [(x0, y0)]
        for f in (0.38, 0.62):
            px, py = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
            pts += [(px - 5, py + 1.5), (px - 3, y + 2), (px + 3, y + 2), (px + 5, py)]
        pts.append((x1, y1))
    d = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    colour = "#dc2626" if dropouts else "#16a34a"
    o += f'  <polyline points="{d}" fill="none" stroke="{colour}" stroke-width="2.5" stroke-linejoin="round"/>\n'
    o += text(x - 6, y + 8, "Ω", "mut", 11, "end")
    o += text(x + w, y + h + 15, "rotation de l'axe →", "mut", 11, "end")
    return o


def fig_wiper() -> str:
    b = _heading(
        "Hors tension : ensuite le curseur, entre les bornes 1 et 2",
        "Sélecteur sur Ω, calibre 20 kΩ ; tourner l'axe lentement d'une butée à l'autre en regardant l'afficheur",
    )
    b += '  <path class="grid" d="M380 84 V600"/>\n'

    def half(x0, title, lcd, turn, notes, dropouts, cls, verdict) -> str:
        o = text(x0 + 20, 100, title, size=15, weight=700)
        m, (_, com, v) = meter(x0 + 24, 116, 0.9, "20k", lcd, "kΩ")
        o += m
        for i, line in enumerate(notes):
            o += text(x0 + 205, 132 + 16 * i, line, "mut", 12)
        p, terminals = _pot(x0 + 282, 240, 52, turn)
        o += p
        (x1, y), (x2, _), _ = terminals
        # red lead inside, black lead outside: the cables do not cross
        pr, (ex, ey) = probe(x1 - 3, y - 6, -0.8, 0.6, True)
        o += (
            lead(
                v,
                f"V400 C{v[0]:.1f} 436 {ex:.1f} 446 {ex:.1f} 410 L{ex:.1f} {ey:.1f}",
                True,
            )
            + pr
        )
        pr, (ex, ey) = probe(x2, y - 3, 0.1, 1, False)
        o += (
            lead(
                com,
                f"V404 C{com[0]:.1f} 470 {ex:.1f} 482 {ex:.1f} 410 L{ex:.1f} {ey:.1f}",
                False,
            )
            + pr
        )
        o += _sweep(x0 + 60, 492, 280, 48, dropouts)
        o += text(x0 + 190, 578, verdict[0], cls, 14, "middle", 700)
        o += text(x0 + 190, 596, verdict[1], "mut", 12, "middle")
        return o

    b += half(
        0,
        "Curseur sain : la lecture glisse",
        "4.87",
        0.5,
        ("La lecture suit l'axe,", "sans saut ni retour", "en arrière."),
        False,
        "ok",
        ("✓ de 0 à 10 kΩ sans à-coup", "puis même essai entre les bornes 2 et 3"),
    )
    b += half(
        380,
        "Curseur usé : la lecture saute",
        "OL",
        0.62,
        ("Sauts, passages à OL,", "valeurs qui dansent", "à certains endroits."),
        True,
        "no",
        ("✗ coupures en tournant", "piste usée ou encrassée : nettoyer ou remplacer"),
    )
    return svg(
        760,
        612,
        "Mesure du curseur d'un potentiomètre en tournant l'axe",
        "Deux multimètres, sélecteur sur ohms calibre 20 kΩ, ont une pointe sur la borne 1 et l'autre sur la borne 2, le curseur, d'un potentiomètre de 10 kΩ dont on tourne l'axe lentement. "
        "À gauche, curseur sain : l'appareil lit 4,87 kΩ à mi-course et la lecture monte de 0 à 10 kΩ sans à-coup, comme le montre la courbe régulière de la lecture en fonction de la rotation ; refaire l'essai entre les bornes 2 et 3. "
        "À droite, curseur usé : l'appareil passe à OL à certains endroits de la course, la courbe montre deux coupures ; la piste est usée ou encrassée, il faut nettoyer ou remplacer.",
        b,
    )


FIGURES = {
    "bornes-et-marquage": (fig_identify, []),
    "mesure-de-la-piste": (fig_track, ["20k"]),
    "mesure-du-curseur": (fig_wiper, ["20k", "20k"]),
}
