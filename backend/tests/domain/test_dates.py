"""M-006 — dates: decided once per file, from evidence, never guessed."""

from __future__ import annotations

import datetime as dt

import pytest

from app.domain.dates import Order, infer_dates, readings
from app.errors import ErrorCode

E = ErrorCode
D = dt.date
WEEK_1 = (D(2026, 9, 27), D(2026, 10, 3))   # has days above 12
WEEK_2 = (D(2026, 10, 4), D(2026, 10, 10))  # no day above 12 — the hard week


# ── One value ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2026-09-28", {Order.YMD: D(2026, 9, 28)}),
        ("30/09/2026", {Order.DMY: D(2026, 9, 30)}),
        ("09/30/2026", {Order.MDY: D(2026, 9, 30)}),
        ("29-09-2026", {Order.DMY: D(2026, 9, 29)}),
        ("٣٠/٠٩/٢٠٢٦", {Order.DMY: D(2026, 9, 30)}),
        ("28/09/26", {Order.DMY: D(2026, 9, 28)}),
        ("1 Oct 2026", {Order.TEXT: D(2026, 10, 1)}),
        ("27 Sept 2026", {Order.TEXT: D(2026, 9, 27)}),
        ("10/03/2026", {Order.DMY: D(2026, 3, 10), Order.MDY: D(2026, 10, 3)}),
        ("10/10/2026", {Order.DMY: D(2026, 10, 10), Order.MDY: D(2026, 10, 10)}),
        ("31/02/2026", {}),  # date-shaped, not a date
        ("next tuesday", None),
        ("2026/09-28", None),  # mixed separators are not a date we know
        ("5 Okt 2026", None),
    ],
)
def test_readings(raw: str, expected) -> None:
    assert readings(raw) == expected


# ── A whole file ────────────────────────────────────────────────────────────


def test_unambiguous_values_need_no_decision() -> None:
    result = infer_dates(["30/09/2026", "10/10/2026", "2026-09-28"])
    assert [r.value for r in result.results] == [D(2026, 9, 30), D(2026, 10, 10), D(2026, 9, 28)]
    assert all(r.code is None for r in result.results)


def test_the_file_decides_its_ambiguous_values() -> None:
    result = infer_dates(["30/09/2026", "01/10/2026"])
    assert result.order is Order.DMY and result.order_evidence == "file"
    second = result.results[1]
    assert second.value == D(2026, 10, 1)
    assert second.code is E.DATE_FORMAT_INFERRED
    assert second.context["evidence"] == "file"
    assert second.context["candidates"] == {"DMY": "2026-10-01", "MDY": "2026-01-10"}


def test_ramallah_month_first_is_read_month_first() -> None:
    result = infer_dates(["09/30/2026", "10/03/2026"], WEEK_1)
    assert result.order is Order.MDY
    assert result.results[1].value == D(2026, 10, 3)


def test_the_week_decides_when_the_file_cannot() -> None:
    """4–10 October has no day above 12: the file alone proves nothing."""
    result = infer_dates(["04/10/2026", "07/10/2026", "10/10/2026"], WEEK_2)
    assert [r.value for r in result.results] == [D(2026, 10, 4), D(2026, 10, 7), D(2026, 10, 10)]
    assert result.results[0].context["evidence"] == "week"
    assert result.order is Order.DMY and result.order_evidence == "week"


def test_the_week_decides_month_first_too() -> None:
    result = infer_dates(["10/04/2026", "10/07/2026"], WEEK_2)
    assert [r.value for r in result.results] == [D(2026, 10, 4), D(2026, 10, 7)]
    assert result.order is Order.MDY


def test_without_any_evidence_it_is_held_with_both_candidates() -> None:
    result = infer_dates(["04/10/2026", "07/10/2026"])
    first = result.results[0]
    assert first.value is None
    assert first.code is E.DATE_FORMAT_AMBIGUOUS
    assert first.context["candidates"] == {"DMY": "2026-10-04", "MDY": "2026-04-10"}
    assert result.order is None


def test_file_and_week_disagreeing_is_held_not_chosen() -> None:
    # The file says month-first; the week says 04/10 is 4 October (day-first).
    result = infer_dates(["09/30/2026", "04/10/2026"], WEEK_2)
    assert result.results[1].code is E.DATE_FORMAT_AMBIGUOUS
    assert result.results[1].context["reason"] == "file_and_week_disagree"


def test_both_orders_in_one_file_is_reported_as_conflicting() -> None:
    result = infer_dates(["30/09/2026", "09/30/2026", "01/10/2026"])
    assert result.conflicting is True
    assert result.order is None
    assert result.results[2].code is E.DATE_FORMAT_AMBIGUOUS


def test_a_date_outside_the_week_is_held() -> None:
    result = infer_dates(["30/09/2026", "15/12/2026"], WEEK_1)
    late = result.results[1]
    assert late.code is E.ROW_DATE_OUT_OF_RANGE
    assert late.value == D(2026, 12, 15)
    assert late.context["period_end"] == "2026-10-03"


def test_unreadable_values_are_rejected_with_the_value() -> None:
    result = infer_dates(["31/02/2026", "soon", "30/09/2026"])
    assert [r.code for r in result.results[:2]] == [E.ROW_DATE_UNPARSEABLE] * 2
    assert result.results[1].context == {"value": "soon"}


def test_empty_values_are_left_for_the_presence_check() -> None:
    assert infer_dates([None, "  ", "30/09/2026"]).results[:2] == (None, None)


def test_hebron_mixed_digits_read_as_one_format() -> None:
    result = infer_dates(["٠١/١٠/٢٠٢٦", "30/09/2026", "٢٨/٠٩/٢٠٢٦"], WEEK_1)
    assert [r.value for r in result.results] == [D(2026, 10, 1), D(2026, 9, 30), D(2026, 9, 28)]
    assert result.results[0].context["value"] == "٠١/١٠/٢٠٢٦"  # the original is what is reported
    assert result.order is Order.DMY
