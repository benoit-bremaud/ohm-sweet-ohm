"""Figures of guide 01, understand your multimeter: one figure per mode."""

from __future__ import annotations

from elements import (
    NODE_A,
    NODE_B,
    Jacks,
    box,
    diode_v,
    lead,
    meter,
    res_v,
    side_hookup,
    svg,
    text,
)

YA, YB = NODE_A[1], NODE_B[1]


def _nodes() -> str:
    return (
        f'  <circle class="fg" cx="{NODE_A[0]}" cy="{YA}" r="5"/>'
        f'<circle class="fg" cx="{NODE_B[0]}" cy="{YB}" r="5"/>\n'
    )


def _notes(lines: list[str], y: int = 352) -> str:
    """Bulleted key points under the hookup, right of the meter."""
    o = ""
    for i, s in enumerate(lines):
        o += f'  <circle class="mut" cx="292" cy="{y + 22 * i - 4}" r="2.5"/>\n'
        o += text(302, y + 22 * i, s, "fg", 12.5)
    return o


def _powered_rails(
    source: tuple[str, tuple[str, ...]], load: str, top: str, bottom: str
) -> str:
    """Source and load blocks between two rails, with the load current animated."""
    o = f'  <path class="wire" d="M300 {YA} H580 M300 {YB} H580 M420 {YA} V165 M420 245 V{YB} M580 {YA} V165 M580 245 V{YB}"/>\n'
    o += box(370, 165, 100, 80, source[0], source[1]) + box(530, 165, 100, 80, load)
    o += f'  <path class="flow fb" d="M430 160 V{YA + 9} H570 V160 M570 250 V{YB - 9} H430 V250"/>\n'
    o += text(500, YA - 10, top, "mut", 12, "middle") + text(
        500, YB + 20, bottom, "mut", 12, "middle"
    )
    return o + _nodes()


def fig_volts_dc() -> str:
    b = text(
        24,
        38,
        "Voltmètre continu : en parallèle, carte sous tension",
        size=20,
        weight=700,
    )
    b += text(
        24, 60, "Sélecteur sur V continu, cordon rouge dans la douille VΩ", "mut", 14
    )
    m, jacks = meter(30, 80, 1, "VDC", "5.02", "V", "DC")
    b += m
    b += _powered_rails(
        ("Alim. 5 V", ("limitée", "en courant")), "Carte", "rail +5 V", "masse (0 V)"
    )
    b += side_hookup(jacks.v, jacks.com)
    b += text(644, 200, "Le courant de", "mut", 12) + text(
        644, 216, "la carte ne passe", "mut", 12
    )
    b += text(644, 232, "pas par l'appareil.", "mut", 12)
    b += _notes(
        [
            "Pointe noire sur la masse, pointe rouge sur le point à mesurer.",
            "Entrée de 1 à 10 MΩ : l'appareil ne dévie presque aucun courant.",
            "Lecture négative : les pointes sont inversées, rien de plus.",
            "Point à haute impédance (MΩ) : l'appareil fait baisser la lecture.",
        ]
    )
    return svg(
        760,
        450,
        "Voltmètre continu : mesure en parallèle sur une carte alimentée",
        "Un multimètre, sélecteur sur volts continus, cordon rouge dans la douille V ohms, a sa pointe rouge sur le rail +5 V et sa pointe noire sur la masse "
        "d'une carte alimentée par une alimentation limitée en courant. Il lit 5,02 V. Le courant de la carte ne passe pas par l'appareil, "
        "dont l'entrée présente 1 à 10 MΩ.",
        b,
    )


