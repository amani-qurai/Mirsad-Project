"""Numbers as the tills write them (M-005). Pure: values in, values out.

Every amount in the six weeks of real files is plain: ``457.93``, ``-570.65``,
``647``. The parser still handles what a till or a hand-typed sheet can
produce — Arabic-Indic digits, ``٫``/``٬`` separators, a currency word or sign,
a trailing or bracketed minus — because a format change is exactly the kind of
thing that arrives unannounced on a Sunday.

What it will not do is guess. ``1,500`` could be one and a half or fifteen
hundred; it comes back as ambiguous, for a person to decide (D-019).

Money is ``Decimal``, never ``float``: ``0.1 + 0.2`` must equal ``0.3`` in a
branch total.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

# Arabic-Indic (U+0660–0669) — Hebron writes about half its dates with these.
# Extended Arabic-Indic (U+06F0–06F9) — the Persian/Urdu forms; no till uses
# them today, but a keyboard layout can produce them and they mean the same.
_DIGITS = str.maketrans(
    "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹",
    "01234567890123456789",
)


def to_ascii_digits(text: str) -> str:
    """Replace Arabic-Indic digits with 0–9. Every other character is untouched.

    For comparison and parsing only — the original string is what is stored
    and shown (NN-7).
    """
    return text.translate(_DIGITS)


def has_arabic_indic_digits(text: str) -> bool:
    return text != to_ascii_digits(text)


# ── Amounts ─────────────────────────────────────────────────────────────────

# Currency markers that may surround an amount. Stripped only at the ends,
# and only these — an unknown word means the value is not a plain amount.
_CURRENCY = re.compile(
    r"^(?:₪|ils|nis|شيكل|شيقل|ش\.ج\.?|ش\.ج)\s*|\s*(?:₪|ils|nis|شيكل|شيقل|ش\.ج\.?)$",
    re.IGNORECASE,
)
_MINUS = "-−‒–"  # hyphen-minus, minus sign, figure dash, en dash
_SHAPE = re.compile(r"^\d[\d.,]*$|^[.,]\d+$")


@dataclass(frozen=True)
class ParsedNumber:
    value: Decimal | None
    ambiguous: bool = False  # e.g. "1,500": a person must say what it means
    candidates: tuple[Decimal, ...] = ()


def parse_amount(raw: str) -> ParsedNumber:
    """Read one amount. ``value`` is None when it cannot be read with certainty."""
    s = to_ascii_digits(raw).strip()
    s = s.replace("٫", ".").replace("٬", ",")  # Arabic decimal / thousands
    s = s.replace(" ", "").replace(" ", "")
    for _ in range(2):  # a sign and a currency word can sit on either side
        s = _CURRENCY.sub("", s).strip()

    negative = False
    if s[:1] in _MINUS:
        negative, s = True, s[1:]
    elif s[-1:] in _MINUS:
        negative, s = True, s[:-1]
    elif s.startswith("(") and s.endswith(")"):
        negative, s = True, s[1:-1]
    s = s.strip()

    if not _SHAPE.match(s):
        return ParsedNumber(None)

    readings = _readings(s)
    if not readings:
        return ParsedNumber(None)
    if negative:
        readings = [-r for r in readings]
    if len(set(readings)) > 1:
        return ParsedNumber(None, ambiguous=True, candidates=tuple(readings))
    return ParsedNumber(readings[0])


def _readings(s: str) -> list[Decimal]:
    dots, commas = s.count("."), s.count(",")
    if dots and commas:
        # Both present: whichever comes last is the decimal mark.
        decimal, group = (".", ",") if s.rfind(".") > s.rfind(",") else (",", ".")
        if s.count(decimal) > 1 or not _grouped(s.split(decimal)[0], group):
            return []
        return _decimal(s.replace(group, "").replace(decimal, "."))
    if dots > 1 or commas > 1:
        mark = "." if dots else ","
        return _decimal(s.replace(mark, "")) if _grouped(s, mark) else []
    if commas == 1:
        whole, frac = s.split(",")
        as_decimal = _decimal(f"{whole}.{frac}")
        if len(frac) == 3 and whole and len(whole) <= 3:
            # "1,500": a thousands group or a decimal comma. Undecidable alone.
            return as_decimal + _decimal(whole + frac)
        return as_decimal
    return _decimal(s)


def _grouped(s: str, mark: str) -> bool:
    """True if ``mark`` splits ``s`` into a valid thousands grouping."""
    parts = s.split(mark)
    return 1 <= len(parts[0]) <= 3 and all(len(p) == 3 for p in parts[1:])


def _decimal(s: str) -> list[Decimal]:
    try:
        return [Decimal(s)]
    except InvalidOperation:
        return []
