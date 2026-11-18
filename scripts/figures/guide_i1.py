"""Figures of page i1, the multimeter presented as an instrument (anatomy, fuse check)."""

from __future__ import annotations

from elements import (
    Point,
    heading,
    lead,
    meter,
    probe,
    svg,
    text,
    verdict,
)


def _callout(
    px: float, py: float, tx: float, ty: float, head: str, sub: str, left: bool
) -> str:
    """Leader line from the part at (px, py) to a label at (tx, ty), right-aligned if `left`."""
    end = tx + 8 if left else tx - 8
    anchor = "end" if left else "start"
    return (
        f'  <path class="wire" stroke-width="1.5" d="M{px:.1f} {py:.1f} L{end:.1f} {ty - 5:.1f}"/>\n'
        f'  <circle class="blkf" cx="{px:.1f}" cy="{py:.1f}" r="3"/>\n'
        + text(tx, ty, head, size=14, anchor=anchor, weight=700)
        + text(tx, ty + 17, sub, "mut", 12, anchor)
    )


# ---------------------------------------------------------------- figure 1
def fig_anatomy() -> str:
    b = heading(
        "Anatomie d'un multimètre de poche",
        "Six organes à connaître avant la première mesure ; les modes eux-mêmes sont expliqués fiche 01",
    )
    x, y, s = 272, 90, 1.2
    m, jacks = meter(x, y, s, "VDC", "12.47", "V")
    b += m

    def at(mx: float, my: float) -> Point:
        return x + mx * s, y + my * s

    # the selected position, ringed by a slow dotted halo (still under prefers-reduced-motion)
    sx, sy = at(90, 165)
    b += f'  <circle class="flow fa" cx="{sx:.1f}" cy="{sy:.1f}" r="{78 * s:.1f}"/>\n'
    # leads parked below the meter, probes pointing outwards
    pr, (ex, ey) = probe(640, 560, -0.8, -0.6, True)
    b += lead(
        jacks.v, f"V520 C{jacks.v[0]:.1f} 560 {ex:.1f} 520 {ex:.1f} {ey:.1f}", True
    )
    b += pr
    pb, (ex, ey) = probe(140, 560, 0.8, -0.6, False)
    b += lead(
        jacks.com, f"V530 C{jacks.com[0]:.1f} 570 {ex:.1f} 520 {ex:.1f} {ey:.1f}", False
    )
    b += pb
    left, right = 238, 540
    b += _callout(
        *at(30, 50), left, 130, "1 Afficheur", "chiffres, unité, symboles", True
    )
    b += _callout(*at(24, 89), left, 190, "2 Touches", "HOLD fige, LIGHT éclaire", True)
    b += _callout(*at(40, 150), left, 260, "3 Sélecteur", "fonction et calibre", True)
    b += _callout(*at(45, 283), left, 380, "4 Douille 10 A", "courant seulement", True)
    b += _callout(
        *at(135, 283),
        right,
        380,
        "4 Douille VΩ",
        "cordon rouge ; le noir en COM",
        False,
    )
    b += _callout(
        *at(170, 60),
        right,
        130,
        "5 Fusibles et pile",
        "derrière le capot arrière",
        False,
    )
    b += _callout(
        *at(135, 342),
        right,
        470,
        "6 Cordons et pointes",
        "garde-doigts, catégorie CAT",
        False,
    )
    return svg(
        760,
        600,
        "Anatomie d'un multimètre de poche",
        "Multimètre jaune, sélecteur sur la tension continue entouré d'un halo pointillé, "
        "afficheur 12,47 V. Repères : 1 afficheur, 2 touches HOLD et LIGHT, 3 sélecteur, "
        "4 douilles 10 A, COM et VΩ, 5 fusibles et pile derrière le capot, "
        "6 cordons rouge et noir terminés par des pointes avec garde-doigts.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def fig_fuse() -> str:
    b = heading(
        "Contrôler le fusible de la douille 10 A sans ouvrir l'appareil",
        "Ohmmètre, cordon rouge en VΩ, sa pointe enfoncée dans la douille 10 A ; cordon noir en COM, sans contact",
    )
    b += '  <path class="grid" d="M380 84 V470"/>\n'
    for x0, lcd, title, notes, cls, head, sub in (
        (
            0,
            "0.3",
            "Chemin fermé",
            ("Quelques dixièmes", "d'ohm : shunt,", "fusible, cordon."),
            "ok",
            "✓ valeur basse",
            "fusible bon, s'il existe : voir le manuel",
        ),
        (
            380,
            "OL",
            "Fusible fondu",
            ("OL : le chemin", "est ouvert, mode", "courant hors service."),
            "no",
            "✗ OL",
            "remplacer par le calibre exact du manuel",
        ),
    ):
        b += text(x0 + 20, 100, title, size=15, weight=700)
        m, jacks = meter(x0 + 24, 116, 0.9, "200", lcd, "Ω")
        b += m
        for i, line in enumerate(notes):
            b += text(x0 + 205, 132 + 16 * i, line, "mut", 12)
        # red probe goes back into the meter's own 10 A jack; its lead loops under the
        # parked black probe, so the two leads never cross
        pr, (ex, ey) = probe(jacks.a[0], jacks.a[1] + 4, 0, 1, True)
        b += lead(jacks.v, f"V490 H{ex:.1f} V{ey:.1f}", True)
        b += pr
        pb, (bx, by) = probe(jacks.com[0], 470, 0, -1, False)
        b += lead(jacks.com, f"V{by:.1f}", False)
        b += pb
        b += verdict(x0 + 190, 530, head, sub, cls)
    return svg(
        760,
        570,
        "Contrôler le fusible de la douille 10 A",
        "Deux multimètres sur le calibre 200 ohms, cordon rouge branché en VΩ et sa pointe "
        "enfoncée dans la douille 10 A du même appareil, cordon noir en COM, pointe en l'air. À gauche 0,3 ohm : chemin fermé. "
        "À droite OL : fusible fondu, le mode courant ne mesure plus rien.",
        b,
    )


# Figure name -> (function, expected multimeter dial positions)
FIGURES = {
    "anatomie": (fig_anatomy, ["VDC"]),
    "controle-fusible": (fig_fuse, ["200", "200"]),
}