def fig_volts_ac() -> str:
    b = text(
        24,
        38,
        "Voltmètre alternatif : même branchement, sans polarité",
        size=20,
        weight=700,
    )
    b += text(
        24,
        60,
        "Sélecteur sur V alternatif (V~), cordon rouge dans la douille VΩ",
        "mut",
        14,
    )
    m, jacks = meter(30, 80, 1, "V~", "12.1", "V", "AC")
    b += m
    b += _powered_rails(
        ("Transfo.", ("sortie 12 V~",)), "Charge", "12 V alternatif", "retour"
    )
    b += '  <path d="M396 232 q6 -12 12 0 t12 0 t12 0 t12 0" fill="none" stroke="#2563eb" stroke-width="2"/>\n'
    b += side_hookup(jacks.v, jacks.com, polarity=False)
    b += text(644, 200, "L'appareil affiche", "mut", 12) + text(
        644, 216, "la valeur efficace,", "mut", 12
    )
    b += text(644, 232, "pas la crête.", "mut", 12)
    b += _notes(
        [
            "Pas de sens des pointes : la lecture est la même, pointes inversées.",
            "Limite de cette série : 25 V alternatif au plus, partout sur la carte.",
            "Forme non sinusoïdale : seul un appareil « True RMS » lit juste.",
            "Fil en l'air : des volts « fantômes », qui disparaissent sous charge.",
        ]
    )
    return svg(
        760,
        450,
        "Voltmètre alternatif : mesure en parallèle, sans polarité",
        "Un multimètre, sélecteur sur volts alternatifs, cordon rouge dans la douille V ohms, a ses pointes en parallèle sur la sortie 12 V alternatif "
        "d'un transformateur qui alimente une charge. Il lit 12,1 V, la valeur efficace. Le sens des pointes est indifférent.",
        b,
    )


def fig_ohms() -> str:
    b = text(
        24,
        38,
        "Ohmmètre : l'appareil injecte un courant et lit une tension",
        size=20,
        weight=700,
    )
    b += text(
        24,
        60,
        "Sélecteur sur Ω, calibre 20 kΩ, cordon rouge dans la douille VΩ, composant hors tension",
        "mut",
        14,
    )
    m, jacks = meter(30, 80, 1, "20k", "9.96", "kΩ")
    b += m
    b += (
        f'  <path class="wire" d="M300 {YA} H420 M300 {YB} H420"/>\n'
        + res_v(420, YA, YB)
        + _nodes()
    )
    b += text(440, 200, "R · 10 kΩ", "blue", 13, weight=700) + text(
        440, 218, "tolérance 5 %", "mut", 12
    )
    b += f'  <path class="flow fb" d="M308 {YA + 9} H398 V{YB - 9} H308"/>\n'
    b += side_hookup(jacks.v, jacks.com)
    b += '  <rect class="panel" x="540" y="100" width="196" height="200" rx="10" stroke-width="1.5"/>\n'
    b += text(556, 126, "Ce que fait l'appareil", size=14, weight=700)
    for i, (head, sub) in enumerate(
        (
            ("1. Il injecte un courant", "connu : I ≈ 100 µA ici"),
            ("2. Il mesure la tension", "V ≈ 1 V entre les pointes"),
            ("3. Il affiche R = V / I", "ici 9,96 kΩ : dans la tolérance"),
        )
    ):
        b += text(556, 156 + 50 * i, head, "fg", 12.5, weight=700) + text(
            556, 174 + 50 * i, sub, "mut", 12
        )
    b += _notes(
        [
            "Carte hors tension, condensateurs déchargés, sinon lecture fausse.",
            "Pointes tenues à mains nues : le corps se met en parallèle.",
            "Sous 10 Ω : retrancher la résistance des cordons (touche REL).",
            "« OL » : au-delà du calibre, ou circuit ouvert.",
        ]
    )
    return svg(
        760,
        450,
        "Ohmmètre : un courant de test injecté, une tension lue",
        "Un multimètre, sélecteur sur ohms calibre 20 kΩ, cordon rouge dans la douille V ohms, mesure une résistance de 10 kΩ isolée, hors tension. "
        "Il injecte un courant connu d'environ 100 µA, mesure environ 1 V entre ses pointes et affiche 9,96 kΩ, le rapport de la tension au courant.",
        b,
    )


