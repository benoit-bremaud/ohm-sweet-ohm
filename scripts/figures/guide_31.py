"""Figures of guide 31, the common-mode choke."""

from __future__ import annotations

from elements import (
    four_pad,
    half_meter,
    heading,
    hookup,
    svg,
    text,
    verdict,
    winding,
)


def _arrow(x: float, y1: float, y2: float, cls: str) -> str:
    """Vertical current arrow at `x` from y1 to y2 (head at y2), in theme stroke class `cls`."""
    d = 1 if y2 > y1 else -1
    return (
        f'  <g data-arrow="{"down" if d > 0 else "up"}">\n'
        f'  <path class="{cls}" fill="none" stroke-width="3" stroke-linecap="round" '
        f'd="M{x} {y1} V{y2 - 4 * d} M{x - 6} {y2 - 10 * d} L{x} {y2} L{x + 6} {y2 - 10 * d}"/>\n'
        "  </g>\n"
    )


def _symbol(cx: float, top: float, dots: bool = True) -> str:
    """Schematic symbol: two windings on one core, a dot at the same end of each."""
    o = winding(cx - 26, top, top + 80, 4, right=False)
    o += winding(cx + 26, top, top + 80, 4)
    o += f'  <path class="blk" stroke-width="2" d="M{cx - 4} {top} V{top + 80} M{cx + 4} {top} V{top + 80}"/>\n'
    o += f'  <path class="wire" d="M{cx - 26} {top - 26} V{top} M{cx - 26} {top + 80} V{top + 106} M{cx + 26} {top - 26} V{top} M{cx + 26} {top + 80} V{top + 106}"/>\n'
    if dots:
        for x in (cx - 46, cx + 46):
            o += f'  <circle class="blkf" cx="{x}" cy="{top + 4}" r="4"/>\n'
    return o


# ---------------------------------------------------------------- figure 1
def fig_structure() -> str:
    b = heading(
        "Self de mode commun : deux bobinages sur un même noyau",
        "Elle laisse passer le courant utile et freine les parasites communs aux deux fils",
    )
    for cx, title in ((130, "Le symbole"), (380, "Courant utile"), (630, "Parasites")):
        b += text(cx, 100, title, size=15, weight=700, anchor="middle")
        b += _symbol(cx, 160)
    b += text(130, 296, "deux bobinages, un noyau,", "mut", 12, "middle")
    b += text(130, 313, "un point du même côté", "mut", 12, "middle")
    b += _arrow(322, 150, 250, "fb") + _arrow(438, 250, 150, "fb")
    b += text(380, 296, "aller par un fil, retour par l'autre :", "mut", 12, "middle")
    b += text(380, 313, "les champs s'annulent", "mut", 12, "middle")
    b += verdict(
        380, 348, "✓ Passe librement", "la self se comporte comme deux fils", "ok"
    )
    b += _arrow(572, 150, 250, "fr") + _arrow(688, 150, 250, "fr")
    b += text(630, 296, "même sens dans les deux fils :", "mut", 12, "middle")
    b += text(630, 313, "les champs s'ajoutent", "mut", 12, "middle")
    b += verdict(630, 348, "✗ Freinés", "la self oppose une forte impédance", "no")
    b += text(
        380,
        404,
        "En continu, chaque bobinage n'est qu'un fil : c'est ce que l'ohmmètre contrôle.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        424,
        "Principe d'une self de mode commun",
        "Trois schémas d'une self de mode commun : deux bobinages côte à côte sur un même noyau, avec un point du même côté de chaque bobinage. "
        "Au centre, le courant utile va par un fil et revient par l'autre : les champs magnétiques s'annulent et le courant passe librement, comme dans deux fils. "
        "À droite, les parasites circulent dans le même sens dans les deux fils : les champs s'ajoutent et la self leur oppose une forte impédance. "
        "En continu, chaque bobinage n'est qu'un fil : c'est ce que l'ohmmètre contrôle.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def fig_windings() -> str:
    b = heading(
        "Deux contrôles à l'ohmmètre, self dessoudée",
        "Chaque bobinage doit conduire, et les deux bobinages doivent rester isolés l'un de l'autre",
    )
    b += '  <path class="grid" d="M380 84 V504"/>\n'
    for x0, sel, lcd, unit, title, notes, ends, head, sub in (
        (
            0,
            "200",
            "0.3",
            "Ω",
            "Le long d'un bobinage",
            ("les deux plots", "du même bobinage"),
            ("a1", "a2"),
            "✓ Faible résistance : bobinage continu",
            "OL : bobinage coupé. Refaire sur l'autre bobinage",
        ),
        (
            380,
            "2M",
            "OL",
            "MΩ",
            "Entre les deux bobinages",
            ("un plot de chaque", "bobinage"),
            ("a1", "b2"),
            "✓ OL : bobinages isolés",
            "toute autre lecture : isolant détruit",
        ),
    ):
        o, v, com = half_meter(x0, sel, lcd, unit, title, notes)
        part, pads = four_pad(x0 + 290, 250)
        b += o + part + hookup(v, com, pads[ends[0]], pads[ends[1]])
        b += verdict(x0 + 190, 478, head, sub, "ok")
    b += text(
        380,
        528,
        "Le brochage varie d'un modèle à l'autre : repérer d'abord à l'ohmmètre les deux plots de chaque bobinage.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        546,
        "Contrôler une self de mode commun à l'ohmmètre",
        "Deux mesures côte à côte sur une self de mode commun CMS à quatre plots, dessoudée. "
        "À gauche, multimètre sur le calibre 200 ohms, une pointe sur chaque plot du même bobinage : 0,3 ohm, le bobinage est continu ; OL signifierait un bobinage coupé. La mesure se refait sur l'autre bobinage. "
        "À droite, multimètre sur le calibre 2 mégohms, une pointe sur un plot de chaque bobinage : OL, les deux bobinages sont isolés ; toute autre lecture signifierait un isolant détruit. "
        "Le brochage varie d'un modèle à l'autre : repérer d'abord à l'ohmmètre les deux plots de chaque bobinage.",
        b,
    )


FIGURES = {
    "principe": (fig_structure, []),
    "controle-a-l-ohmmetre": (fig_windings, ["200", "2M"]),
}
