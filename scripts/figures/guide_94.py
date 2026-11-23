"""Figures of guide 94, diagnosing a resistive temperature (PT1000) input channel (#162)."""

from __future__ import annotations

import math

from elements import (
    Point,
    box,
    chart,
    curve,
    half_meter,
    heading,
    hookup,
    res_h,
    screen,
    svg,
    text,
    verdict,
)

PT1000_ALPHA = 3.85  # Ω per °C around 0 °C (IEC 60751, α = 0.00385)


def pt1000_celsius(ohms: float) -> float:
    """Temperature read by a linear PT1000 conversion: 1000 Ω at 0 °C, 3.85 Ω/°C."""
    return (ohms - 1000) / PT1000_ALPHA


def header(
    x: float, y: float, label: str, pins: tuple[str, str] = ("a", "b")
) -> tuple[str, Point, Point]:
    """2-pin header seen from above, top-left at (x, y); returns (svg, pin 1 centre, pin 2 centre)."""
    o = f'  <rect x="{x}" y="{y}" width="92" height="46" rx="4" fill="#f4f1e8" stroke="#8a8577" stroke-width="1.5"/>\n'
    centres = []
    for i, name in enumerate(pins):
        cx, cy = x + 24 + 44 * i, y + 23
        o += f'  <rect x="{cx - 13}" y="{cy - 13}" width="26" height="26" fill="#3b3b3b"/>\n'
        o += f'  <rect x="{cx - 5}" y="{cy - 5}" width="10" height="10" fill="#d4af37"/>\n'
        o += text(cx, y - 8, name, "fg", 13, "middle", 700)
        centres.append((cx, cy))
    o += text(x + 46, y - 28, label, "mut", 12, "middle")
    return o, centres[0], centres[1]


# ---------------------------------------------------------------- figure 1
def fig_substitution() -> str:
    b = heading(
        "Remplacer la sonde par une résistance connue",
        "Carte sous tension : une résistance précise à la place de la PT1000 isole la sonde et son câble de la carte",
    )
    h, (xa, ya), (xb, yb) = header(80, 150, "")
    b += h + text(126, 236, "connecteur TEMP", "mut", 12, "middle")
    b += f'  <path class="wire" d="M{xa} {ya} V{ya - 40} H{xa - 30} M{xb} {yb} V{yb - 40} H{xb + 30}"/>\n'
    b += res_h(xa - 30, xb + 30, ya - 40, 20)
    b += text((xa + xb) / 2, ya - 64, "1 000 Ω · 0,1 %", "blue", 13, "middle", 700)
    b += box(250, 140, 150, 66, "Carte", ("lit la voie", "comme une sonde"))
    b += f'  <path class="wire" d="M{xb + 46} {yb} H250"/>\n'
    b += text(440, 120, "Résistance injectée → lecture attendue", size=15, weight=700)
    for i, ohms in enumerate((1000, 1100, 1385)):
        y = 152 + 30 * i
        b += text(460, y, f"{ohms} Ω", "fg", 13, weight=700)
        b += text(560, y, f"≈ {pt1000_celsius(ohms):.0f} °C", "blue", 13, weight=700)
    b += text(440, 260, "Boîte à décades : balayer la plage utile.", "mut", 12)
    b += verdict(
        220,
        300,
        "✓ lecture juste : sonde ou câble en cause",
        "remettre la sonde, la changer",
        "ok",
    )
    b += verdict(
        220,
        350,
        "✗ lecture fausse ou défaut : la voie de la carte",
        "suivre la voie jusqu'à l'ADC",
        "no",
    )
    b += text(
        24,
        404,
        "Essai bref, élément chauffant débranché : la protection thermique est neutralisée pendant l'essai.",
        "mut",
        12,
    )
    return svg(
        760,
        430,
        "Substitution d'une sonde PT1000 par une résistance connue",
        "Une résistance de 1 000 Ω à 0,1 % est branchée à la place de la sonde PT1000 sur le connecteur 2 broches TEMP, carte sous tension. "
        "Lectures attendues : 1 000 Ω donne 0 °C, 1 100 Ω environ 26 °C, 1 385 Ω environ 100 °C ; une boîte à décades balaie la plage. "
        "Lecture juste : la sonde ou son câble est en cause. Lecture fausse ou défaut maintenu : la voie de la carte est en cause. Essai bref, élément chauffant débranché : la protection thermique est neutralisée pendant l'essai.",
        b,
    )


