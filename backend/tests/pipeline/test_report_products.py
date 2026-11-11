"""Matching in the report: a product question never removes a sale from its branch total."""

from __future__ import annotations

from app.domain.matching import Catalogue
from app.errors import ErrorCode, Severity
from app.pipeline.report import report_batch, report_file
from app.pipeline.validate import Scope

HEADER = "TXN_ID,TRX_DATE,ITEM_NO,ITEM_NAME,QTY,NET_AMOUNT,NOTES"


def csv(*rows: str) -> bytes:
    return ("\n".join([HEADER, *rows]) + "\n").encode()


def test_a_held_product_keeps_the_row_in_the_branch_total() -> None:
    cat = Catalogue()
    report = report_file(
        csv("1,29/09/2026,0004,Bathmat,1,26.66,", "2,29/09/2026,0004,بساط حمام,4,103.34,"),
        "bethlehem-2026-09-27.csv",
        catalogue=cat,
    )
    known, question = report.rows
    assert known.product is not None and Scope.PRODUCT in known.scope
    assert question.severity is Severity.HELD
    assert question.scope == {Scope.TOTAL}  # in the total, out of product (and quantity) figures
    assert (report.rows_in_totals, report.rows_in_product_figures) == (2, 1)


def test_an_ambiguous_date_withholds_the_row_from_everything() -> None:
    report = report_file(csv("1,04/10/2026,0004,Bathmat,1,26.66,"), "export.csv", catalogue=Catalogue())
    assert report.rows[0].scope == frozenset()
    assert report.rows_in_totals == 0


def test_the_queue_has_one_question_per_spelling(tmp_path) -> None:
    a = tmp_path / "nablus-2026-09-27.csv"
    b = tmp_path / "hebron-2026-09-27.csv"
    a.write_bytes(csv("1,29/09/2026,0004,Bathmat,1,26.66,"))
    b.write_bytes(csv(*(f"{i},29/09/2026,0004,بساط حمام,1,25.00," for i in range(1, 6))))
    batch = report_batch([a, b])
    [question] = batch.questions()
    assert question["name"] == "بساط حمام"
    assert question["rows"] == 5 and question["files"] == ["hebron-2026-09-27.csv"]
    assert question["code"] == ErrorCode.PRODUCT_MATCH_UNCONFIRMED.value


def test_answers_carry_over_to_the_next_batch(tmp_path) -> None:
    a = tmp_path / "nablus-2026-09-27.csv"
    a.write_bytes(csv("1,29/09/2026,0004,Bathmat,1,26.66,", "2,29/09/2026,0004,بساط حمام,1,25.00,"))
    first = report_batch([a])
    [q] = first.questions()
    first.catalogue.confirm(q["name"], q["candidates"][0]["product"])
    second = report_batch([a], first.catalogue)
    assert second.questions() == []
    assert second.totals()["rows_in_product_figures"] == 2