def fig_beeper() -> str:
    b = text(24, 38, "Bipeur : il répond « faible », pas « nul »", size=20, weight=700)
    b += text(
        24,
        60,
        "Sélecteur sur continuité, cordon rouge dans la douille VΩ, carte hors tension",
        "mut",
        14,
    )
    m, jacks = meter(30, 80, 1, "BEEP", "0.3", "Ω", "•)))")
    b += m
    # a board with one copper track between two pads
    b += '  <rect x="282" y="104" width="178" height="202" rx="6" fill="#1f7a4d"/>\n'
    b += f'  <path d="M300 {YA} H420 V{YB} H300" fill="none" stroke="#d4a017" stroke-width="9" stroke-linejoin="round"/>\n'
    for py in (YA, YB):
        b += f'  <circle cx="300" cy="{py}" r="10" fill="#d4a017"/><circle cx="300" cy="{py}" r="3.5" fill="#0d3b26"/>\n'
    b += '  <text x="372" y="210" font-size="11" text-anchor="middle" fill="#ffffff">piste</text>\n'
    b += side_hookup(jacks.v, jacks.com, polarity=False)
    # threshold scale
    b += text(490, 122, "Ce qui fait sonner l'appareil", size=14, weight=700)
    b += '  <rect x="490" y="136" width="120" height="24" rx="5" fill="#16a34a"/>\n'
    b += '  <rect x="610" y="136" width="126" height="24" rx="5" fill="#9aa3ae"/>\n'
    b += '  <text x="550" y="153" font-size="12" font-weight="700" text-anchor="middle" fill="#ffffff">bip</text>\n'
    b += '  <text x="673" y="153" font-size="12" font-weight="700" text-anchor="middle" fill="#1f2933">silence</text>\n'
    b += '  <path class="grid" d="M610 130 V170"/>\n'
    b += text(610, 186, "seuil : 10 à 100 Ω", "mut", 12, "middle") + text(
        610, 202, "selon l'appareil", "mut", 12, "middle"
    )
    for i, (val, verdict, cls) in enumerate(
        (
            ("0,1 Ω · court-circuit franc", "bip", "ok"),
            ("47 Ω · une résistance", "bip aussi", "warn"),
            ("1 kΩ", "silence", "mut"),
        )
    ):
        b += text(490, 232 + 22 * i, val, "fg", 12.5) + text(
            736, 232 + 22 * i, verdict, cls, 12.5, "end", 700
        )
    b += _notes(
        [
            "Carte hors tension : le bipeur est un ohmmètre sur son petit calibre.",
            "Court-circuit ou faible résistance ? Lire la valeur en Ω.",
            "Un gros condensateur bipe brièvement puis se tait : il se charge.",
            "Un vrai court-circuit bipe dans les deux sens des pointes.",
        ]
    )
    return svg(
        760,
        450,
        "Bipeur de continuité : un seuil, pas une mesure",
        "Un multimètre, sélecteur sur continuité, cordon rouge dans la douille V ohms, a ses pointes sur les deux pastilles d'une piste de circuit imprimé, hors tension. "
        "Il lit 0,3 Ω et sonne. L'appareil sonne sous un seuil de 10 à 100 Ω selon le modèle : "
        "un court-circuit de 0,1 Ω sonne, une résistance de 47 Ω sonne aussi, 1 kΩ reste silencieux.",
        b,
    )


def _half_meter(x0: int, y: int, sel: str, lcd: str, unit: str) -> tuple[str, Jacks]:
    return meter(x0 + 24, y, 0.9, sel, lcd, unit)