# ---------------------------------------------------------------- figure 2
def _pin_panel(
    x0: float,
    sel: str,
    lcd: str,
    unit: str,
    title: str,
    notes: tuple[str, ...],
    red_on_pin: bool,
) -> str:
    """Half panel: a meter, an input pin and a ground pad; the red probe on the pin or on ground.

    The red tip always lands on the left point (see `hookup`), so the pin and the pad swap places.
    """
    o, v, com = half_meter(x0, sel, lcd, unit, title, notes)
    left, right = (x0 + 245, 300), (x0 + 330, 300)
    pin, gnd = (left, right) if red_on_pin else (right, left)
    o += _pin(pin, "broche") + _pad(gnd, "masse")
    return o + hookup(v, com, left, right)


def _pin(at: Point, label: str) -> str:
    """Round plated pin with its label under it."""
    return (
        f'  <circle cx="{at[0]}" cy="{at[1]}" r="9" fill="#d4af37" stroke="#8a6d1c"/>\n'
        + text(at[0], at[1] - 20, label, "fg", 12, "middle", 700)
    )


def _pad(at: Point, label: str) -> str:
    """Rectangular ground pad with its label under it."""
    return (
        f'  <rect x="{at[0] - 14}" y="{at[1] - 9}" width="28" height="18" fill="#9aa3ad"/>\n'
        + text(at[0], at[1] - 20, label, "fg", 12, "middle", 700)
    )


def fig_ohm_polarities() -> str:
    b = heading(
        "Résistance d'une broche à la masse, dans les deux sens",
        "Carte hors tension et déchargée, sélecteur sur Ω : mesurer, puis inverser les pointes",
    )
    b += _pin_panel(
        0,
        "20k",
        "4.72",
        "kΩ",
        "Rouge sur la broche",
        ("Le courant de l'ohmmètre", "bloque la diode de", "protection."),
        True,
    )
    b += _pin_panel(
        380,
        "20k",
        "1.18",
        "kΩ",
        "Rouge sur la masse",
        ("La diode de protection", "conduit un peu : la", "lecture chute."),
        False,
    )
    b += verdict(
        380,
        505,
        "Deux lectures différentes : une jonction est en parallèle",
        "ce n'est pas un défaut, c'est la protection de l'entrée",
        "warn",
    )
    b += text(
        380,
        548,
        "Comparer chaque sens à la même broche d'une voie jumelle, jamais à une valeur théorique.",
        "fg",
        13,
        "middle",
        700,
    )
    return svg(
        760,
        570,
        "Mesure de la résistance d'une broche à la masse dans les deux polarités",
        "Carte hors tension et déchargée, multimètre sur ohms calibre 20 kΩ. "
        "À gauche, pointe rouge sur la broche d'entrée et pointe noire sur la masse : 4,72 kΩ, la diode de protection est bloquée. "
        "À droite, pointes inversées : 1,18 kΩ, la diode conduit un peu et la lecture chute. "
        "Deux lectures différentes signalent une jonction en parallèle, la protection de l'entrée, pas un défaut. "
        "Chaque sens se compare à la même broche d'une voie jumelle.",
        b,
    )


# ---------------------------------------------------------------- figure 3
def fig_diode_mode() -> str:
    b = heading(
        "Mode diode sur une broche d'entrée",
        "Carte hors tension : la diode de protection vers la masse se voit d'un côté seulement",
    )
    b += _pin_panel(
        0,
        "DIODE",
        "0.58",
        "V",
        "Rouge sur la masse",
        ("Diode de protection", "passante : 0,5 à 0,7 V."),
        False,
    )
    b += _pin_panel(
        380,
        "DIODE",
        "OL",
        "V",
        "Rouge sur la broche",
        ("Diode bloquée : valeur", "haute ou OL, comme", "la voie jumelle."),
        True,
    )
    b += verdict(
        190,
        505,
        "✓ 0,5–0,7 V puis haute ou OL : saine",
        "comme sur la voie jumelle",
        "ok",
    )
    b += verdict(
        570,
        505,
        "✗ ≈ 0 V dans les deux sens",
        "protection ou entrée en court-circuit",
        "no",
    )
    return svg(
        760,
        545,
        "Mode diode sur une broche d'entrée : protection passante dans un seul sens",
        "Carte hors tension, multimètre en mode diode. "
        "À gauche, pointe rouge sur la masse et pointe noire sur la broche : 0,58 V, la diode de protection vers la masse conduit. "
        "À droite, pointes inversées : OL ou une valeur haute, la diode est bloquée. "
        "Entre 0,5 et 0,7 V puis une valeur haute ou OL, comme sur la voie jumelle : protection saine. "
        "Environ 0 V dans les deux sens : protection ou entrée en court-circuit.",
        b,
    )


