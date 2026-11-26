"""Tests of the photo, marking and coating figures of guide 90 (#162)."""

from __future__ import annotations

import re

import pytest

import guide_90


def test_turning_the_board_over_mirrors_a_point_inside_its_panel() -> None:
    assert guide_90.flipped(90, 0) == 290
    assert guide_90.flipped(guide_90.flipped(123, 380), 380) == 123


def test_header_pins_run_left_to_right_from_above_and_right_to_left_from_the_back() -> (
    None
):
    top, back = guide_90.header_pins(0, False), guide_90.header_pins(0, True)
    assert sorted(top) == sorted(back) == list(range(1, guide_90.HEADER_PINS + 1))
    assert list(top.values()) == sorted(top.values())
    assert list(back.values()) == sorted(back.values(), reverse=True)
    assert set(top.values()) == set(back.values())  # same holes, other order


def test_connector_figure_numbers_the_back_in_reverse_order() -> None:
    content = guide_90.fig_connector_back()
    labels = re.findall(r'<text x="([\d.]+)" y="264"[^>]*>(\d)</text>', content)
    left = [n for x, n in labels if float(x) < guide_90.PANEL_W]
    right = [
        n
        for x, n in sorted(labels, key=lambda p: float(p[0]))
        if float(x) > guide_90.PANEL_W
    ]
    assert left == ["1", "2", "3", "4", "5", "6"]
    assert right == ["6", "5", "4", "3", "2", "1"]


def test_connector_figure_keeps_the_landmark_on_the_side_of_pin_1() -> None:
    content = guide_90.fig_connector_back()
    holes = [float(x) for x in re.findall(r'<circle cx="([\d.]+)" cy="156"', content)]
    for x0, back, hole in ((0, False, holes[0]), (guide_90.PANEL_W, True, holes[1])):
        pins = guide_90.header_pins(x0, back)
        assert abs(hole - pins[1]) < abs(hole - pins[guide_90.HEADER_PINS])


@pytest.mark.parametrize(
    ("year", "week", "code"),
    [(2025, 30, "2530"), (2000, 6, "0006"), (1999, 48, "9948")],
)
def test_date_code_is_two_digits_of_the_year_then_the_week(
    year: int, week: int, code: str
) -> None:
    assert guide_90.date_code(year, week) == code


@pytest.mark.parametrize("week", [0, 54])
def test_date_code_refuses_a_week_outside_the_calendar(week: int) -> None:
    with pytest.raises(ValueError, match="calendar week"):
        guide_90.date_code(2025, week)


def test_marking_figure_prints_the_part_code_then_the_date_and_lot_codes() -> None:
    content = guide_90.fig_chip_marking()
    code = guide_90.date_code(guide_90.MARK_YEAR, guide_90.MARK_WEEK)
    assert (
        content.count(f">{guide_90.PART_MARKING}</text>") == 4
    )  # three chips, one legend
    assert content.count(f">{code} {guide_90.LOT}</text>") == 3
    assert f"{guide_90.MARK_YEAR}, semaine {guide_90.MARK_WEEK}" in content
    assert guide_90.PART in content


def test_marking_figure_hides_the_marking_under_the_glare_of_one_chip_only() -> None:
    assert guide_90.fig_chip_marking().count("<ellipse") == 1


def test_needle_tip_lands_on_the_metal_termination_not_on_the_body() -> None:
    x, y = guide_90.NEEDLE_TIP
    assert guide_90.TERMINAL[0] <= x <= guide_90.TERMINAL[1]
    assert y == guide_90.PART_TOP
    assert f'd="M{x} {y} L' in guide_90.fig_coating()


def test_figure_week_starts_a_six_week_period() -> None:
    """The drawn code must read the same as a calendar week and as a period start."""
    assert guide_90.MARK_WEEK % 6 == 0
