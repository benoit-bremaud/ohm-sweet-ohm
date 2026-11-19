"""Tests of the figure generator: the element library and every generated figure."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path

import pytest

import generate
import guide_01
from elements import (
    BAND_COLOURS,
    BAND_WIDTH,
    BLUE,
    POS,
    UNITS,
    band_offsets,
    bands,
    bench_supply,
    chart,
    chip,
    curve,
    dial_angle,
    half_meter,
    heading,
    hookup,
    meter,
    mlcc,
    probe,
    res_h,
    res_v,
    tile,
    verdict,
    winding,
)

SVG_NS = "{http://www.w3.org/2000/svg}"
FIGURES = [
    pytest.param(generate.ROOT / folder / f"{name}.svg", draw, positions, id=name)
    for folder, figures in generate.GUIDES.items()
    for name, (draw, positions) in figures.items()
]


@pytest.mark.parametrize("sel", POS)
def test_dial_points_at_the_selected_position(sel: str) -> None:
    drawing, _ = meter(0, 0, 1, sel, "0.00", sorted(UNITS[sel])[0])
    assert f'data-sel="{sel}"' in drawing
    assert f'transform="rotate({dial_angle(sel)} ' in drawing


def test_dial_positions_are_distinct_angles_within_one_turn() -> None:
    assert dial_angle(POS[0]) == 0
    angles = [dial_angle(sel) for sel in POS]
    assert len(set(angles)) == len(POS)
    assert max(angles) < 360


def test_unknown_dial_position_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown dial position"):
        meter(0, 0, 1, "10A", "0.00", "A")


@pytest.mark.parametrize(
    ("sel", "unit"), [("20k", "V"), ("ADC", "V"), ("VDC", "kΩ"), ("BEEP", "A")]
)
def test_unit_the_position_cannot_display_is_refused(sel: str, unit: str) -> None:
    with pytest.raises(ValueError, match="cannot be read"):
        meter(0, 0, 1, sel, "1.00", unit)


def test_meter_jacks_scale_and_keep_their_order() -> None:
    _, small = meter(10, 20, 1, "VDC", "0.00", "V")
    _, large = meter(10, 20, 2, "VDC", "0.00", "V")
    assert small.a[0] < small.com[0] < small.v[0]
    assert large.v[0] - 10 == pytest.approx(2 * (small.v[0] - 10))
    assert large.v[1] - 20 == pytest.approx(2 * (small.v[1] - 20))


def test_probe_cable_end_is_tip_plus_handle_away() -> None:
    _, (end_x, end_y) = probe(100, 100, 3, 4, red=True, tip=10, handle=40)
    assert (end_x, end_y) == pytest.approx((130, 140))


def test_probe_without_direction_is_refused() -> None:
    with pytest.raises(ValueError, match="null vector"):
        probe(0, 0, 0, 0, red=False)


def test_probe_with_a_handle_too_short_is_refused() -> None:
    with pytest.raises(ValueError, match="handle too short"):
        probe(0, 0, 1, 0, red=True, handle=23)


@pytest.mark.parametrize(("red", "colour"), [(True, "red"), (False, "black")])
def test_probe_records_its_colour(red: bool, colour: str) -> None:
    drawing, _ = probe(0, 0, 1, 0, red=red)
    assert f'data-probe="{colour}"' in drawing


@pytest.mark.parametrize("mode", ["CV", "CC"])
def test_bench_supply_records_its_mode(mode: str) -> None:
    drawing, minus, plus = bench_supply(0, 0, "5.00", "0.100", mode)
    assert f'data-mode="{mode}"' in drawing
    assert minus[0] < plus[0]


def test_bench_supply_unknown_mode_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown supply mode"):
        bench_supply(0, 0, "5.00", "0.100", "OFF")


def test_bands_translate_colour_names_in_reading_order() -> None:
    assert bands("brown", "black", "orange", "gold") == [
        BAND_COLOURS[name] for name in ("brown", "black", "orange", "gold")
    ]


@pytest.mark.parametrize("count", [3, 6])
def test_resistor_with_a_wrong_band_count_is_refused(count: int) -> None:
    with pytest.raises(ValueError, match="4 or 5 bands"):
        bands(*["red"] * count)


def test_unknown_band_colour_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown band colour"):
        bands("brown", "black", "pink", "gold")


@pytest.mark.parametrize("count", [4, 5])
def test_tolerance_band_stands_apart_and_every_band_fits_the_body(count: int) -> None:
    offsets = band_offsets(count)
    gaps = [b - a for a, b in zip(offsets, offsets[1:], strict=False)]
    assert len(offsets) == count
    assert gaps[-1] > max(gaps[:-1])
    assert offsets[0] > 0
    assert offsets[-1] + BAND_WIDTH < 1


@pytest.mark.parametrize("draw", [res_h, res_v])
def test_resistor_draws_its_bands_in_order(draw: Callable[..., str]) -> None:
    colours = bands("yellow", "violet", "black", "red", "brown")
    drawing = draw(0, 100, 50, colours=colours)
    found = re.findall(r'fill="(#[0-9a-f]{6})"', drawing)
    assert [c for c in found if c in colours] == colours


def test_resistor_body_colour_is_selectable() -> None:
    assert f'fill="{BLUE[0]}"' in res_h(0, 100, 50, body=BLUE)


def test_chip_prints_its_marking() -> None:
    assert ">4R7</text>" in chip(0, 0, "4R7")


def test_heading_prints_the_title_then_the_subtitle() -> None:
    drawing = heading("Titre", "Sous-titre")
    assert drawing.index(">Titre</text>") < drawing.index(">Sous-titre</text>")


def test_half_meter_and_hookup_draw_one_meter_with_its_probe_pair() -> None:
    drawing, v, com = half_meter(380, "BEEP", "OL", "Ω", "Rail sain", ["note"])
    assert 'data-sel="BEEP"' in drawing
    assert ">Rail sain</text>" in drawing and ">note</text>" in drawing
    assert 380 < com[0] < v[0] < 380 + 205  # jacks stay left of the part under test
    probes = re.findall(
        r'data-probe="(red|black)" transform="translate\(([\d.]+) ([\d.]+)\)',
        hookup(v, com, (600, 200), (700, 300)),
    )
    assert probes == [("red", "600.0", "200.0"), ("black", "700.0", "300.0")]


def test_verdict_prints_its_head_in_the_given_class_above_the_note() -> None:
    drawing = verdict(100, 50, "Court-circuit", "à localiser", "no")
    head, sub = drawing.strip().splitlines()
    assert 'class="no"' in head and ">Court-circuit</text>" in head
    assert 'class="mut"' in sub and ">à localiser</text>" in sub


def test_chart_maps_values_from_the_origin_to_the_far_corner() -> None:
    axes, at = chart(
        100, 50, 400, 200, 16, 100, [(8, "8 V")], [(50, "50 %")], "tension", "capacité"
    )
    assert at(0, 0) == pytest.approx((100, 250))  # y grows downwards in SVG
    assert at(16, 100) == pytest.approx((500, 50))
    assert at(8, 50) == pytest.approx((300, 150))
    for label in ("8 V", "50 %", "tension", "capacité"):
        assert f">{label}</text>" in axes


def test_curve_joins_its_points_in_order() -> None:
    drawing = curve([(0, 0), (10, 5), (20, 0)], "fr")
    assert 'class="fr"' in drawing
    assert 'd="M0.0 0.0 L10.0 5.0 L20.0 0.0"' in drawing
    assert "stroke-dasharray" not in drawing
    assert 'stroke-dasharray="6 4"' in curve([(0, 0), (1, 1)], "fb", dash="6 4")


def test_mlcc_terminations_follow_its_orientation() -> None:
    _, left, right = mlcc(100, 50, w=60)
    assert (left, right) == (pytest.approx((76, 50)), pytest.approx((124, 50)))
    _, top, bottom = mlcc(100, 50, w=60, vertical=True)
    assert (top, bottom) == (pytest.approx((100, 26)), pytest.approx((100, 74)))


def test_winding_spans_its_two_ends_and_bulges_on_the_asked_side() -> None:
    drawing = winding(100, 50, 130, loops=4)
    assert 'd="M100 50 ' in drawing
    assert drawing.count("a10 10 0 0 1 0 20") == 4  # 4 loops of 20 fill the 80 span
    assert winding(100, 50, 130, loops=2, right=False).count("a20 20 0 0 0 0 40") == 2


def test_winding_without_a_loop_is_refused() -> None:
    with pytest.raises(ValueError, match="one loop at least"):
        winding(0, 0, 10, loops=0)


def test_tile_prints_the_code_above_its_meaning() -> None:
    code, head, sub = (
        tile(10, 20, "47", "chiffres significatifs", "ici 47").strip().splitlines()[1:]
    )
    assert ">47</text>" in code
    assert 'class="blue"' in head and ">chiffres significatifs</text>" in head
    assert 'class="mut"' in sub and ">ici 47</text>" in sub


@pytest.mark.parametrize(("path", "draw", "positions"), FIGURES)
def test_figure_is_accessible_standalone_svg(path: Path, draw, positions) -> None:
    content = draw()
    root = ET.fromstring(content)  # well-formed XML
    assert root.tag == f"{SVG_NS}svg"
    assert root.get("role") == "img"
    assert (root.findtext(f"{SVG_NS}title") or "").strip()
    assert (root.findtext(f"{SVG_NS}desc") or "").strip()
    # nothing fetched or executed: the only URL is the SVG namespace
    assert re.findall(r"https?://[^\"'\s)]+", content) == ["http://www.w3.org/2000/svg"]
    for forbidden in ("href", "url(", "@import", "<image", "<script", "<foreignObject"):
        assert forbidden not in content


@pytest.mark.parametrize(("path", "draw", "positions"), FIGURES)
def test_figure_meters_are_on_the_expected_positions(
    path: Path, draw, positions: list[str]
) -> None:
    assert re.findall(r'data-sel="([^"]+)"', draw()) == positions


@pytest.mark.parametrize(("path", "draw", "positions"), FIGURES)
def test_figure_draws_one_probe_pair_per_meter(
    path: Path, draw, positions: list[str]
) -> None:
    probes = re.findall(r'data-probe="([^"]+)"', draw())
    assert probes.count("red") == probes.count("black") == len(positions)


def test_diode_figure_puts_the_red_probe_on_the_anode_then_on_the_cathode() -> None:
    svg = guide_01.fig_diode()
    tips = re.findall(
        r'data-probe="(red|black)" transform="translate\(([\d.]+) ([\d.]+)\)', svg
    )
    (c1, _, y1), (c2, _, y2), (c3, _, y3), (c4, _, y4) = tips
    # the anode is labelled above the cathode in both panels
    assert (c1, c2) == ("red", "black") and float(y1) < float(y2)  # forward
    assert (c3, c4) == ("black", "red") and float(y3) < float(y4)  # reversed
    # the red contact dot sits under the red probe tip
    red_dots = re.findall(r'cy="([\d.]+)" r="5" fill="#dc2626"', svg)
    assert [float(y) for y in red_dots] == [float(y1), float(y4)]


@pytest.mark.parametrize(("path", "draw", "positions"), FIGURES)
def test_committed_figure_matches_the_generator(path: Path, draw, positions) -> None:
    assert path.is_file(), f"missing figure, run `just figures`: {path}"
    assert path.read_text(encoding="utf-8") == draw(), "stale, run `just figures`"


def test_check_reports_a_stale_figure(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(generate, "ROOT", tmp_path)
    assert generate.main(["--check"]) == 1  # nothing written yet
    for folder in generate.GUIDES:
        (tmp_path / folder).mkdir()
    assert generate.main([]) == 0
    assert generate.main(["--check"]) == 0
    stale = next(tmp_path.rglob("*.svg"))
    stale.write_text("<svg/>", encoding="utf-8")
    assert generate.main(["--check"]) == 1


def test_unknown_option_is_refused() -> None:
    assert generate.main(["--force"]) == 2


def test_fuse_figure_puts_the_red_probe_in_the_10a_jack_of_each_panel() -> None:
    import guide_i1

    reds = re.findall(
        r'data-probe="red" transform="translate\(([\d.]+) ([\d.]+)\)',
        guide_i1.fig_fuse(),
    )
    jacks = [meter(x0 + 24, 116, 0.9, "200", "OL", "Ω")[1].a for x0 in (0, 380)]
    got = [float(v) for pair in reds for v in pair]
    want = [v for jx, jy in jacks for v in (jx, jy + 4)]
    assert got == pytest.approx(want, abs=0.06)


def test_earth_clip_figure_draws_the_short_circuit_in_the_wrong_panel_only() -> None:
    import guide_i2

    starts = re.findall(r'class="flow fr" d="M([\d.]+)', guide_i2.fig_earth_clip())
    assert len(starts) == 1
    assert float(starts[0]) > 380  # right of the divider: clip on the +12 V


def test_compensation_trace_overshoots_only_when_overcompensated() -> None:
    import guide_i2

    low, high = guide_i2.LOW, guide_i2.HIGH
    levels = {
        shape: [y for _, y in guide_i2.square_wave(shape)]
        for shape in ("flat", "under", "over")
    }
    assert (min(levels["flat"]), max(levels["flat"])) == (low, high)
    assert low <= min(levels["under"]) and max(levels["under"]) <= high
    assert min(levels["under"]) < max(levels["under"])
    assert min(levels["over"]) < low and max(levels["over"]) > high


def test_ring_of_a_shorted_turn_dies_within_two_periods() -> None:
    import guide_30

    good, bad = (guide_30.RING_DECAY[k] for k in ("sain", "spire en court-circuit"))
    assert guide_30.ring(0, good) == pytest.approx(1)
    assert guide_30.ring(4, good) > 0.2  # still ringing after four periods
    assert abs(guide_30.ring(2, bad)) < 0.01
    assert guide_30.fig_ring_test().count("data-ring=") == 2


@pytest.mark.parametrize(("diode", "floor"), [(False, -300), (True, -1.4)])
def test_kick_of_an_opened_coil_is_clamped_by_the_diode(
    diode: bool, floor: float
) -> None:
    import guide_30

    levels = [guide_30.kick(t / 100, diode) for t in range(1001)]
    assert levels[0] == guide_30.KICK_SUPPLY
    assert min(levels) == pytest.approx(floor)
    assert levels[-1] == pytest.approx(0, abs=0.01)