# ---------------------------------------------------------------- figure 4, excitation-pulsee
def pulses(
    cols: int = 8, period: float = 2, duty: float = 0.25, high: float = 3
) -> list[Point]:
    """Excitation pulses in divisions: `high` for `duty` of each period, 0.4 division otherwise."""
    pts: list[Point] = [(0, 0.4)]
    t = 0.0
    while t < cols:
        on = min(t + period * duty, cols)
        pts += [(t, 0.4), (t, high), (on, high), (on, 0.4)]
        t += period
    return [*pts, (cols, 0.4)]


def fig_pulsed() -> str:
    b = heading(
        "Excitation pulsée : le multimètre moyenne, l'oscilloscope montre",
        "Carte sous tension, sonde branchée : la voie n'est alimentée que pendant la conversion",
    )
    o, v, com = half_meter(
        0,
        "VDC",
        "0.45",
        "V",
        "Multimètre : une valeur qui saute",
        ("Il affiche une moyenne", "de quelques impulsions :", "0,4… 0,5… 0,45 V."),
    )
    b += o
    pin, gnd = (245, 300), (330, 300)
    b += _pin(pin, "broche") + _pad(gnd, "masse")
    b += hookup(v, com, pin, gnd)
    b += text(400, 100, "Oscilloscope : la vraie forme", size=15, weight=700)
    b += screen(400, 116, 320, 200, 8, 5, pulses())
    b += text(
        400, 336, "Impulsion ≈ 1,2 V pendant la mesure, ≈ 0,2 V entre deux.", "mut", 12
    )
    b += text(
        400,
        354,
        "Source commutée d'une voie à l'autre : un créneau par voie.",
        "mut",
        12,
    )
    b += verdict(
        380,
        505,
        "Lire le plateau de l'impulsion, pas la moyenne",
        "et le comparer au même plateau sur la voie jumelle",
        "blue",
    )
    return svg(
        760,
        545,
        "Excitation pulsée d'une sonde : lecture instable au multimètre, forme réelle à l'oscilloscope",
        "Carte sous tension, sonde branchée, la voie n'est alimentée que pendant la conversion. "
        "À gauche, un multimètre sur volts continus entre la broche et la masse affiche une valeur qui saute, 0,4, 0,5, 0,45 V : il moyenne quelques impulsions. "
        "À droite, l'écran d'oscilloscope montre des impulsions rectangulaires d'environ 1,2 V pendant la mesure et 0,2 V entre deux ; "
        "quand la source de courant est commutée d'une voie à l'autre, chaque voie a son créneau. On lit le plateau de l'impulsion et on le compare à la voie jumelle.",
        b,
    )


# ---------------------------------------------------------------- figure 5, broche-de-masse
def fig_ground_pin() -> str:
    b = heading(
        "Trouver la broche de masse d'un connecteur 2 broches",
        "Carte hors tension, sélecteur sur continuité : pointe noire sur un trou de fixation métallisé",
    )
    o, v, com = half_meter(
        0,
        "BEEP",
        "0.3",
        "Ω",
        "La broche qui bipe est la masse",
        ("Pointe rouge sur", "chaque broche,", "l'une après l'autre."),
        "•)))",
    )
    b += o
    h, (xa, ya), (xb, yb) = header(225, 225, "TEMP")
    b += h
    hole = (345, 300)
    b += f'  <circle cx="{hole[0]}" cy="{hole[1]}" r="14" fill="#d4af37" stroke="#8a6d1c" stroke-width="2"/><circle cx="{hole[0]}" cy="{hole[1]}" r="7" fill="#20242b"/>\n'
    b += text(hole[0] + 20, 304, "trou de fixation", "mut", 11)
    b += hookup(v, com, (xb, yb), hole)
    b += text(420, 120, "Résultat", size=15, weight=700)
    for i, (cls, head, sub) in enumerate(
        (
            ("ok", "b : bip, ≈ 0 Ω", "broche reliée à la masse"),
            ("mut", "a : pas de bip", "broche de mesure, vers le filtre"),
            ("warn", "aucune ne bipe", "masse isolée, ou sonde sur la référence"),
        )
    ):
        y = 150 + 46 * i
        b += text(420, y, head, cls, 13, weight=700)
        b += text(420, y + 17, sub, "mut", 12)
    b += text(420, 300, "Le trou de fixation est souvent la terre (PE),", "mut", 12)
    b += text(420, 316, "pas forcément le 0 V logique : vérifier", "mut", 12)
    b += text(420, 332, "aussi à la broche GND d'un circuit intégré.", "mut", 12)
    return svg(
        760,
        480,
        "Trouver la broche de masse d'un connecteur 2 broches au testeur de continuité",
        "Carte hors tension, multimètre en continuité, pointe noire sur un trou de fixation métallisé, pointe rouge sur chaque broche du connecteur TEMP. "
        "La broche b bipe, environ 0 Ω : c'est la masse. La broche a ne bipe pas : c'est la broche de mesure. "
        "Si aucune ne bipe, la masse logique est peut-être isolée du châssis, ou la sonde est montée sur une résistance de référence : le trou de fixation est souvent la terre, pas le 0 V logique ; "
        "vérifier aussi à la broche GND d'un circuit intégré.",
        b,
    )


