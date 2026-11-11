"""M-006 in the report: the week from the file name, and a loud format change."""

from __future__ import annotations

import datetime as dt

from app.domain.dates import Order
from app.errors import ErrorCode
from app.pipeline.filenames import parse_file_name
from app.pipeline.report import report_batch, report_file

E = ErrorCode
HEADER = "Transaction,Date,ITEM_NO,Description,Qty,Amount,Remarks"


def csv(*rows: str) -> bytes:
    return ("\n".join([HEADER, *rows]) + "\n").encode()


def test_file_name_gives_branch_and_week() -> None:
    name = parse_file_name("ramallah-2026-10-04.xlsx")
    assert name.branch == "ramallah"
    assert name.period == (dt.date(2026, 10, 4), dt.date(2026, 10, 10))
    assert parse_file_name("jenin-2026-10-11-FINAL.csv").week_start == dt.date(2026, 10, 11)
    assert parse_file_name("rania-quarterly-review-notes-2023-2026.xlsx") is None
    assert parse_file_name("sales.csv") is None


def test_rows_carry_their_date() -> None:
    report = report_file(csv("1,10/04/2026,0002,ابريق زجاج,2,596.63,"), "ramallah-2026-10-04.csv")
    assert report.rows[0].date == dt.date(2026, 10, 4)
    assert report.date_order is Order.MDY and report.date_order_evidence == "week"


def test_without_a_week_in_the_name_ambiguous_dates_are_held() -> None:
    report = report_file(csv("1,10/04/2026,0002,ابريق زجاج,2,596.63,"), "export.csv")
    assert report.rows[0].date is None
    assert report.rows_held == 1


def test_a_branch_changing_date_order_holds_the_file(tmp_path) -> None:
    """Ramallah: month-first for three weeks, then day-first."""
    week3 = tmp_path / "ramallah-2026-10-11.csv"
    week4 = tmp_path / "ramallah-2026-10-18.csv"
    week5 = tmp_path / "ramallah-2026-10-25.csv"
    week3.write_bytes(csv("1,10/13/2026,0002,ابريق زجاج,2,596.63,"))
    week4.write_bytes(csv("1,19/10/2026,0002,ابريق زجاج,2,596.63,", "2,20/10/2026,0011,ساعة حائط 30,1,380.79,"))
    week5.write_bytes(csv("1,26/10/2026,0002,ابريق زجاج,2,596.63,"))

    batch = report_batch([week3, week4, week5])
    first, changed, after = batch.files

    assert first.file_findings == ()
    assert [f.code for f in changed.file_findings] == [E.FILE_DATE_FORMAT_CHANGED]
    assert changed.file_findings[0].context == {
        "file": "ramallah-2026-10-18.csv", "branch": "ramallah", "previous": "MDY", "current": "DMY",
    }
    assert changed.held_file and changed.rows_held == 2
    assert after.file_findings == ()  # the new format is now the branch's format
    assert batch.totals()["files_held"] == 1


def test_one_branch_changing_does_not_affect_another(tmp_path) -> None:
    a = tmp_path / "ramallah-2026-10-11.csv"
    b = tmp_path / "nablus-2026-10-18.csv"
    a.write_bytes(csv("1,10/13/2026,0002,ابريق زجاج,2,596.63,"))
    b.write_bytes(csv("1,19/10/2026,0002,ابريق زجاج,2,596.63,"))
    assert all(f.file_findings == () for f in report_batch([a, b]).files)


def test_both_orders_inside_one_file_hold_it() -> None:
    report = report_file(
        csv("1,10/13/2026,0002,ابريق زجاج,2,596.63,", "2,14/10/2026,0011,ساعة حائط 30,1,380.79,"),
        "ramallah-2026-10-11.csv",
    )
    assert report.file_findings[0].context["within_file"] is True
    assert report.held_file
