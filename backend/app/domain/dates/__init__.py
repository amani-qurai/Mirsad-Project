"""Dates as the tills write them: inference, ambiguity, never a guess (M-006).

Pure: strings in, dates and findings out. The original string is never
changed; this module only says what it means, or that it cannot tell.

Formats seen in the six weeks of real files:

    2026-09-28    year first                     Al-Bireh
    27/09/2026    day/month                      most branches
    29-09-2026    day-month                      Jenin
    ٠١/١٠/٢٠٢٦     Arabic-Indic digits            Hebron, about half its rows
    10/03/2026    month/day, then day/month      Ramallah, changed mid-history
    28/09/26      two-digit year                 Salfit
    1 Oct 2026    day, month name, year          Jericho

How day/month order is decided for a value like ``10/03/2026``, in order:

1. **The value itself.** ``30/09/2026`` has only one valid reading.
   ``10/10/2026`` reads the same both ways. Neither needs a decision.
2. **The rest of the file.** If every value in the file that *can* only be
   read one way is read the same way, the ambiguous ones follow it
   (``DATE_FORMAT_INFERRED``, a warning, with the evidence recorded).
3. **The week the file covers.** A weekly file's dates fall inside its week.
   ``10/04/2026`` in the file for 4–10 October is 4 October; 10 April is not
   in that week. Used when the file alone cannot decide — the week of 4–10
   October has no day above 12, so its files carry no evidence of their own.
4. **Otherwise it is held** (``DATE_FORMAT_AMBIGUOUS``) with both candidate
   dates, for a person to choose. It is never guessed (AC-6).

If the file's order and its week disagree about a value, that value is held:
two pieces of evidence pointing different ways is exactly when not to choose.
"""

from __future__ import annotations

import datetime as dt
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.domain.numbers import to_ascii_digits
from app.errors import ErrorCode


class Order(StrEnum):
    DMY = "DMY"    # 27/09/2026
    MDY = "MDY"    # 09/27/2026
    YMD = "YMD"    # 2026-09-27
    TEXT = "TEXT"  # 27 Sep 2026 — the month is a word, so the order is never in doubt


Period = tuple[dt.date, dt.date]  # inclusive

_MONTHS = {
    name: number
    for number, names in enumerate(
        [
            ("jan", "january"), ("feb", "february"), ("mar", "march"), ("apr", "april"),
            ("may",), ("jun", "june"), ("jul", "july"), ("aug", "august"),
            ("sep", "sept", "september"), ("oct", "october"), ("nov", "november"), ("dec", "december"),
        ],
        start=1,
    )
    for name in names
}

_YMD = re.compile(r"^(\d{4})([/\-.])(\d{1,2})\2(\d{1,2})$")
_DM_OR_MD = re.compile(r"^(\d{1,2})([/\-.])(\d{1,2})\2(\d{4}|\d{2})$")
_TEXT = re.compile(r"^(\d{1,2})[\s\-/]+([A-Za-z]+)\.?[\s\-/,]+(\d{4})$")


def _date(year: int, month: int, day: int) -> dt.date | None:
    try:
        return dt.date(year, month, day)
    except ValueError:
        return None


def readings(raw: str) -> dict[Order, dt.date] | None:
    """Every valid reading of one value, by order.

    ``None``: the value is not in any date shape we know.
    ``{}``: it has a date shape, but no reading is a real date (``31/02/2026``).
    """
    text = to_ascii_digits(raw).strip()

    if m := _YMD.match(text):
        d = _date(int(m[1]), int(m[3]), int(m[4]))
        return {Order.YMD: d} if d else {}

    if m := _DM_OR_MD.match(text):
        first, second, year = int(m[1]), int(m[3]), m[4]
        # A two-digit year is this century. A year-first reading of a
        # two-digit value (26/10/05 as 2026-10-05) is not considered: no till
        # writes it, and the week check would reject it anyway (D-015).
        y = 2000 + int(year) if len(year) == 2 else int(year)
        out = {}
        if d := _date(y, second, first):
            out[Order.DMY] = d
        if d := _date(y, first, second):
            out[Order.MDY] = d
        return out

    if m := _TEXT.match(text):
        month = _MONTHS.get(m[2].lower())
        if month is None:
            return None
        d = _date(int(m[3]), month, int(m[1]))
        return {Order.TEXT: d} if d else {}

    return None