# ---------------------------------------------------------------- figure 6, trace-multiplexeur
TSSOP16 = {
    3: "1S4",
    4: "1S3",
    5: "1S2",
    6: "1S1",
    8: "GND",
    10: "2S1",
    11: "2S2",
    12: "2S3",
    13: "2S4",
}


def tssop16(cx: float, cy: float) -> tuple[str, dict[int, Point]]:
    """TSSOP-16 seen from above, pin 1 bottom left beside the dot; returns (svg, pin tips by number)."""
    o = f'  <rect x="{cx - 80}" y="{cy - 30}" width="160" height="60" rx="3" fill="#20242b" stroke="#7d8794"/>\n'
    o += f'  <circle cx="{cx - 66}" cy="{cy + 16}" r="4" fill="#5f6b7a"/>\n'
    o += f'  <text x="{cx}" y="{cy + 5}" font-size="12" font-weight="700" text-anchor="middle" fill="#ffffff">TS3A5017</text>\n'
    tips: dict[int, Point] = {}
    for i in range(8):
        x = cx - 70 + 20 * i
        for n, y0, dy in ((i + 1, cy + 30, 14), (16 - i, cy - 30, -14)):
            o += f'  <rect x="{x - 3}" y="{min(y0, y0 + dy)}" width="6" height="14" fill="#c9d0d9"/>\n'
            tips[n] = (x, y0 + dy)
            if n in TSSOP16:
                o += text(
                    x, y0 + dy + (16 if dy > 0 else -6), TSSOP16[n], "mut", 9, "middle"
                )
    o += text(cx - 70, cy + 70, "1", "no", 12, "middle", 700)
    return o, tips


def fig_mux_trace() -> str:
    b = heading(
        "Suivre une piste du connecteur jusqu'au multiplexeur",
        "Hors tension, continuité : une pointe sur le connecteur, l'autre promenée sur les entrées du multiplexeur",
    )
    o, v, com = half_meter(
        0,
        "BEEP",
        "1.2",
        "Ω",
        "Bip sur 1S2 : la voie TEMP 2",
        ("Entrées 1S1–1S4 :", "broches 6 à 3 ;", "2S1–2S4 : 10 à 13."),
        "•)))",
    )
    b += o
    h, (xa, ya), _ = header(212, 300, "TEMP 2")
    b += h
    m, tips = tssop16(560, 250)
    b += m
    b += hookup(v, com, (xa, ya), tips[5], 0.2)
    b += text(400, 120, "Broche 1 : le point ou le chanfrein du boîtier,", "mut", 12)
    b += text(400, 136, "et le point sérigraphié à côté ; puis on compte", "mut", 12)
    b += text(400, 152, "en sens inverse des aiguilles d'une montre.", "mut", 12)
    b += text(
        24,
        505,
        "Continuité pour suivre une piste ; mode diode pour comparer deux voies (les jonctions comptent).",
        "fg",
        13,
        weight=700,
    )
    b += text(
        24,
        525,
        "Pas de bip : passer sur Ω, une résistance série de protection (1 à 10 kΩ) est normale.",
        "mut",
        12,
    )
    return svg(
        760,
        545,
        "Tracer la continuité d'un connecteur 2 broches vers un multiplexeur analogique TS3A5017",
        "Carte hors tension, multimètre en continuité. Une pointe sur la broche de mesure du connecteur TEMP 2, l'autre promenée sur les broches 3 à 6 (1S4 à 1S1) "
        "et 10 à 13 (2S1 à 2S4) d'un TS3A5017 en boîtier TSSOP-16 ; le bip sur 1S2, broche 5, désigne la voie. "
        "La broche 1 se trouve au point ou au chanfrein du boîtier et au point sérigraphié, puis on compte en sens inverse des aiguilles d'une montre. "
        "La continuité suit une piste ; le mode diode compare deux voies. Pas de bip : passer sur ohms, une résistance série de protection de 1 à 10 kΩ est normale.",
        b,
    )


