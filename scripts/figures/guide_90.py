"""Figures of guide 90, visual inspection of a board (checking a cracked solder joint)."""

from __future__ import annotations

from elements import heading, lead, meter, probe, res_h, svg, text

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


FIGURES = {
    "joint-fissure": (fig_cracked_joint, ["20k", "BEEP"]),
}