def fig_diode() -> str:
    b = text(
        24,
        38,
        "Mode diode : une tension dans un sens, « OL » dans l'autre",
        size=20,
        weight=700,
    )
    b += text(
        24,
        60,
        "Sélecteur sur le symbole diode, cordon rouge dans la douille VΩ, composant hors tension",
        "mut",
        14,
    )
    b += '  <path class="grid" d="M380 84 V470"/>\n'

    def half(
        x0: int, forward: bool, lcd: str, title: str, verdict: tuple[str, str]
    ) -> str:
        o = text(x0 + 20, 100, title, size=15, weight=700)
        m, jacks = _half_meter(x0, 116, "DIODE", lcd, "V")
        o += m
        dx, top, bot = x0 + 290, 190, 310
        o += diode_v(dx, top, bot, False, 26, 62)
        o += text(dx + 22, top + 14, "anode", "mut", 12) + text(
            dx + 22, bot - 6, "cathode", "mut", 12
        )
        o += text(dx + 22, bot + 9, "(bague)", "mut", 11)
        (vx, jy), cx = jacks.v, jacks.com[0]
        red_end, blk_end = (top, bot) if forward else (bot, top)
        xi = x0 + 208

        def inner(jx: float) -> str:
            return (
                f"V{jy + 16} C{jx:.1f} {jy + 60} {xi} {jy + 66} {xi} 300 V240 "
                f"C{xi} {top + 12} {xi + 24} {top} {dx} {top}"
            )

        def outer(jx: float) -> str:
            return f"V{jy + 40} C{jx:.1f} {jy + 100} {dx} {jy + 100} {dx} {bot}"

        if forward:
            o += lead(jacks.com, outer(cx), False) + lead(jacks.v, inner(vx), True)
            o += f'  <path class="flow fb" d="M{dx - 22} {top + 8} V{bot - 8}"/>\n'
            o += text(dx + 22, 254, "≈ 1 mA", "blue", 12, weight=700)
        else:
            o += lead(jacks.v, outer(vx), True) + lead(jacks.com, inner(cx), False)
            o += text(dx + 22, 254, "aucun", "mut", 12) + text(
                dx + 22, 269, "courant", "mut", 12
            )
        o += f'  <circle cx="{dx}" cy="{red_end}" r="5" fill="#dc2626"/><circle class="blkf" cx="{dx}" cy="{blk_end}" r="5"/>\n'
        o += text(dx - 12, red_end + (-8 if forward else 20), "+", "no", 16, "end", 700)
        o += text(x0 + 190, 478, verdict[0], "ok", 14, "middle", 700)
        o += text(x0 + 190, 496, verdict[1], "mut", 12, "middle")
        return o

    b += half(
        0,
        True,
        "0.582",
        "Pointe rouge sur l'anode",
        ("✓ 0,5 à 0,7 V : la jonction conduit", "sens passant, diode au silicium"),
    )
    b += half(
        380,
        False,
        "OL",
        "Pointes inversées",
        ("✓ OL : la jonction bloque", "sens inverse, aucune tension lue"),
    )
    b += text(24, 524, "Proche de 0 V dans les deux sens : court-circuit.", "mut", 12)
    b += text(
        24,
        541,
        "« OL » dans les deux sens : diode ouverte, ou tension directe hors de portée (LED bleue ou blanche).",
        "mut",
        12,
    )
    return svg(
        760,
        558,
        "Mode diode : tension directe dans un sens, hors limite dans l'autre",
        "Deux multimètres, sélecteur sur le symbole diode, cordon rouge dans la douille V ohms, testent la même diode au silicium hors tension. "
        "À gauche, pointe rouge sur l'anode : un courant d'environ 1 mA traverse la jonction, l'appareil lit 0,582 V. "
        "À droite, pointes inversées : la jonction bloque, l'appareil affiche OL. Proche de 0 V dans les deux sens : court-circuit ; "
        "OL dans les deux sens : diode ouverte, ou tension directe hors de portée.",
        b,
    )


