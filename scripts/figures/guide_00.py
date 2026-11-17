"""Figures of guide 00, safety for low-voltage bench work."""

from __future__ import annotations

import math

from elements import (
    NODE_A,
    NODE_B,
    bench_supply,
    cap_v,
    clip,
    meter,
    power_resistor,
    side_hookup,
    svg,
    text,
)

YA, YB = NODE_A[1], NODE_B[1]


def fig_supply() -> str:
    b = text(
        24,
        38,
        "Alimentation de laboratoire : la limite de courant protège la carte",
        size=20,
        weight=700,
    )
    b += text(
        24,
        60,
        "Tension réglée à 5 V et limite à 100 mA, sorties déconnectées, avant de brancher la carte",
        "mut",
        14,
    )
    b += '  <path class="grid" d="M380 84 V470"/>\n'

    def half(x0: int, shorted: bool) -> str:
        o = text(
            x0 + 20,
            100,
            "Carte en court-circuit" if shorted else "Carte saine",
            size=15,
            weight=700,
        )
        s, minus, plus = bench_supply(
            x0 + 20,
            116,
            "0.21" if shorted else "5.00",
            "0.100" if shorted else "0.080",
            "CC" if shorted else "CV",
        )
        o += s
        notes = (
            ("Voyant CC :", "la limite agit,", "la tension", "s'effondre.")
            if shorted
            else ("Voyant CV :", "la tension", "est tenue,", "80 mA lus.")
        )
        for i, line in enumerate(notes):
            o += text(
                x0 + 264,
                160 + 17 * i,
                line,
                "no" if shorted and i == 0 else "ok" if i == 0 else "mut",
                12.5,
                weight=700 if i == 0 else None,
            )
        # the board under test
        o += f'  <rect x="{x0 + 60}" y="350" width="260" height="70" rx="5" fill="#1f7a4d"/>\n'
        o += f'  <rect x="{x0 + 150}" y="368" width="70" height="34" rx="3" fill="#20242b"/>\n'
        for px in range(x0 + 158, x0 + 216, 12):
            o += f'  <path d="M{px} 364 v4 M{px} 402 v4" stroke="#c9d0d9" stroke-width="3"/>\n'
        for px, col in ((x0 + 92, "#20242b"), (x0 + 288, "#dc2626")):
            o += f'  <circle cx="{px}" cy="368" r="8" fill="#d4a017"/><circle cx="{px}" cy="368" r="3.5" fill="{col}"/>\n'
        o += f'  <text x="{x0 + 92}" y="394" font-size="11" text-anchor="middle" fill="#ffffff">0 V</text>\n'
        o += f'  <text x="{x0 + 288}" y="394" font-size="11" text-anchor="middle" fill="#ffffff">+5 V</text>\n'
        o += (
            f'  <path class="blk" stroke-width="4" fill="none" stroke-linecap="round" '
            f'd="M{minus[0]} {minus[1]} C{minus[0]} 320 {x0 + 92} 300 {x0 + 92} 368"/>\n'
        )
        o += (
            f'  <path stroke="#dc2626" stroke-width="4" fill="none" stroke-linecap="round" '
            f'd="M{plus[0]} {plus[1]} C{plus[0]} 320 {x0 + 288} 300 {x0 + 288} 368"/>\n'
        )
        if shorted:
            o += f'  <path d="M{x0 + 236} 372 l26 26 m0 -26 l-26 26" stroke="#f87171" stroke-width="5" stroke-linecap="round"/>\n'
        else:
            o += f'  <circle cx="{x0 + 249}" cy="385" r="7" fill="#4ade80" stroke="#bbf7d0" stroke-width="2"/>\n'
        verdict = (
            (
                "✗ Voyant CC, tension proche de 0 V",
                "court-circuit probable : couper et chercher, sans monter la limite",
            )
            if shorted
            else (
                "✓ Courant stable sous la limite, voyant CV",
                "la carte fonctionne : limite juste au-dessus du courant lu",
            )
        )
        o += text(
            x0 + 190, 446, verdict[0], "no" if shorted else "ok", 14, "middle", 700
        )
        o += text(x0 + 190, 464, verdict[1], "mut", 12, "middle")
        return o

    b += half(0, False) + half(380, True)
    return svg(
        760,
        484,
        "Alimentation de laboratoire limitée en courant : carte saine et carte en court-circuit",
        "Deux alimentations de laboratoire réglées à 5 V avec une limite de courant de 100 mA. "
        "À gauche, carte saine : l'afficheur indique 5,00 V et 0,080 A, le voyant CV (tension constante) est allumé. "
        "À droite, carte en court-circuit : la limite agit, l'afficheur indique 0,21 V et 0,100 A, le voyant CC (courant constant) est allumé ; "
        "la tension s'effondre au lieu de brûler une piste.",
        b,
    )