# ---------------------------------------------------------------- figure 7, noeud-filtre-ohm
def rc_ohms(t: float, r: float = 100_000, tau: float = 1) -> float:
    """Apparent resistance of a node holding a capacitor, `t` seconds after the probes touch.

    The ohmmeter's test current first charges the capacitor: τ = R · C, 1 s for 100 kΩ and 10 µF.
    """
    return r * (1 - math.exp(-t / tau))


def fig_cap_rising() -> str:
    b = heading(
        "Une lecture qui monte : un gros condensateur sur le nœud",
        "Carte hors tension : l'ohmmètre charge d'abord le condensateur, attendre que la valeur se stabilise",
    )
    o, v, com = half_meter(
        0,
        "200k",
        "86.5",
        "kΩ",
        "Après 2 s : 86,5 kΩ et ça monte",
        ("100 kΩ et 10 µF :", "τ = R·C = 1 s, stable", "après 5 s environ."),
    )
    b += o
    node, gnd = (245, 300), (330, 300)
    b += _pin(node, "nœud") + _pad(gnd, "masse")
    b += hookup(v, com, node, gnd)
    x0, y0, w, h = 430, 300, 290, 190
    c, at = chart(
        x0,
        y0 - h,
        w,
        h,
        6,
        110,
        [(t, f"{t} s") for t in (0, 2, 4, 6)],
        [(50, "50"), (100, "100")],
        "temps après le contact",
        "lecture (kΩ)",
    )
    b += c + curve([at(t / 10, rc_ohms(t / 10) / 1000) for t in range(61)], "fb")
    b += verdict(
        380,
        505,
        "Lire la valeur stable : ici 100 kΩ",
        "le filtre d'une entrée de sonde (nF à µF) se charge en moins d'1 ms : lecture immédiate",
        "blue",
    )
    return svg(
        760,
        545,
        "Lecture d'ohmmètre qui monte sur un nœud chargé par un gros condensateur",
        "Carte hors tension, multimètre sur ohms calibre 200 kΩ entre un nœud et la masse ; le nœud porte 100 kΩ et un condensateur de 10 µF, soit τ = 1 s. "
        "Le courant de l'ohmmètre charge d'abord le condensateur : la lecture part de zéro, vaut 86,5 kΩ après 2 s et se stabilise à 100 kΩ après 5 s environ. "
        "Lire la valeur stable. Le filtre d'une entrée de sonde, de quelques nanofarads à un microfarad, se charge en moins d'une milliseconde : sa lecture est immédiate.",
        b,
    )


# ---------------------------------------------------------------- family 2: compare twin channels
# Field data (bare board, 2026-11-23): pin b to ground on the four channels; TEMP 1 and 2 are the
# two sensors of the same hose, so they are twins.
TWINS = (("TEMP 1", 995), ("TEMP 2", 1071), ("TEMP 3", 1000), ("TEMP 4", 1025))
R_NOMINAL = 1000  # reference resistor the firmware assumes


def fr(value: float, sign: bool = False) -> str:
    """French number: narrow thousands space, true minus sign (1 071, −1, +18)."""
    out = f"{value:+,.0f}" if sign else f"{value:,.0f}"
    if round(value) == 0:
        return "0"
    return out.replace(",", "\u202f").replace("-", "−")


def drift_percent(actual: float, assumed: float = R_NOMINAL) -> float:
    """Drift of a resistor from the value it should have, in percent."""
    return (actual / assumed - 1) * 100


def odd_one_out(readings: tuple[tuple[str, float], ...]) -> str:
    """Name of the channel furthest from the median of all the channels."""
    values = sorted(v for _, v in readings)
    mid = len(values) // 2
    median = values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2
    return max(readings, key=lambda nv: abs(nv[1] - median))[0]


def reference_error(actual: float, assumed: float = R_NOMINAL) -> float:
    """Temperature error (°C) of a current-source channel whose series reference drifted.

    The channel reads V = I · (R_PT1000 + R_ref) and subtracts the assumed R_ref: the whole drift
    lands on the sensor reading.
    """
    return (actual - assumed) / PT1000_ALPHA


