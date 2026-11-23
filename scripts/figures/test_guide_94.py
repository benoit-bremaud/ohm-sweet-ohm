"""Tests of the RTD channel figures (guide 94, #162) and of the PNG export."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import export
import guide_94


@pytest.mark.parametrize(("ohms", "celsius"), [(1000, 0), (1100, 26), (1385, 100)])
def test_pt1000_conversion_follows_its_linear_slope(
    ohms: float, celsius: float
) -> None:
    assert guide_94.pt1000_celsius(ohms) == pytest.approx(celsius, abs=0.5)


def test_twin_drift_of_76_ohms_is_about_20_degrees() -> None:
    assert guide_94.pt1000_celsius(1071) - guide_94.pt1000_celsius(
        995
    ) == pytest.approx(20, abs=0.5)


def test_filtered_node_starts_at_zero_and_settles_on_the_resistor() -> None:
    assert guide_94.rc_ohms(0) == 0
    assert guide_94.rc_ohms(3) == pytest.approx(
        861, abs=1
    )  # the 0.86 kΩ shown on the meter
    assert guide_94.rc_ohms(20) == pytest.approx(995, abs=0.5)


def test_pulses_alternate_between_rest_and_plateau_over_the_screen() -> None:
    pts = guide_94.pulses(cols=8, period=2, duty=0.25, high=3)
    assert {y for _, y in pts} == {0.4, 3}
    assert pts[0][0] == 0 and pts[-1][0] == 8
    assert (
        sum(1 for (_, y0), (_, y1) in zip(pts, pts[1:], strict=False) if y0 < y1) == 4
    )


def test_tssop16_puts_pin_1_bottom_left_and_pin_16_above_it() -> None:
    _, tips = guide_94.tssop16(100, 100)
    assert sorted(tips) == list(range(1, 17))
    assert tips[1][0] == tips[16][0] < tips[8][0]
    assert tips[1][1] > 100 > tips[16][1]


def test_mux_figure_probes_input_1s2_on_pin_5() -> None:
    _, tips = guide_94.tssop16(560, 250)
    svg = guide_94.fig_mux_trace()
    black = re.search(
        r'data-probe="black" transform="translate\(([\d.]+) ([\d.]+)\)', svg
    )
    assert black and (float(black[1]), float(black[2])) == tips[5]
    assert guide_94.TSSOP16[5] == "1S2"


@pytest.mark.parametrize(
    ("draw", "red_on"),
    [
        (guide_94.fig_ohm_polarities, ("broche", "masse")),
        (guide_94.fig_diode_mode, ("masse", "broche")),
    ],
)
def test_two_polarity_figures_swap_the_red_probe_between_pin_and_ground(
    draw, red_on: tuple[str, str]
) -> None:
    svg = draw()
    # the red tip lands on the left point of each panel: x0 + 245
    for x0, label in zip((0, 380), red_on, strict=True):
        assert re.search(rf'<text [^>]*x="{x0 + 245}"[^>]*>{label}<', svg)


def test_export_plans_one_png_per_figure_and_a_plate_only_with_a_photo(
    tmp_path: Path,
) -> None:
    guide, photos, out = tmp_path / "g", tmp_path / "p", tmp_path / "o"
    guide.mkdir()
    photos.mkdir()
    (guide / "a.svg").write_text("<svg/>")
    (guide / "b.svg").write_text("<svg/>")
    (photos / "b.jpg").write_bytes(b"")
    commands = export.plan(guide, out, photos)
    assert [c[0] for c in commands] == ["inkscape", "inkscape", "magick"]
    assert commands[2][-1] == str(out / "b-planche.png")
    assert [c[0] for c in export.plan(guide, out, None)] == ["inkscape", "inkscape"]


def test_export_refuses_wrong_arguments(tmp_path: Path) -> None:
    assert export.main([]) == 2
    assert export.main([str(tmp_path / "missing"), str(tmp_path)]) == 2


def test_export_runs_every_planned_command(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "g").mkdir()
    (tmp_path / "g" / "a.svg").write_text("<svg/>")
    ran: list[list[str]] = []
    monkeypatch.setattr(export.subprocess, "run", lambda c, **_: ran.append(c))
    assert export.main([str(tmp_path / "g"), str(tmp_path / "o")]) == 0
    assert ran and ran[0][0] == "inkscape" and (tmp_path / "o").is_dir()