@dataclass(frozen=True)
class DateResult:
    """One value's outcome. ``code`` is None when the date is certain and in range."""

    value: dt.date | None
    code: ErrorCode | None = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FileDates:
    results: tuple[DateResult | None, ...]  # None where the input was empty
    order: Order | None  # the order the file was read in, when one order explains it
    order_evidence: str | None  # "file": its own unambiguous values · "week": only the week it covers
    conflicting: bool  # the file contains values only readable as DMY *and* values only readable as MDY


def _in(period: Period | None, d: dt.date) -> bool:
    return period is not None and period[0] <= d <= period[1]


def infer_dates(values: Sequence[str | None], period: Period | None = None) -> FileDates:
    """Read every date in one file, deciding day/month order once for the file."""
    parsed = [None if v is None or not v.strip() else readings(v) for v in values]

    # Evidence: values with exactly one valid reading.
    single_orders = {next(iter(r)) for r in parsed if r is not None and len(r) == 1}
    dm_evidence = single_orders & {Order.DMY, Order.MDY}
    conflicting = len(dm_evidence) == 2
    file_dm = next(iter(dm_evidence)) if len(dm_evidence) == 1 else None

    families = single_orders - {Order.DMY, Order.MDY}
    has_dm = any(r and (Order.DMY in r or Order.MDY in r) for r in parsed)
    if has_dm:
        file_order = file_dm
    elif len(families) == 1:
        file_order = next(iter(families))
    else:
        file_order = None

    results: list[DateResult | None] = []
    for raw, r in zip(values, parsed):
        if raw is None or not raw.strip():
            results.append(None)
        elif not r:
            results.append(DateResult(None, ErrorCode.ROW_DATE_UNPARSEABLE, {"value": raw}))
        else:
            results.append(_decide(raw, r, file_dm, period))

    evidence = "file" if file_order is not None else None
    if file_order is None and not conflicting:
        # A file the week had to decide: if the week chose one order for
        # every ambiguous value, that is the order the file was written in.
        week_orders = {
            res.context["order"]
            for res in results
            if res is not None and res.code is ErrorCode.DATE_FORMAT_INFERRED and res.context.get("evidence") == "week"
        }
        if len(week_orders) == 1:
            file_order, evidence = Order(week_orders.pop()), "week"
    return FileDates(tuple(results), file_order, evidence, conflicting)


def _decide(raw: str, r: dict[Order, dt.date], file_dm: Order | None, period: Period | None) -> DateResult:
    distinct = set(r.values())
    if len(distinct) == 1:
        d = distinct.pop()
        return _range_checked(raw, d, period)

    candidates = {order.value: d.isoformat() for order, d in r.items()}
    in_period = [order for order, d in r.items() if _in(period, d)]
    base = {"value": raw, "candidates": candidates}

    if file_dm is not None:
        chosen = r[file_dm]
        if period is not None and file_dm not in in_period and in_period:
            # The file says one thing and the week says another. Do not choose.
            return DateResult(None, ErrorCode.DATE_FORMAT_AMBIGUOUS, {**base, "reason": "file_and_week_disagree"})
        if period is not None and not in_period:
            return DateResult(chosen, ErrorCode.ROW_DATE_OUT_OF_RANGE, {**base, **_period_context(period), "date": chosen.isoformat()})
        return DateResult(chosen, ErrorCode.DATE_FORMAT_INFERRED, {**base, "order": file_dm.value, "evidence": "file"})

    if len(in_period) == 1:
        order = in_period[0]
        return DateResult(r[order], ErrorCode.DATE_FORMAT_INFERRED, {**base, "order": order.value, "evidence": "week"})

    return DateResult(None, ErrorCode.DATE_FORMAT_AMBIGUOUS, base)


def _range_checked(raw: str, d: dt.date, period: Period | None) -> DateResult:
    if period is not None and not _in(period, d):
        return DateResult(d, ErrorCode.ROW_DATE_OUT_OF_RANGE, {"value": raw, "date": d.isoformat(), **_period_context(period)})
    return DateResult(d)


def _period_context(period: Period) -> dict[str, str]:
    return {"period_start": period[0].isoformat(), "period_end": period[1].isoformat()}