def fig_twin_table() -> str:
    b = heading(
        "Comparer les voies jumelles : l'intruse désigne la panne",
        "Carte déposée, hors tension : la même mesure, broche b → masse, sur chaque voie identique",
    )
    x0, base, scale = 60, 400, 1.5  # bars start at 900 Ω
    suspect = odd_one_out(TWINS)
    for i, (name, ohms) in enumerate(TWINS):
        x = x0 + 120 * i
        h = (ohms - 900) * scale
        cls = "no" if name == suspect else "ok"
        b += f'  <rect class="{cls}" x="{x}" y="{base - h:.1f}" width="70" height="{h:.1f}" rx="4"/>\n'
        b += text(x + 35, base - h - 8, f"{fr(ohms)} Ω", cls, 14, "middle", 700)
        b += text(x + 35, base + 20, name, "fg", 13, "middle", 700)
    b += f'  <path class="grid" d="M{x0 - 10} {base - 100 * scale} H{x0 + 480}"/>\n'
    b += text(x0 - 14, base - 100 * scale + 4, "1 000", "mut", 11, "end")
    b += text(x0 - 10, base + 44, "Échelle à partir de 900 Ω", "mut", 11)
    gap = reference_error(1071) - reference_error(995)
    for i, (line, cls, weight) in enumerate(
        (
            ("Lecture", "fg", 700),
            ("TEMP 1 et TEMP 2 : même", "fg", 400),
            ("tuyau, même lecture attendue.", "fg", 400),
            (
                f"{fr(TWINS[1][1])} − {fr(TWINS[0][1])} = {fr(TWINS[1][1] - TWINS[0][1])} Ω",
                "no",
                700,
            ),
            (f"≈ {fr(gap)} °C de PT1000", "no", 700),
            ("TEMP 2 : l'intruse.", "no", 700),
            (
                f"TEMP 4 : {drift_percent(TWINS[3][1]):+.1f} % sur 1 000 Ω,".replace(
                    ".", ","
                ),
                "mut",
                400,
            ),
            ("second suspect, à relire", "mut", 400),
            ("après la réparation.", "mut", 400),
        )
    ):
        b += text(
            570,
            120 + 20 * i + (6 if i else 0),
            line,
            cls,
            15 if i == 0 else 12,
            weight=weight,
        )
    b += verdict(
        380,
        470,
        "Mesurer dans les deux sens, comparer sens par sens",
        "en circuit, l'ohmmètre voit aussi les chemins en parallèle",
        "blue",
    )
    return svg(
        760,
        510,
        "Tableau de comparaison de quatre voies jumelles : la voie intruse",
        "Sur une carte déposée, hors tension, la résistance de la broche b à la masse est mesurée sur quatre voies identiques : "
        "TEMP 1 995 Ω, TEMP 2 1 071 Ω, TEMP 3 1 000 Ω, TEMP 4 1 025 Ω. TEMP 1 et TEMP 2 sont les deux sondes du même tuyau et doivent lire pareil ; "
        "leur écart de 76 Ω vaut environ 20 °C de PT1000. TEMP 2 est l'intruse. TEMP 4, 2,5 % au-dessus de 1 000 Ω, est un second suspect à relire après la réparation. "
        "En circuit l'ohmmètre voit aussi les chemins en parallèle : mesurer dans les deux sens et comparer sens par sens.",
        b,
    )


def ratiometric_error(
    actual: float, sensor: float = 1078, assumed: float = R_NOMINAL
) -> float:
    """Temperature error (°C) of a ratiometric channel (TI SBAA275A) whose reference drifted.

    The ADC reads R_PT1000 / R_ref and multiplies by the assumed R_ref: a reference that rises
    makes the sensor read cold.
    """
    return (sensor * assumed / actual - sensor) / PT1000_ALPHA


