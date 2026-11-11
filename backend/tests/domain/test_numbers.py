"""M-005 — digits."""

from __future__ import annotations

import pytest

from app.domain.numbers import has_arabic_indic_digits, to_ascii_digits


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("٠١/١٠/٢٠٢٦", "01/10/2026"),  # Hebron's dates
        ("۰۱/۱۰/۲۰۲۶", "01/10/2026"),  # extended forms
        ("ساعه حائط ٣٠", "ساعه حائط 30"),  # letters untouched
        ("30/09/2026", "30/09/2026"),
        ("", ""),
    ],
)
def test_to_ascii_digits(raw: str, expected: str) -> None:
    assert to_ascii_digits(raw) == expected


def test_separators_are_not_this_functions_business() -> None:
    assert to_ascii_digits("١٫٧") == "1٫7"


def test_has_arabic_indic_digits() -> None:
    assert has_arabic_indic_digits("٠١/10/2026")
    assert not has_arabic_indic_digits("01/10/2026")
