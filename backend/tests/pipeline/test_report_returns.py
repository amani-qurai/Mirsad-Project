"""Returns in the report: Jericho's RTN rows reduce the total, and silence is a finding."""

from __future__ import annotations

from decimal import Decimal

from app.errors import ErrorCode
from app.pipeline.report import report_file

E = ErrorCode
D = Decimal
JERICHO = "Trans No,Trans Date,Item Code,Item Description,Quantity,Value,Notes"
NABLUS = "TXN_ID,TRX_DATE,ITEM_NO,ITEM_NAME,QTY,NET_AMOUNT,NOTES"


def csv(header: str, *rows: str) -> bytes:
    return ("\n".join([header, *rows]) + "\n").encode()


def test_rtn_rows_are_subtracted_not_added() -> None:
    report = report_file(
        csv(JERICHO, "1,1 Oct 2026,0021,Ironing board,1,161.84,", "2,1 Oct 2026,0021,Ironing board,1,90,RTN"),
        "jericho-2026-09-27.csv",
    )
    sale, refund = report.rows
    assert refund.amount == D("-90") and refund.is_return
    assert [f.code for f in refund.findings] == [E.ROW_RETURN_SIGN_FLIPPED]
    assert refund.findings[0].context == {"value": "90", "note": "RTN", "line": 3}
    assert report.worth()["in_totals"] == D("71.84")
    assert report.return_convention == "rtn_note"


def test_negative_returns_need_no_correction() -> None:
    report = report_file(
        csv(NABLUS, "1,29/09/2026,0024,Doormat,1,100.00,", "2,29/09/2026,0024,Doormat,1,-40.00,"),
        "nablus-2026-09-27.csv",
    )
    assert report.rows[1].findings == ()
    assert report.worth()["in_totals"] == D("60.00")
    assert report.return_convention == "negative"


def test_a_busy_file_with_no_refunds_is_a_finding() -> None:
    rows = [f"{i},29/09/2026,0024,Doormat,1,10.00," for i in range(1, 51)]
    report = report_file(csv(NABLUS, *rows), "tulkarem-2026-09-27.csv")
    assert [f.code for f in report.file_findings] == [E.FILE_NO_RETURNS]
    assert report.file_findings[0].context["rows"] == 50
    assert not report.held_file  # a warning: the figures stand, with the caveat


def test_a_quiet_week_without_refunds_is_not() -> None:
    rows = [f"{i},29/09/2026,0024,Doormat,1,10.00," for i in range(1, 50)]
    assert report_file(csv(NABLUS, *rows), "x-2026-09-27.csv").file_findings == ()
