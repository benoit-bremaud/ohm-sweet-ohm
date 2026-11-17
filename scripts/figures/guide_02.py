"""Figures of guide 02, in-circuit measurement pitfalls."""

from __future__ import annotations

from elements import diode_v, lead, meter, probe, res_h, res_v, svg, text


# ---------------------------------------------------------------- figure 1
def fig_parallel() -> str:
    b = text(24, 38, "L'ohmmètre mesure le nœud, pas le composant", size=20, weight=700)
    b += text(
        24,
        60,
        "Sélecteur sur Ω, calibre 20 kΩ : R1 est saine (10 kΩ), l'appareil lit pourtant 5 kΩ",
        "mut",
        14,
    )
    m, (_, com, v) = meter(30, 80, 1, "20k", "5.00", "kΩ")
    b += m
    ya, yb = 130, 280
    b += f'  <path class="wire" d="M300 {ya} H610 M300 {yb} H610"/>\n'
    b += res_v(390, ya, yb) + res_v(500, ya, yb) + diode_v(610, ya, yb, True)
    b += '  <circle class="fg" cx="300" cy="130" r="5"/><circle class="fg" cx="300" cy="280" r="5"/>\n'
    b += text(390, 112, "R1 · 10 kΩ", "blue", 13, "middle", 700) + text(
        390, 306, "mesurée", "blue", 12, "middle"
    )
    b += text(500, 112, "R2 · 10 kΩ", "amber", 13, "middle", 700) + text(
        500, 306, "chemin caché", "amber", 12, "middle"
    )
    b += text(610, 112, "jonction", "mut", 13, "middle", 700) + text(
        610, 306, "bloquée dans ce sens", "mut", 12, "middle"
    )
    b += text(610, 322, "(conduirait, pointes inversées)", "mut", 12, "middle")
    b += text(624, 135, "nœud A", "fg", 12) + text(624, 285, "nœud B", "fg", 12)
    b += '  <path class="flow fb" d="M308 139 H368 V271 H308"/>\n'
    b += '  <path class="flow fa" d="M308 121 H524 V289 H308"/>\n'
    b += text(300, 90, "Le courant de test se partage :", "mut", 12)
    b += '  <circle class="blue" cx="484" cy="86" r="4"/>\n' + text(
        492, 90, "dans R1", "blue", 12
    )
    b += '  <circle class="amber" cx="552" cy="86" r="4"/>\n' + text(
        560, 90, "dans R2", "amber", 12
    )
    p, e = probe(300, 130, -0.6, 0.8, True)
    b += (
        lead(
            v,
            f"V395 C165 425 232 425 236 340 C240 260 235 215 {e[0]:.1f} {e[1]:.1f}",
            True,
        )
        + p
    )
    p, e = probe(300, 280, -0.6, 0.8, False)
    b += lead(com, f"V398 C120 442 262 446 {e[0]:.1f} {e[1]:.1f}", False) + p
    b += text(284, 124, "+", "no", 16, "end", 700) + text(
        284, 274, "−", "fg", 16, "end", 700
    )
    # reading scale
    b += text(300, 358, "Que vaut la lecture stabilisée ?", size=14, weight=700)
    b += '  <rect x="300" y="368" width="240" height="24" rx="5" fill="#f59e0b"/>\n'
    b += '  <rect x="540" y="368" width="60" height="24" fill="#16a34a"/>\n'
    b += '  <rect x="600" y="368" width="140" height="24" rx="5" fill="#dc2626"/>\n'
    b += '  <text x="420" y="385" font-size="12" font-weight="700" text-anchor="middle" fill="#1f2933">lecture ici : 5 kΩ</text>\n'
    b += text(300, 410, "En dessous", size=13, weight=700) + text(
        300, 426, "rien de prouvé", "mut", 12
    )
    b += text(570, 410, "nominale ± tol.", size=13, anchor="middle", weight=700) + text(
        570, 426, "probablement saine", "mut", 12, "middle"
    )
    b += text(740, 410, "Au-dessus", size=13, anchor="end", weight=700) + text(
        740, 426, "défectueuse", "mut", 12, "end"
    )
    return svg(
        760,
        450,
        "Chemins parallèles : l'ohmmètre mesure le nœud",
        "Un multimètre, sélecteur sur ohms calibre 20 kΩ, mesure une résistance R1 de 10 kΩ soudée. "
        "Une résistance R2 de 10 kΩ relie les mêmes nœuds : le courant de test se partage et l'appareil lit 5 kΩ. "
        "Une jonction relie aussi les deux nœuds ; elle est bloquée dans ce sens des pointes, pointe rouge sur sa cathode, et conduirait pointes inversées. "
        "Échelle de lecture : en dessous de la nominale, rien de prouvé ; dans la tolérance, probablement saine ; au-dessus, défectueuse.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def fig_junction() -> str:
    b = text(24, 38, "Monter d'un calibre démasque une jonction", size=20, weight=700)
    b += text(
        24,
        60,
        "Même montage des deux côtés : R = 10 kΩ, une diode au silicium en parallèle, dans le sens passant",
        "mut",
        14,
    )
    b += '  <path class="grid" d="M380 84 V446"/>\n'

    def half(x0, sel, lcd, volt, good, l1, l2):
        m, (_, com, v) = meter(x0 + 24, 84, 0.9, sel, lcd, "kΩ")
        o = m

        def yv(u):
            return 250 - 140 * u

        o += text(x0 + 205, 100, "tension aux pointes", "mut", 11)
        o += f'  <rect class="panel" x="{x0 + 228}" y="110" width="24" height="140" rx="4"/>\n'
        o += f'  <rect x="{x0 + 223}" y="{yv(0.5)}" width="34" height="{yv(0.4) - yv(0.5)}" fill="#fde68a" stroke="#d97706"/>\n'
        col = "#16a34a" if good else "#dc2626"
        o += f'  <rect x="{x0 + 228}" y="{yv(volt)}" width="24" height="{250 - yv(volt)}" rx="4" fill="{col}"/>\n'
        o += text(x0 + 222, 114, "1 V", "mut", 11, "end") + text(
            x0 + 222, 254, "0", "mut", 11, "end"
        )
        o += text(x0 + 264, 184, "conduction", "warn", 11, weight=700) + text(
            x0 + 264, 198, "0,4 à 0,5 V", "warn", 11
        )
        if not good:
            o += f'  <path class="grid" d="M{x0 + 224} 110 H{x0 + 258}"/>\n'
            o += text(x0 + 264, 114, "I × R = 1 V visé", "mut", 11)
        o += text(x0 + 205, 272, l1, "ok" if good else "no", 12, weight=700)
        # mini circuit
        o += f'  <path class="wire" d="M{x0 + 232} 300 H{x0 + 322} M{x0 + 232} 356 H{x0 + 322}" stroke-width="2.5"/>\n'
        o += res_v(x0 + 268, 300, 356, 12, 30) + diode_v(
            x0 + 322, 300, 356, False, 10, 24
        )
        o += text(x0 + 280, 332, "10 kΩ", "mut", 10) + text(
            x0 + 332, 332, "diode", "mut", 10
        )
        o += lead(
            v, f"C{v[0] + 4:.1f} {v[1] + 34:.1f} {x0 + 205} 322 {x0 + 232} 300", True
        )
        o += lead(com, f"V380 C{com[0]:.1f} 404 {x0 + 232} 404 {x0 + 232} 356", False)
        o += f'  <circle cx="{x0 + 232}" cy="300" r="4" fill="#dc2626"/><circle class="blkf" cx="{x0 + 232}" cy="356" r="4"/>\n'
        o += text(x0 + 190, 428, l2[0], "ok" if good else "no", 14, "middle", 700)
        o += text(x0 + 190, 446, l2[1], "mut", 12, "middle")
        return o

    b += half(
        0,
        "20k",
        "4.50",
        0.45,
        False,
        "0,45 V : elle conduit",
        ("✗ 4,5 kΩ lus au lieu de 10 kΩ", "calibre 20 kΩ · courant de test ≈ 100 µA"),
    )
    b += half(
        380,
        "200k",
        "10.0",
        0.1,
        True,
        "0,1 V : elle reste bloquée",
        ("✓ 10 kΩ lus", "calibre 200 kΩ · courant de test ≈ 10 µA"),
    )
    return svg(
        760,
        460,
        "Monter d'un calibre démasque une jonction en parallèle",
        "Deux multimètres mesurent le même montage : une résistance de 10 kΩ avec une diode au silicium en parallèle, dans le sens passant. "
        "À gauche, sélecteur sur le calibre 20 kΩ : le courant de test d'environ 100 µA viserait 1 V, la jonction conduit et plafonne la tension vers 0,45 V, l'appareil lit 4,5 kΩ. "
        "À droite, sélecteur sur le calibre 200 kΩ : le courant d'environ 10 µA ne donne que 0,1 V, la jonction reste bloquée, l'appareil lit 10 kΩ.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def fig_lift() -> str:
    b = text(
        24,
        38,
        "Lever une patte : couper la boucle, mesurer le composant seul",
        size=20,
        weight=700,
    )
    b += text(
        24,
        60,
        "Carte hors tension et déchargée, sélecteur sur Ω, calibre 20 kΩ",
        "mut",
        14,
    )
    b += '  <path class="grid" d="M380 84 V520"/>\n'

    def half(x0, lifted, lcd, title, verdict):
        o = text(x0 + 20, 96, title, size=15, weight=700)
        # board, side view
        o += f'  <rect x="{x0 + 55}" y="210" width="260" height="26" rx="3" fill="#1f7a4d"/>\n'
        o += (
            f'  <rect x="{x0 + 215}" y="210" width="100" height="26" fill="#145c39"/>\n'
        )
        o += f'  <text x="{x0 + 283}" y="227" font-size="9" text-anchor="middle" fill="#ffffff">plan de masse</text>\n'
        o += f'  <text x="{x0 + 84}" y="227" font-size="10" text-anchor="middle" fill="#ffffff">signal</text>\n'
        for px in (x0 + 125, x0 + 245):
            o += f'  <rect x="{px - 15}" y="205" width="30" height="5" rx="1" fill="#d4a017"/><rect x="{px - 15}" y="236" width="30" height="5" rx="1" fill="#d4a017"/>\n'
        left_end = 192 if lifted else 247
        o += f'  <path d="M{x0 + 143} 160 H{x0 + 125} V{left_end} M{x0 + 227} 160 H{x0 + 245} V247" stroke="#aab2bd" stroke-width="4" fill="none" stroke-linejoin="round" stroke-linecap="round"/>\n'
        solder = [x0 + 245] if lifted else [x0 + 125, x0 + 245]
        for px in solder:
            o += f'  <path d="M{px - 11} 205 L{px - 3} 196 H{px + 3} L{px + 11} 205 Z M{px - 11} 241 L{px - 3} 250 H{px + 3} L{px + 11} 241 Z" fill="#c9d0d9" stroke="#8b949e"/>\n'
        if lifted:
            o += f'  <rect x="{x0 + 122}" y="207" width="6" height="32" fill="#0d3b26"/>\n'
            o += f'  <path d="M{x0 + 125} 203 V196" stroke="#aab2bd" stroke-width="2" stroke-dasharray="2 3"/>\n'
            o += text(x0 + 135, 202, "↑ levée", "ok", 11, weight=700)
        o += res_h(x0 + 143, x0 + 227, 160)
        m, (_, com, v) = meter(x0 + 122, 280, 0.7, "20k", lcd, "kΩ")
        o += m
        p, e = probe(x0 + 125, 178, -0.55, -0.83, False)
        o += (
            lead(
                com,
                f"V500 C{com[0]:.1f} 532 {x0 + 28} 536 {x0 + 28} 450 V200 C{x0 + 28} 150 {x0 + 60} {e[1]:.1f} {e[0]:.1f} {e[1]:.1f}",
                False,
            )
            + p
        )
        p, e = probe(x0 + 245, 178, 0.55, -0.83, True)
        o += (
            lead(
                v,
                f"V500 C{v[0]:.1f} 532 {x0 + 342} 536 {x0 + 342} 450 V200 C{x0 + 342} 150 {x0 + 310} {e[1]:.1f} {e[0]:.1f} {e[1]:.1f}",
                True,
            )
            + p
        )
        o += text(x0 + 185, 268, verdict, "ok" if lifted else "no", 13, "middle", 700)
        return o

    b += half(
        0,
        False,
        "3.20",
        "Avant : les deux pattes soudées",
        "✗ 3,2 kΩ : R en parallèle avec le circuit",
    )
    b += half(
        380,
        True,
        "10.00",
        "Après : patte côté signal levée",
        "✓ 10 kΩ : la résistance seule",
    )
    b += text(
        24,
        548,
        "Lever la patte la plus facile à chauffer, pas celle du plan de masse ; poser la pointe sur la patte, pas sur la pastille.",
        "mut",
        12,
    )
    return svg(
        760,
        564,
        "Lever une patte pour isoler un composant",
        "Vue de côté d'une résistance traversante de 10 kΩ, multimètre sur ohms calibre 20 kΩ. "
        "À gauche, les deux pattes sont soudées : l'appareil lit 3,2 kΩ, la résistance en parallèle avec le reste du circuit. "
        "À droite, la patte côté signal est dessoudée et soulevée, la patte côté plan de masse reste soudée ; pointes sur les pattes et non sur les pastilles, l'appareil lit 10 kΩ, la résistance seule.",
        b,
    )


# ---------------------------------------------------------------- figure 4
def fig_drop() -> str:
    b = text(
        24,
        38,
        "Sous tension : la chute de tension aux bornes d'un contact",
        size=20,
        weight=700,
    )
    b += text(
        24,
        60,
        "Sélecteur sur V continu, carte alimentée par une alimentation limitée en courant",
        "mut",
        14,
    )
    m, (_, com, v) = meter(30, 80, 1, "VDC", "0.012", "V")
    b += m
    for i, (col, s) in enumerate(
        (
            (
                "#16a34a",
                "quelques mV à dizaines de mV : sain (plus pour un fusible PTC)",
            ),
            (
                "#f59e0b",
                "plusieurs centaines de mV : contact résistant, fusible fatigué",
            ),
            ("#dc2626", "toute la tension d'alimentation : ouvert"),
        )
    ):
        y = 96 + i * 22
        b += (
            f'  <rect x="300" y="{y - 11}" width="14" height="14" rx="3" fill="{col}"/>\n'
            + text(322, y, s, "fg", 13)
        )
    y = 240
    b += f'  <rect class="panel" x="300" y="{y - 40}" width="90" height="80" rx="8" stroke-width="1.5"/>\n'
    b += (
        text(345, y - 6, "Alim. 12 V", "fg", 13, "middle", 700)
        + text(345, y + 12, "limitée", "mut", 11, "middle")
        + text(345, y + 26, "en courant", "mut", 11, "middle")
    )
    b += f'  <rect class="panel" x="640" y="{y - 40}" width="90" height="80" rx="8" stroke-width="1.5"/>\n'
    b += text(685, y + 5, "Charge", "fg", 13, "middle", 700)
    b += f'  <path class="wire" d="M390 {y} H470 M550 {y} H640"/>\n'
    # glass fuse
    b += f'  <rect x="470" y="{y - 11}" width="80" height="22" rx="5" fill="#dbeafe" fill-opacity="0.55" stroke="#8b949e"/>\n'
    b += f'  <path d="M482 {y} C500 {y - 7} 520 {y + 7} 538 {y}" stroke="#6b7482" stroke-width="1.5" fill="none"/>\n'
    b += f'  <rect x="466" y="{y - 13}" width="16" height="26" rx="3" fill="#c9d0d9" stroke="#8b949e"/><rect x="538" y="{y - 13}" width="16" height="26" rx="3" fill="#c9d0d9" stroke="#8b949e"/>\n'
    b += text(510, y - 22, "fusible", "fg", 13, "middle", 700)
    b += f'  <path class="flow fb" d="M398 {y - 9} H458 M562 {y - 9} H632"/>\n'
    b += text(428, y - 18, "I →", "blue", 12, "middle", 700) + text(
        597, y - 18, "I →", "blue", 12, "middle", 700
    )
    p, e = probe(460, y + 2, -0.4, 0.92, True)
    b += lead(v, f"V394 C165 430 {e[0]:.1f} 440 {e[0]:.1f} {e[1]:.1f}", True) + p
    p, e = probe(560, y + 2, 0.4, 0.92, False)
    b += lead(com, f"V398 C120 462 {e[0]:.1f} 470 {e[0]:.1f} {e[1]:.1f}", False) + p
    b += text(444, y + 22, "+", "no", 16, "end", 700) + text(
        578, y + 22, "−", "fg", 16, weight=700
    )
    b += (
        text(612, 330, "Les chemins parallèles", "mut", 12)
        + text(612, 346, "ne gênent pas : on lit", "mut", 12)
        + text(612, 362, "la tension réelle.", "mut", 12)
    )
    return svg(
        760,
        470,
        "Mesurer la chute de tension aux bornes d'un fusible sous tension",
        "Un multimètre, sélecteur sur volts continus, a sa pointe rouge côté alimentation et sa pointe noire côté charge d'un fusible parcouru par le courant. "
        "Il lit 0,012 V. Quelques millivolts à quelques dizaines de millivolts : contact ou fusible sain ; plusieurs centaines de millivolts : contact résistant ou fusible fatigué ; "
        "toute la tension d'alimentation : ouvert.",
        b,
    )


FIGURES = {
    "chemins-paralleles": (fig_parallel, ["20k"]),
    "jonction-calibre": (fig_junction, ["20k", "200k"]),
    "lever-une-patte": (fig_lift, ["20k", "20k"]),
    "chute-de-tension": (fig_drop, ["VDC"]),
}
