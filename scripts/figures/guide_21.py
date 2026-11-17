"""Figures of guide 21, the film capacitor."""

from __future__ import annotations

from elements import MONO, Point, half_meter, heading, hookup, svg, text, tile, verdict

RED = "#dc2626"
METAL = "#9aa3ad"
FILM = "#bfdbfe"


def _box_cap(
    cx: float, top: float, lines: tuple[str, ...], w: float = 110, h: float = 60
) -> tuple[str, Point, Point]:
    """Box film capacitor, body centred on cx, its two leads pointing down.

    Returns (svg, a point on the left lead, a point on the right lead).
    """
    xl, xr, foot = cx - w * 0.3, cx + w * 0.3, top + h + 50
    o = f'  <path d="M{xl:.1f} {top + h} V{foot} M{xr:.1f} {top + h} V{foot}" stroke="{METAL}" stroke-width="3" stroke-linecap="round"/>\n'
    o += f'  <rect x="{cx - w / 2}" y="{top}" width="{w}" height="{h}" rx="5" fill="#b91c1c" stroke="#7f1d1d" stroke-width="1.5"/>\n'
    for i, line in enumerate(lines):
        y = top + h / 2 + 5 + 18 * (i - (len(lines) - 1) / 2)
        o += f'  <text x="{cx}" y="{y:.1f}" font-size="14" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#ffffff">{line}</text>\n'
    return o, (xl, top + h + 40), (xr, top + h + 40)


# ---------------------------------------------------------------- figure 1
def _bodies() -> str:
    """Three common film capacitor packages with their marking styles."""
    o, _, _ = _box_cap(130, 118, ("0,47 µF J", "100 V-"), 124)
    o += text(130, 248, "boîtier rectangulaire : valeur en clair", "mut", 12, "middle")
    # dipped
    o += f'  <path d="M362 176 V228 M398 176 V228" stroke="{METAL}" stroke-width="3" stroke-linecap="round"/>\n'
    o += '  <rect x="326" y="118" width="108" height="62" rx="26" fill="#15803d" stroke="#14532d" stroke-width="1.5"/>\n'
    o += f'  <text x="380" y="154" font-size="14" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#ffffff">474J 100V</text>\n'
    o += text(380, 248, "enrobé : code à trois chiffres", "mut", 12, "middle")
    # axial
    o += f'  <path d="M548 149 H712" stroke="{METAL}" stroke-width="3" stroke-linecap="round"/>\n'
    o += '  <rect x="574" y="126" width="112" height="46" rx="8" fill="#eab308" stroke="#a16207" stroke-width="1.5"/>\n'
    o += f'  <text x="630" y="154" font-size="14" font-weight="700" text-anchor="middle" font-family="{MONO}" fill="#1f2933">47n 63V</text>\n'
    o += text(630, 248, "axial : notation avec lettre", "mut", 12, "middle")
    return o


