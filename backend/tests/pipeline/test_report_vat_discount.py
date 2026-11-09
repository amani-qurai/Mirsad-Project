"""M-017 — pre-VAT amounts wait for a decision; discounts are deducted and stated."""

from __future__ import annotations

from decimal import Decimal

from app.errors import ErrorCode
from app.pipeline.report import Decisions, report_batch, report_file

E = ErrorCode
D = Decimal
QALQILYA = "TXN,DATE,CODE,PRODUCT,QTY,AMOUNT_EXVAT,NOTE"
JENIN = "رقم العملية,التاريخ,رمز الصنف,اسم الصنف,الكمية,المبلغ,الخصم,ملاحظات"


def csv(header: str, *rows: str) -> bytes:
    return ("\n".join([header, *rows]) + "\n").encode()


def test_pre_vat_amounts_are_held_not_multiplied() -> None:
    report = report_file(csv(QALQILYA, "1,03/10/2026,0023,Vacuum flask set,1,100.00,"), "qalqilya-2026-09-27.csv")
    [finding] = report.file_findings
    assert finding.code is E.FILE_AMOUNTS_EX_VAT
    assert finding.context == {
        "file": "qalqilya-2026-09-27.csv", "branch": "qalqilya", "suggested_rate": "0.16", "evidence": "header",
    }
    assert report.held_file
    assert report.rows[0].amount == D("100.00")  # untouched
    assert report.worth()["held_from_totals"] == D("100.00")


def test_one_decision_per_branch_adds_vat_to_every_file(tmp_path) -> None:
    weeks = []
    for i, start in enumerate(("2026-09-27", "2026-10-04"), start=1):
        p = tmp_path / f"qalqilya-{start}.csv"
        p.write_bytes(csv(QALQILYA, f"{i},0{i}/10/2026,0023,Vacuum flask set,1,100.00,"))
        weeks.append(p)
    decisions = Decisions()
    decisions.add_vat("qalqilya")
    batch = report_batch(weeks, decisions=decisions)
    for f in batch.files:
        assert [x.code for x in f.file_findings] == [E.FILE_VAT_ADDED]
        assert not f.held_file
        assert f.rows[0].amount == D("116.00")


def test_vat_decision_for_one_branch_does_not_touch_another() -> None:
    decisions = Decisions()
    decisions.add_vat("qalqilya")
    report = report_file(
        csv(QALQILYA, "1,03/10/2026,0023,Vacuum flask set,1,100.00,"), "hebron-2026-09-27.csv", decisions=decisions,
    )
    assert report.file_findings[0].code is E.FILE_AMOUNTS_EX_VAT


def test_vat_is_added_to_refunds_too() -> None:
    decisions = Decisions()
    decisions.add_vat("qalqilya")
    report = report_file(
        csv(QALQILYA, "1,03/10/2026,0023,Vacuum flask set,1,-50.00,"), "qalqilya-2026-09-27.csv", decisions=decisions,
    )
    assert report.rows[0].amount == D("-58.00")


def test_jenin_discount_is_deducted_from_sales_and_refunds() -> None:
    report = report_file(
        csv(
            JENIN,
            "1,29-09-2026,0009,مقلاة 28 سم,2,302.38,45.36,",
            "2,29-09-2026,0007,صندوق تخزين 20,1,-354.72,45.00,",
            "3,29-09-2026,0007,صندوق تخزين 20,1,100.00,0.0,",
        ),
        "jenin-2026-09-27.csv",
    )
    sale, refund, plain = report.rows
    assert sale.amount == D("257.02")
    assert refund.amount == D("-309.72")  # the refund gives back what was paid
    assert plain.amount == D("100.00")
    [finding] = report.file_findings
    assert finding.code is E.FILE_DISCOUNT_DEDUCTED
    assert (finding.context["rows"], finding.context["total"]) == (2, "90.36")


def test_an_unreadable_discount_holds_the_row_from_totals() -> None:
    report = report_file(csv(JENIN, "1,29-09-2026,0009,مقلاة 28 سم,2,302.38,some,"), "jenin-2026-09-27.csv")
    row = report.rows[0]
    assert [f.code for f in row.findings] == [E.ROW_DISCOUNT_UNPARSEABLE]
    assert row.scope == frozenset()
