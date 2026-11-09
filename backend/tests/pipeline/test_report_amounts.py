"""Amounts in the report: every count has its worth beside it."""

from __future__ import annotations

from decimal import Decimal

from app.errors import ErrorCode
from app.pipeline.report import report_file
from app.pipeline.validate import Scope

E = ErrorCode
D = Decimal
HEADER = "TXN_ID,TRX_DATE,ITEM_NO,ITEM_NAME,QTY,NET_AMOUNT,NOTES"


def csv(*rows: str) -> bytes:
    return ("\n".join([HEADER, *rows]) + "\n").encode()


def test_amounts_and_quantities_are_read_as_decimals() -> None:
    row = report_file(csv("1,29/09/2026,0024,Doormat,2,698.28,"), "nablus-2026-09-27.csv").rows[0]
    assert (row.amount, row.quantity) == (D("698.28"), D("2"))


def test_an_unreadable_amount_is_rejected_with_its_value() -> None:
    row = report_file(csv("1,29/09/2026,0024,Doormat,2,lots,"), "x.csv").rows[0]
    assert [f.code for f in row.findings] == [E.ROW_AMOUNT_UNPARSEABLE]
    assert row.findings[0].context["value"] == "lots"
    assert not row.kept


def test_an_ambiguous_amount_is_held_from_totals() -> None:
    row = report_file(csv('1,29/09/2026,0024,Doormat,2,"1,500",'), "x.csv").rows[0]
    assert [f.code for f in row.findings] == [E.ROW_AMOUNT_AMBIGUOUS]
    assert row.kept and row.scope == frozenset() and row.amount is None


def test_an_unreadable_quantity_keeps_the_amount() -> None:
    row = report_file(csv("1,29/09/2026,0024,Doormat,two,698.28,"), "x.csv").rows[0]
    assert [f.code for f in row.findings] == [E.ROW_QUANTITY_UNPARSEABLE]
    assert row.amount == D("698.28")
    assert Scope.TOTAL in row.scope and Scope.QUANTITY not in row.scope


def test_worth_says_where_every_shekel_went() -> None:
    report = report_file(
        csv(
            "1,29/09/2026,0024,Doormat,1,100.00,",
            "2,29/09/2026,0024,,1,20.00,",  # no product: in the total, outside product figures
            "3,,0024,Doormat,1,7.50,",  # no date: rejected
            "4,15/12/2026,0024,Doormat,1,3.25,",  # outside the week: held from totals
        ),
        "nablus-2026-09-27.csv",
    )
    assert report.worth() == {
        "in_totals": D("120.00"),
        "outside_product_figures": D("20.00"),
        "rejected": D("7.50"),
        "held_from_totals": D("3.25"),
    }
    assert report.to_dict()["worth"]["in_totals"] == "120.00"  # text, never a float
