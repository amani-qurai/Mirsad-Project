"""M-005 — amounts: read with certainty or not at all."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.numbers import parse_amount

D = Decimal


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # What the six weeks of real files contain:
        ("457.93", D("457.93")),
        ("-570.65", D("-570.65")),
        ("647", D("647")),
        ("1004.2", D("1004.2")),
        # What a till or a typed sheet can produce:
        ("٣٤٦٫٠١", D("346.01")),
        ("١٬٢٣٤٫٥٠", D("1234.50")),
        ("1,234.50", D("1234.50")),
        ("1.234,50", D("1234.50")),
        ("12,5", D("12.5")),  # one or two decimals after a comma: a decimal comma
        ("1,234,567", D("1234567")),
        ("₪ 457.93", D("457.93")),
        ("457.93 ILS", D("457.93")),
        ("457.93 شيكل", D("457.93")),
        ("−570.65", D("-570.65")),  # minus sign U+2212
        ("570.65-", D("-570.65")),  # trailing minus
        ("(570.65)", D("-570.65")),  # accounting brackets
        (" 1 234.50 ", D("1234.50")),
        ("0", D("0")),
    ],
)
def test_reads(raw: str, expected: Decimal) -> None:
    parsed = parse_amount(raw)
    assert parsed.value == expected and not parsed.ambiguous


def test_decimal_not_float() -> None:
    assert parse_amount("0.1").value + parse_amount("0.2").value == D("0.3")


def test_a_lone_comma_before_three_digits_is_ambiguous() -> None:
    parsed = parse_amount("1,500")
    assert parsed.value is None and parsed.ambiguous
    assert set(parsed.candidates) == {D("1.500"), D("1500")}


def test_ambiguity_keeps_the_sign() -> None:
    assert set(parse_amount("-1,500").candidates) == {D("-1.5"), D("-1500")}


@pytest.mark.parametrize(
    "raw",
    ["", "abc", "12 USD", "1.2.3", "1,23,456", "12..5", "--5", "five", "1e5", "$12"],
)
def test_refuses_what_it_cannot_read(raw: str) -> None:
    parsed = parse_amount(raw)
    assert parsed.value is None and not parsed.ambiguous