def fig_drift() -> str:
    pct = fr(drift_percent(1071))
    b = heading(
        f"Une référence qui dérive de {pct} % : 18 à 19 °C d'erreur",
        "Hypothèse de voie : PT1000 entre a et b, référence R25 de b à la masse ; le sens de l'erreur dépend de la lecture",
    )
    x = 150
    b += box(x - 60, 90, 120, 44, "Excitation", ())
    b += f'  <path class="wire" d="M{x} 134 V170 M{x} 230 V270 M{x} 330 V350 M{x - 14} 350 h28 M{x - 9} 356 h18 M{x - 4} 362 h8 M{x} 160 H280"/>\n'
    b += f'  <rect x="{x - 14}" y="170" width="28" height="60" rx="4" fill="#8fbfe0" stroke="#3f6f96" stroke-width="1.5"/>\n'
    b += text(x + 24, 196, "PT1000", "blue", 13, weight=700)
    b += text(x + 24, 212, "sonde, entre a et b", "mut", 11)
    b += f'  <rect x="{x - 14}" y="270" width="28" height="60" rx="4" fill="#d9b88c" stroke="#8a6d45" stroke-width="1.5"/>\n'
    b += text(x + 24, 296, "R réf. (R25)", "no", 13, weight=700)
    b += text(x + 24, 312, "1 000 Ω prévue", "mut", 11)
    b += text(x - 22, 164, "a", "fg", 13, "end", 700) + text(
        x - 22, 254, "b", "fg", 13, "end", 700
    )
    b += text(x + 24, 254, "b → réf. ADC si ratiométrique", "mut", 11)
    b += text(286, 156, "→ filtre,", "mut", 12) + text(286, 172, "mux, ADC", "mut", 12)
    b += text(24, 400, "Sonde à 20 °C ≈ 1 078 Ω", "fg", 13, weight=700)
    b += text(
        24,
        420,
        "Le menu de service dit quel cas : TEMP 2 lit-elle chaud ou froid ?",
        "mut",
        12,
    )
    cases = (
        (
            "Source de courant, V(a) seule",
            "le logiciel retranche 1 000 Ω",
            reference_error,
        ),
        (
            "Ratiométrique (le plus courant)",
            "rapport R PT1000 / R réf. (TI SBAA275A)",
            ratiometric_error,
        ),
    )
    for i, (title, how, model) in enumerate(cases):
        y = 110 + 140 * i
        b += text(400, y, title, size=14, weight=700)
        b += text(400, y + 18, how, "mut", 11)
        for j, (label, ref) in enumerate(
            (("voie saine, 995 Ω", 995), ("TEMP 2, 1 071 Ω", 1071))
        ):
            e = model(ref)
            b += text(
                400,
                y + 42 + 20 * j,
                f"{label} : {fr(e, True)} °C",
                "ok" if abs(e) < 2 else "no",
                13,
                weight=700,
            )
        gap = abs(model(1071) - model(995))
        b += text(
            400,
            y + 102,
            f"TEMP 2 lit {'chaud' if model(1071) > 0 else 'froid'} ; écart ≈ {fr(gap)} °C",
            "no",
            12,
            weight=700,
        )
    b += text(
        24,
        470,
        "Dans les deux cas l'écart entre les sondes du tuyau déclenche le défaut d'écart : la dérive passe dans la lecture.",
        "mut",
        12,
    )
    return svg(
        760,
        500,
        "Comment une dérive de 7 % de la résistance de référence devient 18 à 19 °C d'erreur",
        "Hypothèse de voie : la PT1000 entre les broches a et b, la résistance de référence R25 de b à la masse ; la broche a part vers le filtre, le multiplexeur et l'ADC. "
        "Sonde à 20 °C, environ 1 078 Ω. Si la carte lit la tension de a seule et retranche 1 000 Ω, la voie saine à 995 Ω lit environ −1 °C de trop et TEMP 2 à 1 071 Ω environ +18 °C : TEMP 2 lit chaud. "
        "Si la carte lit le rapport des deux résistances, cas le plus courant, la voie saine lit environ +1 °C et TEMP 2 environ −19 °C : TEMP 2 lit froid. "
        "Dans les deux cas l'écart d'environ 20 °C entre les deux sondes du tuyau déclenche le défaut d'écart. Le menu de service dit quel cas s'applique.",
        b,
    )


def fig_swap() -> str:
    b = heading(
        "Échanger deux éléments identiques : la panne suit-elle ?",
        "Échange hors tension, bracelet antistatique ; relecture sur alimentation limitée, chauffage débranché",
    )
    rows = (
        (
            "Échanger les cartes filtre TFB1 ↔ TFB2",
            "Le défaut passe au tuyau 2",
            "la carte filtre est en cause",
            "Le défaut reste sur le tuyau 1",
            "la carte de commande ou les sondes",
        ),
        (
            "Échanger les fiches TEMP 1 ↔ TEMP 2",
            "La température fausse suit la sonde",
            "sonde ou câble (lire chaque voie, pas le code)",
            "La température fausse reste sur la voie",
            "la voie de la carte (ici : R25)",
        ),
    )
    for i, (title, follows, follows_sub, stays, stays_sub) in enumerate(rows):
        y = 100 + 180 * i
        b += text(24, y, title, size=15, weight=700)
        for cx, lab in ((150, "A"), (330, "B")):
            b += f'  <rect class="panel" x="{cx - 60}" y="{y + 20}" width="120" height="60" rx="8" stroke-width="1.5"/>\n'
            b += text(cx, y + 56, lab, "fg", 18, "middle", 700)
        b += f'  <path class="wire" d="M210 {y + 40} C230 {y + 20} 250 {y + 20} 270 {y + 40} M270 {y + 60} C250 {y + 80} 230 {y + 80} 210 {y + 60}"/>\n'
        b += text(240, y + 110, "échange", "mut", 12, "middle")
        b += text(440, y + 36, "✓ " + follows, "ok", 13, weight=700) + text(
            456, y + 54, follows_sub, "mut", 12
        )
        b += text(440, y + 88, "✗ " + stays, "no", 13, weight=700) + text(
            456, y + 106, stays_sub, "mut", 12
        )
    b += text(
        24,
        470,
        "Un échange à la fois, repéré et photographié ; jamais sur une panne qui détruit (court-circuit, fumée).",
        "fg",
        13,
        weight=700,
    )
    return svg(
        760,
        500,
        "Test d'échange de deux cartes filtre et de deux fiches de sondes",
        "Hors tension et bracelet antistatique pour chaque échange ; relecture sur alimentation limitée en courant, élément chauffant débranché. "
        "Premier test : échanger les deux cartes filtre identiques TFB1 et TFB2, puis relire le code défaut. "
        "Si le défaut passe du tuyau 1 au tuyau 2, la carte filtre est en cause ; s'il reste sur le tuyau 1, chercher sur la carte de commande ou les sondes. "
        "Second test : échanger les fiches TEMP 1 et TEMP 2 sur la carte de commande, puis lire la température de chaque voie, pas le code : un défaut d'écart entre les deux reste le même. "
        "Si la température fausse suit la sonde, la sonde ou son câble est en cause ; si elle reste sur la voie, la voie de la carte est en cause, ici la résistance R25. Un seul échange à la fois, jamais sur une panne destructrice.",
        b,
    )


