"""Tests of the figure generator: the element library and every generated figure."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

import generate
import guide_01
from elements import POS, UNITS, bench_supply, dial_angle, meter, probe

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
    tips = re.findall(
        r'data-probe="(red|black)" transform="translate\(([\d.]+) ([\d.]+)\)',
        guide_01.fig_diode(),
    )
    (c1, _, y1), (c2, _, y2), (c3, _, y3), (c4, _, y4) = tips
    # the anode is drawn above the cathode in both panels
    assert (c1, c2) == ("red", "black") and float(y1) < float(y2)  # forward
    assert (c3, c4) == ("black", "red") and float(y3) < float(y4)  # reversed


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
