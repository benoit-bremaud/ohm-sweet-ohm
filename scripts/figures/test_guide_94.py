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


def test_capacitor_node_starts_at_zero_and_settles_on_the_resistor() -> None:
    assert guide_94.rc_ohms(0) == 0
    assert guide_94.rc_ohms(2) == pytest.approx(
        86_466, abs=1
    )  # the 86.5 kΩ on the meter
    assert guide_94.rc_ohms(5) > 0.99 * 100_000  # "stable après 5 s environ"


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


@pytest.mark.parametrize(
    ("draw", "red_on", "readings"),
    [
        (guide_94.fig_ohm_polarities, ("broche", "masse"), (">4.72<", ">1.18<")),
        (guide_94.fig_diode_mode, ("masse", "broche"), (">0.58<", ">OL<")),
    ],
)
def test_two_polarity_figures_swap_the_red_probe_between_pin_and_ground(
    draw, red_on: tuple[str, str], readings: tuple[str, str]
) -> None:
    svg = draw()
    # the red tip lands on the left point of each panel: x0 + 245, and each panel keeps its reading
    assert svg.index(readings[0]) < svg.index(readings[1])
    for x0, label in zip((0, 380), red_on, strict=True):
        assert re.search(rf'<text [^>]*x="{x0 + 245}"[^>]*>{label}<', svg)


def test_odd_one_out_is_the_channel_furthest_from_the_median() -> None:
    assert guide_94.odd_one_out(guide_94.TWINS) == "TEMP 2"
    assert guide_94.odd_one_out((("A", 10), ("B", 10), ("C", 3))) == "C"  # odd count
    assert guide_94.odd_one_out((("A", 5), ("B", 5))) == "A"  # all equal: first wins


@pytest.mark.parametrize(("ref", "celsius"), [(1000, 0), (1071, 18.4), (995, -1.3)])
def test_reference_drift_lands_whole_on_the_reading(ref: float, celsius: float) -> None:
    assert guide_94.reference_error(ref) == pytest.approx(celsius, abs=0.1)


def test_twin_gap_is_about_twenty_degrees() -> None:
    gap = guide_94.reference_error(1071) - guide_94.reference_error(995)
    assert gap == pytest.approx(20, abs=0.5)


def test_twin_table_paints_only_the_odd_channel_red() -> None:
    svg = guide_94.fig_twin_table()
    assert len(re.findall(r'<rect class="no"', svg)) == 1
    assert len(re.findall(r'<rect class="ok"', svg)) == 3


def test_funnel_ends_on_the_drifted_resistor() -> None:
    svg = guide_94.fig_funnel()
    assert [stage for stage, _, _ in guide_94.FUNNEL] == [
        "Connecteur",
        "Via",
        "Résistance",
    ]
    assert "R25 : 1 071 Ω" in svg


def test_export_plans_one_png_per_figure_and_a_plate_only_with_a_photo(
    tmp_path: Path,
) -> None:
    guide, photos, out = tmp_path / "g", tmp_path / "p", tmp_path / "o"
    guide.mkdir()
    photos.mkdir()
    for name in ("a", "b", "arbre-1"):
        (guide / f"{name}.svg").write_text("<svg/>")
    (photos / "b.jpg").write_bytes(b"")
    commands = export.plan(guide, out, photos)
    assert [c[0] for c in commands] == ["inkscape", "inkscape", "magick"]
    assert all("arbre-1" not in " ".join(c) for c in commands)
    assert [c[0] for c in export.plan(guide, out, None)] == ["inkscape", "inkscape"]


def test_plate_puts_the_photo_then_a_gutter_then_the_figure() -> None:
    c = export.plate_command(Path("p.jpg"), Path("f.png"), Path("x.png"))
    # the gutter is spliced on the photo's east side, before the figure joins it
    assert c.index("p.jpg") < c.index("east") < c.index("24x0") < c.index("f.png")
    assert c.index("f.png") < c.index("+append") and c[-1] == "x.png"


def test_export_refuses_wrong_arguments(tmp_path: Path) -> None:
    (tmp_path / "g").mkdir()
    assert export.main([]) == 2
    assert export.main([str(tmp_path / "missing"), str(tmp_path)]) == 2
    assert (
        export.main([str(tmp_path / "g"), str(tmp_path), str(tmp_path / "nope")]) == 2
    )


def test_export_runs_every_planned_command(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "g").mkdir()
    (tmp_path / "g" / "a.svg").write_text("<svg/>")
    ran: list[list[str]] = []
    monkeypatch.setattr(export.subprocess, "run", lambda c, **_: ran.append(c))
    assert export.main([str(tmp_path / "g"), str(tmp_path / "o")]) == 0
    assert ran and ran[0][0] == "inkscape" and (tmp_path / "o").is_dir()


def test_export_reports_a_missing_tool(tmp_path: Path, monkeypatch, capsys) -> None:
    (tmp_path / "g").mkdir()
    (tmp_path / "g" / "a.svg").write_text("<svg/>")

    def missing(command: list[str], **_: object) -> None:
        raise FileNotFoundError(command[0])

    monkeypatch.setattr(export.subprocess, "run", missing)
    assert export.main([str(tmp_path / "g"), str(tmp_path / "o")]) == 1
    assert "export failed: inkscape" in capsys.readouterr().err
