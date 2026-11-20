"""Figures of guide 33, the electromechanical relay."""

from __future__ import annotations

from elements import (
    Point,
    box,
    diode_v,
    half_meter,
    heading,
    hookup,
    svg,
    text,
    verdict,
)

COIL_VOLTS = 5.0  # nominal coil voltage of the example relay
COIL_OHMS = 70.0  # its coil resistance, +/-10 % (datasheet)
OPERATE_PERCENT = 75  # the relay must operate at this share of the nominal voltage
CONTACT_MAX = 0.1  # ohm, initial contact resistance (datasheet, new contact)
TEST_VOLTS = 12.0  # contact test circuit
TEST_AMPS = 0.5
GOOD_DROP = 0.02  # volts across a healthy closed contact at TEST_AMPS
WORN_DROP = 0.60


def contact_resistance(drop: float, current: float) -> float:
    """Resistance of a closed contact from the voltage `drop` across it at `current` amperes."""
    if current <= 0:
        raise ValueError("the test current is positive")
    return drop / current


def must_operate(nominal: float, percent: float = OPERATE_PERCENT) -> float:
    """Coil voltage at which the relay must have operated."""
    return nominal * percent / 100


def _fr(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def _coil(x: float, top: float) -> str:
    """Coil symbol: a box on a vertical wire from top - 10 to top + 90."""
    return (
        f'  <path class="wire" d="M{x} {top - 10} V{top + 15} M{x} {top + 65} V{top + 90}"/>\n'
        f'  <path class="wire" d="M{x - 14} {top + 15} h28 v50 h-28 z"/>\n'
    )


def _symbol(cx: float, top: float, energised: bool) -> str:
    """Schematic of a changeover relay: coil on the left, contact on the right."""
    o = _coil(cx - 46, top)
    o += text(cx - 68, top + 2, "A1", "mut", 12, "end")
    o += text(cx - 68, top + 86, "A2", "mut", 12, "end")
    com, nc, no = (cx + 6, top + 40), (cx + 66, top + 15), (cx + 66, top + 65)
    tip = no if energised else nc
    o += f'  <g data-contact="{"no" if energised else "nc"}">\n'
    o += f'  <path class="wire" d="M{com[0]} {com[1]} L{tip[0] - 6} {tip[1] + (-3 if energised else 3)}"/>\n'
    o += "  </g>\n"
    o += f'  <path class="grid" d="M{cx - 32} {top + 40} H{cx + 2}"/>\n'
    for (x, y), name, dx, anchor in (
        (com, "COM", 0, "middle"),
        (nc, "NC", 12, "start"),
        (no, "NO", 12, "start"),
    ):
        o += f'  <circle class="blkf" cx="{x}" cy="{y}" r="4"/>\n'
        o += text(x + dx, y + (22 if name == "COM" else 4), name, "mut", 12, anchor)
    return o


def _relay(cx: float, cy: float) -> tuple[str, dict[str, Point]]:
    """Relay seen from the solder side, simplified: coil pads on top, contact pads below.

    Returns (svg, pad centres keyed "a1", "a2", "com", "no", "nc"). The layout is a teaching
    layout, not the pinout of a real part; each pad's name is printed on the body next to it.
    """
    pads = {
        "a1": (cx - 60, cy - 24),
        "a2": (cx + 60, cy - 24),
        "com": (cx - 60, cy + 24),
        "no": (cx + 60, cy + 24),
        "nc": (cx, cy + 52),
    }
    o = ""
    for px, py in pads.values():
        o += f'  <rect x="{px - 12}" y="{py - 12}" width="24" height="24" fill="#9aa3ad"/>\n'
    o += f'  <rect x="{cx - 50}" y="{cy - 44}" width="100" height="88" rx="6" fill="#20242b" stroke="#7d8794" stroke-width="1.5"/>\n'
    for label, x, y, anchor, weight in (
        ("A1", cx - 44, cy - 20, "start", 700),
        ("bobine", cx, cy - 20, "middle", 400),
        ("A2", cx + 44, cy - 20, "end", 700),
        ("COM", cx - 44, cy + 28, "start", 700),
        ("NO", cx + 44, cy + 28, "end", 700),
        ("NC", cx, cy + 38, "middle", 700),
    ):
        o += f'  <text x="{x}" y="{y}" font-size="11" font-weight="{weight}" text-anchor="{anchor}" fill="#ffffff">{label}</text>\n'
    return o, pads


# ---------------------------------------------------------------- figure 1
def fig_symbol() -> str:
    b = heading(
        "Relais : une bobine qui déplace un contact",
        "La bobine et le contact sont deux circuits séparés ; le contact inverseur a un commun, un repos, un travail",
    )
    for cx, title, energised in (
        (130, "Au repos", False),
        (380, "Bobine alimentée", True),
    ):
        b += text(cx, 100, title, size=15, weight=700, anchor="middle")
        b += _symbol(cx, 150, energised)
    b += text(130, 276, "le commun (COM) touche le contact", "mut", 12, "middle")
    b += text(130, 293, "de repos (NC)", "mut", 12, "middle")
    b += text(380, 276, "le commun (COM) passe sur le contact", "mut", 12, "middle")
    b += text(380, 293, "de travail (NO)", "mut", 12, "middle")
    b += text(630, 100, "Diode de roue libre", size=15, weight=700, anchor="middle")
    b += _coil(600, 150)
    b += diode_v(660, 140, 240, cathode_top=True)
    b += '  <path class="wire" d="M560 140 H660 M560 240 H660"/>\n'
    b += text(552, 145, "+", "mut", 15, "end", 700)
    b += text(552, 245, "−", "mut", 15, "end", 700)
    b += text(
        630, 276, "en parallèle sur la bobine, bague côté + :", "mut", 12, "middle"
    )
    b += text(630, 293, "elle absorbe la surtension à la coupure", "mut", 12, "middle")
    b += text(
        380,
        330,
        "Les noms des bornes (A1, A2, COM, NC, NO) et leur position se lisent sur la fiche technique du relais.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        352,
        "Symbole et contacts d'un relais",
        "Trois schémas d'un relais à contact inverseur : une bobine entre les bornes A1 et A2, et un contact à trois bornes, commun COM, repos NC, travail NO. "
        "À gauche, au repos : le commun touche le contact de repos. "
        "Au centre, bobine alimentée : le commun passe sur le contact de travail. "
        "À droite, une diode de roue libre en parallèle sur la bobine, bague du côté du plus : elle absorbe la surtension à la coupure. "
        "Les noms des bornes et leur position se lisent sur la fiche technique du relais.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def fig_coil() -> str:
    b = heading(
        "Deux contrôles de la bobine",
        f"Exemple : relais {COIL_VOLTS:.0f} V dont la fiche technique annonce une bobine de {COIL_OHMS:.0f} Ω à ±10 %",
    )
    b += '  <path class="grid" d="M380 84 V504"/>\n'
    floor = must_operate(COIL_VOLTS)
    for x0, sel, lcd, unit, title, notes, head, sub in (
        (
            0,
            "200",
            f"{COIL_OHMS:.1f}",
            "Ω",
            "Résistance, relais dessoudé",
            ("une pointe sur chaque", "borne de la bobine"),
            f"✓ {COIL_OHMS:.0f} Ω : bobine conforme",
            "OL : bobine coupée, relais à remplacer",
        ),
        (
            380,
            "VDC",
            f"{COIL_VOLTS - 0.02:.2f}",
            "V",
            "Tension, relais commandé",
            ("relais en place,", "carte sous tension"),
            f"✓ Au moins {_fr(floor)} V : le relais doit coller",
            "tension présente et relais inerte : relais suspect",
        ),
    ):
        o, v, com = half_meter(x0, sel, lcd, unit, title, notes)
        part, pads = _relay(x0 + 290, 250)
        b += o + part + hookup(v, com, pads["a1"], pads["a2"])
        b += verdict(x0 + 190, 478, head, sub, "ok")
    b += text(
        380,
        528,
        "Pas de tension à la bobine d'un relais commandé : la panne est en amont (commande, transistor, alimentation).",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        546,
        "Contrôler la bobine d'un relais",
        f"Deux mesures côte à côte sur la bobine d'un relais {COIL_VOLTS:.0f} volts, entre ses bornes A1 et A2. "
        f"À gauche, relais dessoudé, multimètre sur le calibre 200 ohms : {COIL_OHMS:.0f} ohms, conforme à la fiche technique ; OL signifierait une bobine coupée. "
        f"À droite, relais en place et commandé, carte sous tension, multimètre sur volts continus : {_fr(COIL_VOLTS - 0.02)} volts, au-dessus des {_fr(floor)} volts auxquels le relais doit avoir collé ; si le relais reste inerte, il est suspect. "
        "Sans tension à la bobine d'un relais commandé, la panne est en amont : commande, transistor, alimentation.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def fig_contact() -> str:
    ohms = TEST_VOLTS / TEST_AMPS
    b = heading(
        "Contrôler un contact fermé par sa chute de tension",
        f"Relais dessoudé, bobine alimentée à sa tension nominale, {_fr(TEST_AMPS, 1)} A imposé dans le contact COM–NO",
    )
    b += '  <path class="grid" d="M380 84 V504"/>\n'
    for x0, drop, title, head, sub, cls in (
        (
            0,
            GOOD_DROP,
            "Contact sain",
            f"✓ {_fr(GOOD_DROP)} V ÷ {_fr(TEST_AMPS, 1)} A = {contact_resistance(GOOD_DROP, TEST_AMPS) * 1000:.0f} mΩ",
            f"sous les {CONTACT_MAX * 1000:.0f} mΩ annoncés pour un contact neuf",
            "ok",
        ),
        (
            380,
            WORN_DROP,
            "Contact dégradé",
            f"✗ {_fr(WORN_DROP)} V ÷ {_fr(TEST_AMPS, 1)} A = {_fr(contact_resistance(WORN_DROP, TEST_AMPS), 1)} Ω",
            "contact usé ou encrassé : relais à remplacer",
            "no",
        ),
    ):
        o, v, com = half_meter(x0, "VDC", f"{drop:.2f}", "V", title, ())
        part, pads = _relay(x0 + 290, 250)
        b += o + box(
            x0 + 205,
            118,
            170,
            50,
            f"{TEST_VOLTS:.0f} V + {ohms:.0f} Ω",
            (f"{_fr(TEST_AMPS, 1)} A dans le contact",),
        )
        left, right = x0 + 211, x0 + 369
        b += f'  <path class="wire" d="M{left} 168 V{pads["com"][1]} H{pads["com"][0]} M{right} 168 V{pads["no"][1]} H{pads["no"][0]}"/>\n'
        b += part + hookup(v, com, pads["com"], pads["no"])
        b += verdict(x0 + 190, 478, head, sub, cls)
    b += text(
        380,
        528,
        "Un ohmmètre ne fait pas passer assez de courant pour juger un contact : mesurer la chute de tension sous courant.",
        "mut",
        12,
        "middle",
    )
    return svg(
        760,
        546,
        "Contrôler un contact de relais par sa chute de tension",
        f"Deux mesures côte à côte sur un relais dessoudé dont la bobine est alimentée à sa tension nominale. Une alimentation de {TEST_VOLTS:.0f} volts et une résistance de {ohms:.0f} ohms imposent {_fr(TEST_AMPS, 1)} ampère dans le contact fermé, entre les bornes COM et NO. "
        f"À gauche, multimètre sur volts continus, une pointe sur chaque borne du contact : {_fr(GOOD_DROP)} volt, soit {contact_resistance(GOOD_DROP, TEST_AMPS) * 1000:.0f} milliohms, sous les {CONTACT_MAX * 1000:.0f} milliohms annoncés pour un contact neuf. "
        f"À droite, même mesure sur un contact dégradé : {_fr(WORN_DROP)} volt, soit {_fr(contact_resistance(WORN_DROP, TEST_AMPS), 1)} ohm ; le contact est usé ou encrassé, le relais est à remplacer. "
        "Un ohmmètre ne fait pas passer assez de courant pour juger un contact : on mesure la chute de tension sous courant.",
        b,
    )


FIGURES = {
    "symbole-et-contacts": (fig_symbol, []),
    "controle-de-la-bobine": (fig_coil, ["200", "VDC"]),
    "chute-de-tension-du-contact": (fig_contact, ["VDC", "VDC"]),
}