def fig_current() -> str:
    b = text(
        24,
        38,
        "Mode courant : en série, et jamais oublié sur la douille 10 A",
        size=20,
        weight=700,
    )
    b += text(
        24,
        60,
        "Entre les douilles 10 A et COM, l'appareil est un fil (shunt de quelques milliohms)",
        "mut",
        14,
    )
    b += '  <path class="grid" d="M380 84 V480"/>\n'

    def half(x0: int, trap: bool) -> str:
        title = (
            "Le piège : en parallèle, cordon resté sur 10 A"
            if trap
            else "La mesure : en série, circuit ouvert"
        )
        o = text(x0 + 20, 100, title, size=15, weight=700)
        m, jacks = _half_meter(
            x0,
            116,
            "VDC" if trap else "ADC",
            "0.00" if trap else "0.150",
            "V" if trap else "A",
        )
        o += m
        (ax, jy), cx = jacks.a, jacks.com[0]
        xl, xr, yt = x0 + 262, x0 + 330, 190
        name = (
            ("Batterie", ("ou alim.", "non limitée"))
            if trap
            else ("Alim. 12 V", ("limitée",))
        )
        o += box(x0 + 246, 116, 100, 62, name[0], name[1])
        o += text(xl - 6, yt, "+", "no", 15, "end", 700) + text(
            xr + 8, yt, "−", "fg", 15, weight=700
        )
        red = f"V{jy + 16} C{ax:.1f} {jy + 60} {x0 + 208} {jy + 66} {x0 + 208} 300 V240 C{x0 + 208} 212 {x0 + 232} {yt + 14} {xl} {yt + 14}"
        if trap:
            o += f'  <path class="wire" d="M{xl} 178 V{yt + 14} M{xr} 178 V{yt + 14}"/>\n'
            blk = (
                f"V{jy + 36} C{cx:.1f} {jy + 78} {x0 + 250} {jy + 78} {xr} {jy + 78} "
                f"C{x0 + 366} {jy + 78} {x0 + 366} 330 {x0 + 366} 280 C{x0 + 366} 230 {x0 + 352} {yt + 14} {xr} {yt + 14}"
            )
            o += lead(jacks.com, blk, False) + lead(jacks.a, red, True)
            o += f'  <circle cx="{ax:.1f}" cy="{jy:.1f}" r="15" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="4 3"/>\n'
            o += f'  <path class="flow fr" d="M{xl + 9} 186 V{yt + 24} M{xr - 9} {yt + 24} V186"/>\n'
            o += text(x0 + 296, 262, "✗", "no", 34, "middle", 700)
            o += text(x0 + 296, 288, "court-circuit", "no", 13, "middle", 700)
            o += text(x0 + 296, 308, "des dizaines", "mut", 12, "middle") + text(
                x0 + 296, 324, "d'ampères", "mut", 12, "middle"
            )
            o += text(x0 + 296, 350, "douille 10 A", "mut", 12, "middle") + text(
                x0 + 296, 366, "souvent", "mut", 12, "middle"
            )
            o += text(x0 + 296, 382, "sans fusible", "mut", 12, "middle")
        else:
            yq, yload = yt + 44, 290
            o += f'  <path class="wire" d="M{xl} 178 V{yt + 14} M{xl} {yq} V{yload} M{xr} 178 V{yload}"/>\n'
            o += box(x0 + 246, yload, 100, 50, "Charge")
            blk = f"V{jy + 40} C{cx:.1f} {jy + 92} {x0 + 230} {jy + 92} {x0 + 230} 330 V270 C{x0 + 230} 246 {x0 + 244} {yq} {xl} {yq}"
            o += lead(jacks.com, blk, False) + lead(jacks.a, red, True)
            o += f'  <path class="flow fb" d="M{xr + 9} {yload - 6} V186"/>\n'
            o += text(xr + 18, 244, "I", "blue", 13, weight=700)
            o += text(x0 + 296, 372, "Le courant traverse", "mut", 12, "middle")
            o += text(x0 + 296, 388, "l'appareil : 150 mA", "mut", 12, "middle")
        o += f'  <circle cx="{xl}" cy="{yt + 14}" r="5" fill="#dc2626"/>\n'
        o += f'  <circle class="blkf" cx="{xr if trap else xl}" cy="{yt + 14 if trap else yt + 44}" r="5"/>\n'
        return o

    b += half(0, False) + half(380, True)
    b += text(
        190, 478, "✓ Sélecteur sur A, cordon rouge sur 10 A", "ok", 14, "middle", 700
    )
    b += text(
        190, 496, "le circuit est coupé, l'appareil le referme", "mut", 12, "middle"
    )
    b += text(
        570,
        478,
        "✗ Sélecteur sur V, cordon rouge resté sur 10 A",
        "no",
        14,
        "middle",
        700,
    )
    b += text(
        570,
        496,
        "« pour lire la tension » : la source est court-circuitée",
        "mut",
        12,
        "middle",
    )
    b += text(
        24,
        524,
        "Remettre le cordon rouge dans la douille VΩ avant chaque mesure de tension.",
        "mut",
        12,
    )
    b += text(
        24, 541, "La mesure de courant elle-même relève de la fiche 91.", "mut", 12
    )
    return svg(
        760,
        558,
        "Mode courant : mesure en série, et piège du cordon oublié sur la douille 10 A",
        "À gauche, la mesure : sélecteur sur ampères continus, cordon rouge dans la douille 10 A, l'appareil est inséré en série dans le fil coupé "
        "entre une alimentation limitée et sa charge ; il lit 0,150 A. "
        "À droite, le piège : sélecteur sur volts continus mais cordon rouge resté dans la douille 10 A, pointes en parallèle sur une batterie ; "
        "le shunt de l'appareil court-circuite la source, des dizaines d'ampères circulent, et la douille 10 A est souvent sans fusible.",
        b,
    )


FIGURES = {
    "voltmetre-continu": (fig_volts_dc, ["VDC"]),
    "voltmetre-alternatif": (fig_volts_ac, ["V~"]),
    "ohmmetre": (fig_ohms, ["20k"]),
    "bipeur": (fig_beeper, ["BEEP"]),
    "mode-diode": (fig_diode, ["DIODE", "DIODE"]),
    "mode-courant": (fig_current, ["ADC", "VDC"]),
}