def fig_discharge() -> str:
    b = text(
        24,
        38,
        "Décharger un condensateur dans une résistance, puis vérifier",
        size=20,
        weight=700,
    )
    b += text(
        24,
        60,
        "Exemple : 1000 µF chargé à 35 V, résistance de 1 kΩ 5 W : 35 mA au départ, 5 s environ",
        "mut",
        14,
    )
    m, jacks = meter(30, 80, 1, "VDC", "0.42", "V", "DC")
    b += m
    b += f'  <path class="wire" d="M300 {YA} H470 M300 {YB} H560 M470 {YA} V205 H480 M550 205 H560 V{YB}"/>\n'
    b += cap_v(370, YA, YB)
    b += f'  <circle class="fg" cx="300" cy="{YA}" r="5"/><circle class="fg" cx="300" cy="{YB}" r="5"/>\n'
    b += text(402, 180, "1000 µF", "blue", 13, weight=700) + text(
        402, 198, "+ en haut", "mut", 12
    )
    b += (
        power_resistor(480, 550, 205, "1 kΩ 5 W")
        + clip(470, YA, True)
        + clip(560, YB, False)
    )
    b += text(504, 240, "avec des pinces,", "mut", 11, "middle") + text(
        504, 254, "jamais à mains nues", "mut", 11, "middle"
    )
    b += f'  <path class="flow fa" d="M380 {YA - 9} H458 M548 {YB + 9} H380"/>\n'
    b += side_hookup(jacks.v, jacks.com)
    for i, (num, line, sub) in enumerate(
        (
            ("1", "Mesurer la tension", ""),
            ("2", "Brancher la résistance", ""),
            ("3", "Attendre 5 × R × C", ""),
            ("4", "Vérifier : sous 1 V", ""),
            ("5", "Revérifier avant", "la mesure suivante"),
        )
    ):
        y = 112 + 36 * i
        b += f'  <circle class="blue" cx="596" cy="{y - 4}" r="9"/>\n'
        b += f'  <text x="596" y="{y}" font-size="11" font-weight="700" text-anchor="middle" fill="#ffffff">{num}</text>\n'
        b += text(612, y, line, "fg", 12) + (
            text(612, y + 15, sub, "fg", 12) if sub else ""
        )
    # discharge curve: 35 V, RC = 1 s
    x0, y0, sx, sy = 330, 430, 62, 80 / 35
    b += f'  <path class="wire" d="M{x0} 340 V{y0} H{x0 + 6.4 * sx:.0f}" stroke-width="1.5"/>\n'
    pts = " ".join(
        f"{x0 + t / 10 * sx:.1f},{y0 - 35 * math.exp(-t / 10) * sy:.1f}"
        for t in range(0, 61, 2)
    )
    b += f'  <polyline points="{pts}" fill="none" stroke="#d97706" stroke-width="3" stroke-linejoin="round"/>\n'
    b += text(x0 - 6, 354, "35 V", "mut", 11, "end") + text(
        x0 - 6, y0 + 4, "0", "mut", 11, "end"
    )
    for t in range(1, 7):
        b += f'  <path class="wire" d="M{x0 + t * sx} {y0} v4" stroke-width="1.5"/>\n'
        b += text(x0 + t * sx, y0 + 18, f"{t} s", "mut", 11, "middle")
    b += f'  <path class="grid" d="M{x0 + 5 * sx} 350 V{y0}"/>\n'
    b += text(x0 + 5 * sx - 8, 366, "5 × R × C = 5 s", "warn", 12, "end", 700)
    b += text(x0 + 5 * sx - 8, 382, "moins de 1 % : 0,24 V", "mut", 12, "end")
    b += text(x0 + 70, 372, "13 V après 1 s", "mut", 12)
    b += text(24, 452, "Jamais de tournevis en court-circuit", "no", 12, weight=700)
    b += text(24, 468, "sur les bornes.", "no", 12, weight=700)
    return svg(
        760,
        484,
        "Décharger un condensateur dans une résistance, puis vérifier au voltmètre",
        "Un condensateur électrolytique de 1000 µF chargé à 35 V est déchargé dans une résistance de 1 kΩ 5 W tenue par des pinces crocodile. "
        "Un multimètre, sélecteur sur volts continus, pointe rouge sur la borne plus, vérifie la tension : 0,42 V après la décharge. "
        "La courbe montre la tension qui tombe de 35 V à moins de 1 % en cinq constantes de temps, soit 5 secondes. "
        "Étapes : mesurer la tension, brancher la résistance, attendre cinq fois R fois C, vérifier que la tension est sous 1 V, revérifier avant la mesure suivante.",
        b,
    )


FIGURES = {
    "alimentation-limitee": (fig_supply, []),
    "decharge-condensateur": (fig_discharge, ["VDC"]),
}