FUNNEL = (
    ("Connecteur", "TEMP 2 broche b : 1 071 Ω", "jumelle TEMP 1 : 995 Ω"),
    (
        "Via, côté soudure",
        "TEMP 2 : 1 071 Ω, la piste est saine",
        "jumelle TEMP 1 : 995 Ω",
    ),
    ("Résistance", "R25 : 1 071 Ω", "jumelles R82, R24 : 994 Ω"),
)


def fig_funnel() -> str:
    b = heading(
        "L'entonnoir : du connecteur à la résistance qui a dérivé",
        "Carte hors tension : la même mesure, de plus en plus près du composant, sur la voie suspecte et sa jumelle",
    )
    for i, (stage, suspect, twin) in enumerate(FUNNEL):
        y = 100 + 110 * i
        inset = 40 * i
        b += f'  <path class="panel" d="M{40 + inset} {y} H{720 - inset} L{700 - inset} {y + 90} H{60 + inset} Z" stroke-width="1.5"/>\n'
        b += text(380, y + 30, f"{i + 1}. {stage}", "fg", 15, "middle", 700)
        b += text(380, y + 52, suspect, "no", 13, "middle", 700)
        b += text(380, y + 70, twin, "mut", 12, "middle")
    b += verdict(
        380,
        450,
        f"R25 : {fr(drift_percent(1071), True)} % sur 1 000 Ω ({fr(drift_percent(1071, 994), True)} % sur ses jumelles)",
        "lecture trop haute : un chemin parallèle ne peut que la baisser, R25 est en cause",
        "ok",
    )
    return svg(
        760,
        500,
        "Entonnoir de comparaison du connecteur à la résistance de référence",
        "Carte hors tension, la même mesure faite de plus en plus près du composant sur la voie suspecte et sur sa jumelle. "
        "Au connecteur : broche b de TEMP 2 à 1 071 Ω, TEMP 1 à 995 Ω. Au via, côté soudure : mêmes lectures, la piste est saine. "
        "Sur la résistance : R25 à 1 071 Ω, ses jumelles R82 et R24 à 994 Ω. R25 a dérivé de 7 % sur 1 000 Ω, 8 % sur ses jumelles. "
        "La lecture est trop haute : un chemin parallèle ne pouvant que la baisser, R25 est en cause.",
        b,
    )


FIGURES = {
    "substitution-sonde": (fig_substitution, []),
    "ohm-deux-polarites": (fig_ohm_polarities, ["20k", "20k"]),
    "mode-diode-entree": (fig_diode_mode, ["DIODE", "DIODE"]),
    "excitation-pulsee": (fig_pulsed, ["VDC"]),
    "broche-de-masse": (fig_ground_pin, ["BEEP"]),
    "trace-multiplexeur": (fig_mux_trace, ["BEEP"]),
    "noeud-filtre-ohm": (fig_cap_rising, ["200k"]),
    "comparaison-voies": (fig_twin_table, []),
    "derive-reference": (fig_drift, []),
    "test-echange": (fig_swap, []),
    "entonnoir-voie": (fig_funnel, []),
}
