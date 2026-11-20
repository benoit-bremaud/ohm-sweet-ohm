"""Figures of guide 32, the low-voltage transformer."""

from __future__ import annotations

from elements import (
    box,
    four_pad,
    half_meter,
    heading,
    hookup,
    svg,
    text,
    verdict,
    winding,
)

RATIO = 2  # turns ratio of the example, primary to secondary
INJECTED = (
    1.0  # volts RMS on the winding with the most turns: the transformer steps down
)


def secondary_voltage(primary: float, ratio: float) -> float:
    """Voltage across the secondary for `primary` volts and a primary-to-secondary turns `ratio`."""
    if ratio <= 0:
        raise ValueError("a turns ratio is positive")
    return primary / ratio


def _lcd(volts: float) -> str:
    return f"{volts:.2f}"


def _fr(volts: float) -> str:
    return _lcd(volts).replace(".", ",")


def _symbol(cx: float, top: float, tap: bool = False) -> str:
    """Schematic symbol: primary on the left, core, secondary on the right, a dot on each."""
    o = winding(cx - 26, top, top + 80, 4, right=False)
    o += winding(cx + 26, top, top + 80, 4)
    o += f'  <path class="blk" stroke-width="2" d="M{cx - 4} {top} V{top + 80} M{cx + 4} {top} V{top + 80}"/>\n'
    for x, d in ((cx - 26, -1), (cx + 26, 1)):
        o += f'  <path class="wire" d="M{x} {top} H{x + 34 * d} M{x} {top + 80} H{x + 34 * d}"/>\n'
        o += f'  <circle class="blkf" cx="{x + 20 * d}" cy="{top - 10}" r="4"/>\n'
    if tap:
        o += f'  <g data-tap="centre">\n  <path class="wire" d="M{cx + 26} {top + 40} H{cx + 60}"/>\n  </g>\n'
    return o


