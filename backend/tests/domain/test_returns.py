"""M-011 — returns, however the till writes them."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.returns import convention, is_rtn, signed_amount

D = Decimal


def test_a_negative_amount_is_a_refund() -> None:
    s = signed_amount(D("-570.65"), None)
    assert (s.amount, s.is_return, s.flipped) == (D("-570.65"), True, False)


def test_a_positive_rtn_row_is_a_refund_and_the_flip_is_recorded() -> None:
    s = signed_amount(D("90"), "RTN")
    assert (s.amount, s.is_return, s.flipped) == (D("-90"), True, True)


def test_a_negative_rtn_row_is_not_flipped_twice() -> None:
    s = signed_amount(D("-90"), "RTN")
    assert (s.amount, s.flipped) == (D("-90"), False)


def test_a_sale_is_a_sale() -> None:
    s = signed_amount(D("161.84"), None)
    assert (s.amount, s.is_return) == (D("161.84"), False)


@pytest.mark.parametrize("note", ["RTN", "rtn", "RTN - damaged", "item RTN"])
def test_rtn_marker(note: str) -> None:
    assert is_rtn(note)


@pytest.mark.parametrize("note", [None, "", "RETURN", "مرتجع", "PRTNR", "RTNX"])
def test_only_the_marker_the_tills_use(note: str | None) -> None:
    """Another word is not assumed to mean a refund until seen and confirmed (D-020)."""
    assert not is_rtn(note)


def test_convention() -> None:
    assert convention(3, 0) == "negative"
    assert convention(0, 2) == "rtn_note"
    assert convention(1, 1) == "both"
    assert convention(0, 0) is None