def fig_marking() -> str:
    b = heading(
        "Lire un condensateur film : trois façons d'écrire la même chose",
        "Aucune polarité : il se monte dans les deux sens. La tension marquée est la tension maximale de service",
    )
    b += text(24, 100, "Trois présentations courantes", size=15, weight=700)
    b += _bodies()
    b += '  <path class="grid" d="M24 266 H736"/>\n'
    b += text(
        24,
        296,
        "Décoder 474J : comme un céramique, en picofarads",
        size=15,
        weight=700,
    )
    for i, (code, head, sub) in enumerate(
        (
            ("47", "deux chiffres significatifs", "ici 47"),
            ("4", "nombre de zéros", "ici 0000, en picofarads"),
            ("J", "tolérance ±5 %", "K : ±10 %, M : ±20 %"),
        )
    ):
        b += tile(24 + 240 * i, 314, code, head, sub)
    b += text(
        24,
        420,
        "474 : 47 suivi de 4 zéros = 470 000 pF = 470 nF = 0,47 µF",
        size=14,
        weight=700,
    )
    for i, line in enumerate(
        (
            "Notation avec lettre : la lettre remplace la virgule, qui s'efface trop facilement. n47 = 0,47 nF ; 4n7 = 4,7 nF ; 47n = 47 nF.",
            "Tension : en volts continus, sauf si elle est suivie du signe ~ ou de « AC » (tension alternative).",
        )
    ):
        b += text(24, 442 + 18 * i, line, "mut", 12)
    return svg(
        760,
        480,
        "Lire le marquage d'un condensateur film",
        "En haut, trois présentations courantes du condensateur film, toutes sans polarité : un boîtier rectangulaire rouge marqué en clair 0,47 µF J 100 V ; un modèle enrobé vert marqué du code 474J 100V ; un modèle axial jaune marqué 47n 63V. "
        "En bas, le décodage de 474J : les deux premiers chiffres, 47, sont les chiffres significatifs ; le troisième, 4, est le nombre de zéros, en picofarads ; la lettre J donne la tolérance, ±5 % (K : ±10 %, M : ±20 %). "
        "474 se lit donc 47 suivi de 4 zéros, soit 470 000 pF, 470 nF ou 0,47 µF. "
        "Dans la notation avec lettre, la lettre remplace la virgule, qui s'efface trop facilement : n47 vaut 0,47 nF, 4n7 vaut 4,7 nF et 47n vaut 47 nF. "
        "La tension est donnée en volts continus, sauf si elle est suivie du signe tilde ou de la mention AC, qui indiquent une tension alternative.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def fig_capacitance() -> str:
    b = heading(
        "Hors circuit : le capacimètre donne le verdict",
        "Sélecteur sur le capacimètre, condensateur déchargé, une patte dessoudée, une pointe sur chaque patte",
    )
    b += '  <path class="grid" d="M380 84 V504"/>\n'
    for x0, lcd, title, notes, cls, head, sub in (
        (
            0,
            "468",
            "Sain : dans la tolérance",
            ("474J : 470 nF ±5 %,", "soit de 447 à 493 nF."),
            "ok",
            "✓ 468 nF : dans la tolérance",
            "un film sain reste sur sa valeur pendant des décennies",
        ),
        (
            380,
            "310",
            "Usé : capacité perdue",
            ("Un tiers de moins", "que le marquage."),
            "no",
            "✗ 310 nF : hors tolérance, à remplacer",
            "aucun signe visible : seule la mesure le montre",
        ),
    ):
        o, v, com = half_meter(x0, "CAP", lcd, "nF", title, notes)
        cap, left, right = _box_cap(x0 + 290, 196, ("474J", "100 V-"))
        b += o + cap + hookup(v, com, left, right)
        b += verdict(x0 + 190, 478, head, sub, cls)
    b += text(
        380,
        528,
        "Sens des pointes indifférent : un film n'a pas de polarité. En circuit, le capacimètre additionne tout ce qui est en parallèle.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        546,
        "Mesure d'un condensateur film au capacimètre",
        "Deux multimètres, sélecteur sur le capacimètre, mesurent un condensateur film marqué 474J 100 V, hors circuit, déchargé, une pointe sur chaque patte. Le marquage 474J annonce 470 nF à ±5 %, soit de 447 à 493 nF. "
        "À gauche, condensateur sain : l'appareil lit 468 nF, dans la tolérance ; un film sain reste sur sa valeur pendant des décennies. "
        "À droite, condensateur usé : l'appareil lit 310 nF, un tiers de moins que le marquage, hors tolérance ; il est à remplacer, alors qu'aucun signe n'est visible. "
        "Le sens des pointes est indifférent, un film n'a pas de polarité. En circuit, le capacimètre additionne tout ce qui est en parallèle.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def _layers(y: float, gap: bool) -> str:
    """Cross-section of a metallised film: metal, film, metal; `gap` clears the metal around x = 100."""
    o = f'  <rect x="30" y="{y + 15}" width="140" height="22" fill="{FILM}" stroke="#3f6f96"/>\n'
    for my in (y + 9, y + 37):
        if gap:
            o += f'  <rect x="30" y="{my}" width="52" height="6" fill="{METAL}"/><rect x="118" y="{my}" width="52" height="6" fill="{METAL}"/>\n'
        else:
            o += f'  <rect x="30" y="{my}" width="140" height="6" fill="{METAL}"/>\n'
    return o


def _healing() -> str:
    """Three steps of self-healing, from the weak spot to the cleared fault."""
    o = text(20, 100, "Film métallisé : le défaut se soigne seul", size=15, weight=700)
    steps = (
        (
            "1. Un point faible claque",
            ("Sous la tension, une étincelle", "traverse le film à cet endroit."),
        ),
        (
            "2. Le métal s'évapore autour",
            ("L'armature, très mince, disparaît", "tout autour de l'étincelle."),
        ),
        (
            "3. Le défaut est isolé",
            ("Plus de court-circuit, mais un", "peu d'armature en moins."),
        ),
    )
    for i, (head, lines) in enumerate(steps):
        y = 124 + 96 * i
        o += _layers(y, gap=i > 0)
        if i < 2:
            o += f'  <path d="M100 {y + 9} L95 {y + 20} L105 {y + 27} L100 {y + 43}" stroke="{RED}" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>\n'
        else:
            o += f'  <circle cx="100" cy="{y + 26}" r="3" fill="#3f6f96"/>\n'
        o += text(190, y + 16, head, "no" if i < 2 else "ok", 13, weight=700)
        o += text(190, y + 34, lines[0], "mut", 12)
        o += text(190, y + 50, lines[1], "mut", 12)
    o += text(30, 420, "métal (armatures)", "mut", 11)
    o += f'  <rect x="134" y="411" width="14" height="6" fill="{METAL}"/>\n'
    o += text(30, 438, "film plastique (isolant)", "mut", 11)
    o += f'  <rect x="160" y="428" width="14" height="10" fill="{FILM}" stroke="#3f6f96"/>\n'
    return o


def _foil(x: float, holes: int) -> str:
    """Top view of one metallised electrode, with `holes` cleared spots."""
    o = f'  <rect x="{x}" y="124" width="150" height="96" rx="3" fill="{METAL}" stroke="#5f6b7a"/>\n'
    seed = 7
    for _ in range(holes):
        seed = (seed * 73 + 41) % 997
        hx = x + 10 + seed % 131
        seed = (seed * 73 + 41) % 997
        hy = 132 + seed % 81
        o += f'  <circle class="bg" cx="{hx}" cy="{hy}" r="{3 + seed % 3}"/>\n'
    return o


def _wear() -> str:
    o = text(400, 100, "À la longue : la capacité s'en va", size=15, weight=700)
    o += _foil(410, 0) + _foil(580, 48)
    o += text(485, 242, "neuf : 470 nF", "ok", 13, "middle", 700)
    o += text(655, 242, "usé : 310 nF", "no", 13, "middle", 700)
    o += text(485, 259, "armature intacte", "mut", 12, "middle")
    o += text(655, 259, "armature criblée de cicatrices", "mut", 12, "middle")
    for i, line in enumerate(
        (
            "Chaque cicatrice retire un peu de surface. Quelques",
            "milliers ne coûtent pas 1 % de capacité : il en faut",
            "bien plus pour arriver là, et rien ne se voit.",
        )
    ):
        o += text(400, 296 + 17 * i, line, size=12)
    o += '  <rect class="panel" x="400" y="352" width="336" height="88" rx="8"/>\n'
    o += text(414, 374, "Où cela arrive", "warn", 13, weight=700)
    for i, line in enumerate(
        (
            "Sur le secteur (classe X2, alimentation capacitive) :",
            "l'air ionisé multiplie les claquages, la perte devient",
            "forte en un ou deux ans. Hors périmètre de ces fiches.",
        )
    ):
        o += text(414, 393 + 16 * i, line, "mut", 12)
    return o


def fig_capacitance_loss() -> str:
    b = heading(
        "La panne type du film métallisé : la capacité qui baisse",
        "Le condensateur se répare lui-même à chaque claquage, mais y laisse un peu de son armature",
    )
    b += '  <path class="grid" d="M380 84 V444"/>\n'
    b += _healing() + _wear()
    return svg(
        760,
        460,
        "Auto-cicatrisation et perte de capacité d'un condensateur film métallisé",
        "À gauche, trois coupes d'un film métallisé, une couche de métal très mince de chaque côté d'un film plastique isolant. "
        "Étape 1 : un point faible du film claque, une étincelle le traverse sous la tension. "
        "Étape 2 : le métal de l'armature s'évapore tout autour de l'étincelle. "
        "Étape 3 : le défaut est isolé ; il n'y a plus de court-circuit, mais un peu d'armature en moins. "
        "À droite, deux armatures vues de dessus : celle d'un condensateur neuf, intacte, 470 nF ; celle d'un condensateur usé, criblée de cicatrices, 310 nF. "
        "Chaque cicatrice retire un peu de surface. Quelques milliers ne coûtent pas 1 % de capacité : il en faut bien plus pour arriver là, et rien ne se voit. "
        "Cela arrive sur le secteur (classe X2, alimentation capacitive) : l'air ionisé multiplie les claquages et la perte devient forte en un ou deux ans ; ce cas est hors périmètre de ces fiches.",
        b,
    )


FIGURES = {
    "lire-le-marquage": (fig_marking, []),
    "mesure-de-capacite": (fig_capacitance, ["CAP", "CAP"]),
    "perte-de-capacite": (fig_capacitance_loss, []),
}