# ---------------------------------------------------------------- figure 1
def fig_symbol() -> str:
    b = heading(
        "Transformateur : deux bobinages isolés sur un même noyau",
        "La tension suit le nombre de spires ; rien ne passe en continu d'un bobinage à l'autre",
    )
    out = _fr(secondary_voltage(INJECTED, RATIO))
    for cx, title, tap in (
        (130, "Le symbole", False),
        (380, f"Rapport {RATIO} : 1", False),
        (630, "Point milieu", True),
    ):
        b += text(cx, 100, title, size=15, weight=700, anchor="middle")
        b += _symbol(cx, 150, tap)
    b += text(88, 194, "primaire", "mut", 12, "end")
    b += text(172, 194, "secondaire", "mut", 12)
    b += text(130, 268, "les points marquent les extrémités", "mut", 12, "middle")
    b += text(130, 285, "de même polarité", "mut", 12, "middle")
    b += text(338, 195, f"{_fr(INJECTED)} V~", "blue", 14, "end", 700)
    b += text(422, 195, f"{out} V~", "blue", 14, weight=700)
    b += text(
        380, 268, f"{RATIO} fois moins de spires au secondaire :", "mut", 12, "middle"
    )
    b += text(380, 285, f"{RATIO} fois moins de tension", "mut", 12, "middle")
    b += text(696, 188, "point", "mut", 12)
    b += text(696, 203, "milieu", "mut", 12)
    b += text(630, 268, "une prise au milieu du bobinage :", "mut", 12, "middle")
    b += text(630, 285, "deux moitiés égales", "mut", 12, "middle")
    b += text(
        380,
        330,
        "Un transformateur ne transmet que l'alternatif : à l'ohmmètre, chaque bobinage n'est qu'un fil.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        352,
        "Symbole et rapport d'un transformateur",
        "Trois schémas d'un transformateur : un bobinage primaire à gauche, un noyau, un bobinage secondaire à droite. "
        "À gauche, le symbole : un point à une extrémité de chaque bobinage marque les extrémités de même polarité. "
        f"Au centre, un rapport {RATIO} pour 1 : {_fr(INJECTED)} volt alternatif au primaire donne {out} volt au secondaire, "
        f"car le secondaire compte {RATIO} fois moins de spires. "
        "À droite, un secondaire à point milieu : une prise au milieu du bobinage le partage en deux moitiés égales. "
        "Un transformateur ne transmet que l'alternatif : à l'ohmmètre, chaque bobinage n'est qu'un fil.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def fig_windings() -> str:
    b = heading(
        "Deux contrôles à l'ohmmètre, transformateur dessoudé",
        "Chaque bobinage doit conduire ; primaire (P) et secondaire (S) doivent rester isolés l'un de l'autre",
    )
    b += '  <path class="grid" d="M380 84 V504"/>\n'
    for x0, sel, lcd, unit, title, notes, ends, head, sub in (
        (
            0,
            "200",
            "0.8",
            "Ω",
            "Le long d'un bobinage",
            ("les deux broches", "du même bobinage"),
            ("p1", "p2"),
            "✓ Faible résistance : bobinage continu",
            "OL : bobinage coupé. Refaire sur chaque bobinage",
        ),
        (
            380,
            "2M",
            "OL",
            "MΩ",
            "Entre primaire et secondaire",
            ("une broche de chaque", "bobinage"),
            ("p1", "s2"),
            "✓ OL : bobinages isolés",
            "toute continuité entre bobinages séparés : défaut",
        ),
    ):
        o, v, com = half_meter(x0, sel, lcd, unit, title, notes)
        part, pads = four_pad(x0 + 290, 250, ("P", "S"))
        b += o + part + hookup(v, com, pads[ends[0]], pads[ends[1]])
        b += verdict(x0 + 190, 478, head, sub, "ok")
    b += text(
        380,
        528,
        "L'ohmmètre trouve la coupure et le court-circuit entre bobinages, pas les spires en court-circuit (fiche 30).",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        546,
        "Contrôler un transformateur à l'ohmmètre",
        "Deux mesures côte à côte sur un petit transformateur à quatre broches, dessoudé, bobinage primaire P en haut et secondaire S en bas. "
        "À gauche, multimètre sur le calibre 200 ohms, une pointe sur chaque broche du primaire : 0,8 ohm, le bobinage est continu ; OL signifierait un bobinage coupé. La mesure se refait sur chaque bobinage. "
        "À droite, multimètre sur le calibre 2 mégohms, une pointe sur le primaire et l'autre sur le secondaire : OL, les bobinages sont isolés ; toute continuité entre deux bobinages séparés est un défaut. "
        "L'ohmmètre trouve la coupure et le court-circuit entre bobinages, pas les spires en court-circuit : voir la fiche 30.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def fig_ratio() -> str:
    b = heading(
        "Vérifier le rapport de transformation en très basse tension",
        f"Transformateur basse fréquence dessoudé, générateur sinus 100 Hz réglé sur {_fr(INJECTED)} V efficace au plus",
    )
    b += '  <path class="grid" d="M380 84 V504"/>\n'
    out = secondary_voltage(INJECTED, RATIO)
    for x0, volts, title, ends, head, sub in (
        (
            0,
            INJECTED,
            "1. Tension au primaire",
            ("p1", "p2"),
            f"{_fr(INJECTED)} V injecté au primaire",
            "le générateur reste branché sur le primaire",
        ),
        (
            380,
            out,
            "2. Tension au secondaire",
            ("s1", "s2"),
            f"✓ {_fr(out)} V : rapport {_fr(INJECTED)} / {_fr(out)} = {RATIO}",
            "à comparer au rapport du schéma ou de la fiche technique",
        ),
    ):
        o, v, com = half_meter(x0, "V~", _lcd(volts), "V", title, ())
        part, pads = four_pad(x0 + 290, 250, ("P", "S"))
        b += o + box(x0 + 225, 118, 130, 50, "Générateur", ("sinus 100 Hz",))
        b += f'  <path class="wire" d="M{pads["p1"][0]} 168 V214 M{pads["p2"][0]} 168 V214"/>\n'
        b += part + hookup(v, com, pads[ends[0]], pads[ends[1]])
        b += verdict(x0 + 190, 478, head, sub, "ok")
    b += text(
        380,
        528,
        "Le multimètre ne mesure juste qu'en basse fréquence : pour un transformateur d'impulsions, passer à l'oscilloscope.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        546,
        "Vérifier le rapport de transformation d'un transformateur basse fréquence",
        f"Deux mesures côte à côte sur un petit transformateur basse fréquence dessoudé. Un générateur délivre une sinusoïde de 100 hertz, {_fr(INJECTED)} volt efficace au plus, sur le primaire P. "
        f"À gauche, multimètre sur volts alternatifs, une pointe sur chaque broche du primaire : {_fr(INJECTED)} volt. "
        f"À droite, même calibre, une pointe sur chaque broche du secondaire S : {_fr(out)} volt. "
        f"Le rapport des deux tensions vaut {RATIO} : il se compare au rapport du schéma ou de la fiche technique. "
        "Le multimètre ne mesure juste qu'en basse fréquence : pour un transformateur d'impulsions, passer à l'oscilloscope.",
        b,
    )


FIGURES = {
    "symbole-et-rapport": (fig_symbol, []),
    "controle-a-l-ohmmetre": (fig_windings, ["200", "2M"]),
    "rapport-de-transformation": (fig_ratio, ["V~", "V~"]),
}
