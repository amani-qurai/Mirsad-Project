"""M-009 — the rejection report: every row accounted for, nothing dropped."""

from __future__ import annotations

from app.errors import ErrorCode, Severity
from app.pipeline.headers import AmountBasis, Field
from app.pipeline.report import report_batch, report_file
from app.pipeline.validate import Scope

E = ErrorCode

HEADER = "TXN_ID,TRX_DATE,ITEM_NO,ITEM_NAME,QTY,NET_AMOUNT,NOTES"


def csv(*rows: str, header: str = HEADER) -> bytes:
    return ("\n".join([header, *rows]) + "\n").encode()


def by_line(report):
    return {row.line: row for row in report.rows}


def test_clean_rows_are_kept_with_full_scope() -> None:
    report = report_file(csv("40000,29/09/2026,0024,دعاسة باب,2,698.28,"), "nablus.csv")
    row = report.rows[0]
    assert row.findings == ()
    assert row.severity is None
    assert row.scope == {Scope.TOTAL, Scope.PRODUCT, Scope.QUANTITY}
    assert (report.rows_in, report.rows_kept, report.rows_rejected) == (1, 1, 0)


def test_no_date_or_no_amount_is_rejected_but_kept_visible() -> None:
    report = report_file(
        csv(
            "1,,0024,دعاسة باب,2,698.28,",
            "2,29/09/2026,0024,دعاسة باب,2,,",
            "3,   ,0010,سلة غسيل,1,  ,",
        ),
        "x.csv",
    )
    rows = by_line(report)
    assert [f.code for f in rows[2].findings] == [E.ROW_MISSING_DATE]
    assert [f.code for f in rows[3].findings] == [E.ROW_MISSING_AMOUNT]
    assert {f.code for f in rows[4].findings} == {E.ROW_MISSING_DATE, E.ROW_MISSING_AMOUNT}
    assert all(r.severity is Severity.REJECTED and r.scope == frozenset() for r in rows.values())
    assert report.rows_in == 3 and report.rows_rejected == 3
    assert report.lines_by_code()[E.ROW_MISSING_DATE] == [2, 4]


def test_no_product_counts_in_the_total_only() -> None:
    report = report_file(csv("1,29/09/2026,0024,,2,698.28,"), "x.csv")
    row = report.rows[0]
    assert [f.code for f in row.findings] == [E.ROW_MISSING_PRODUCT]
    assert row.findings[0].context == {"product_code": "0024", "line": 2}
    assert row.kept and Scope.TOTAL in row.scope and Scope.PRODUCT not in row.scope
    assert report.lines_outside(Scope.PRODUCT) == [2]


def test_no_quantity_keeps_the_amount() -> None:
    row = report_file(csv("1,29/09/2026,0024,دعاسة باب,,698.28,"), "x.csv").rows[0]
    assert [f.code for f in row.findings] == [E.ROW_MISSING_QUANTITY]
    assert row.scope == {Scope.TOTAL, Scope.PRODUCT}


def test_reused_id_on_different_sales_keeps_every_row() -> None:
    """Ramallah's till restarted its numbering — these are real sales (D-013)."""
    report = report_file(
        csv(
            "2,09/28/2026,0002,ابريق زجاج ١.٥ ل,2,596.63,",
            "3,09/27/2026,0008,غطاء وسادة ٤٥,2,483.87,",
            "2,10/01/2026,0011,ساعة حائط 30,1,380.79,",
        ),
        "ramallah.csv",
    )
    rows = by_line(report)
    assert report.rows_kept == 3
    assert [f.code for f in rows[2].findings] == [E.TXN_ID_REUSED]
    assert rows[2].findings[0].context["lines"] == [2, 4]
    assert rows[3].findings == ()


def test_identical_row_is_a_duplicate_and_points_at_the_original() -> None:
    line = "7,29/09/2026,0024,دعاسة باب,2,698.28,"
    report = report_file(csv(line, line), "x.csv")
    rows = by_line(report)
    assert rows[2].findings == ()
    assert [f.code for f in rows[3].findings] == [E.TXN_DUPLICATE_WITHIN_FILE]
    assert rows[3].findings[0].context["same_as_line"] == 2
    assert report.rows_in == 2 and report.rows_kept == 1


def test_identical_pair_plus_a_reuse() -> None:
    a = "7,29/09/2026,0024,دعاسة باب,2,698.28,"
    report = report_file(csv(a, a, "7,30/09/2026,0010,سلة غسيل,1,223.40,"), "x.csv")
    rows = by_line(report)
    assert [f.code for f in rows[3].findings] == [E.TXN_DUPLICATE_WITHIN_FILE]
    assert [f.code for f in rows[2].findings] == [E.TXN_ID_REUSED]
    assert rows[2].findings[0].context["lines"] == [2, 4]


def test_missing_txn_id_is_a_warning() -> None:
    row = report_file(csv(",29/09/2026,0024,دعاسة باب,2,698.28,"), "x.csv").rows[0]
    assert [f.code for f in row.findings] == [E.TXN_ID_MISSING]
    assert row.kept


def test_a_file_without_an_id_column_is_not_flagged_on_every_row() -> None:
    """Tulkarem has no transaction ids at all: one file-level fact, not 170 warnings."""
    report = report_file(csv("29/09/2026,دعاسة,2,722.9,", header="التاريخ,الصنف,الكمية,المبلغ,ملاحظات"), "t.csv")
    assert report.rows[0].findings == ()
    assert set(report.fields_absent) == {Field.TXN_ID, Field.PRODUCT_CODE, Field.DISCOUNT}


def test_pre_vat_basis_reaches_the_report() -> None:
    header = "TXN,DATE,CODE,PRODUCT,QTY,AMOUNT_EXVAT,NOTE"
    report = report_file(csv("1,03/10/2026,0023,Vacuum flask set,1,313.4,", header=header), "q.csv")
    assert report.amount_basis is AmountBasis.EX_VAT
    assert report.to_dict()["amount_basis"] == "ex_vat"


def test_a_refused_file_is_reported_with_its_code_and_no_rows() -> None:
    report = report_file(csv("1,2", header="Quarter,Branch"), "notes.csv")
    assert report.file_code is E.FILE_HEADERS_UNRECOGNISED
    assert report.rows == ()


def test_identical_files_in_one_batch_are_counted_once(tmp_path) -> None:
    data = csv("1,29/09/2026,0024,دعاسة باب,2,698.28,", "2,30/09/2026,0010,سلة غسيل,1,223.40,")
    first, second = tmp_path / "jenin.csv", tmp_path / "jenin-FINAL.csv"
    first.write_bytes(data)
    second.write_bytes(data)
    batch = report_batch([first, second])
    assert batch.files[1].file_code is E.FILE_EXACT_DUPLICATE
    assert batch.files[1].file_context["same_as"] == "jenin.csv"
    assert batch.totals()["rows_in"] == 2


def test_report_dict_holds_codes_and_numbers_only() -> None:
    report = report_file(csv("1,,0024,,2,698.28,", "2,29/09/2026,0024,دعاسة باب,2,10,"), "x.csv")
    d = report.to_dict()
    assert d["rows"] == {"in": 2, "kept": 1, "rejected": 1, "held": 0, "warning": 0}
    assert d["codes"]["ROW_MISSING_DATE"] == {"severity": "rejected", "count": 1, "lines": [2]}
    assert d["codes"]["ROW_MISSING_PRODUCT"]["lines"] == [2]
    assert d["outside_scope"]["product"] == []  # line 2 is rejected, so it is not a completeness gap
