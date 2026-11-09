"""M-008 — every format comes back as the same RawTable, untouched."""

from __future__ import annotations

import pytest

from app.errors import ErrorCode, MirsadError, Severity
from app.pipeline.readers import RawTable, read_bytes

from .conftest import AR_HEADER, make_docx, make_xlsx

AR_CSV = "\n".join([
    ",".join(AR_HEADER),
    "40000,29-09-2026,0009,مقلاة 28 سم,2,302.38,",
    "40001,03-10-2026,0007,صندوق تخزين 20,1,-354.72,RTN",
]) + "\n"


def code_of(excinfo: pytest.ExceptionInfo[MirsadError]) -> ErrorCode:
    return excinfo.value.code


# ── The shared shape ────────────────────────────────────────────────────────


def test_every_format_returns_the_same_shape(hebron_like_xlsx: bytes) -> None:
    csv_table = read_bytes(AR_CSV.encode("utf-8"), "jenin.csv")
    xlsx_table = read_bytes(hebron_like_xlsx, "hebron.xlsx")
    word_table = read_bytes(
        make_docx(["نخيل للتجزئة - فرع طولكرم"], [[["التاريخ", "الصنف", "المبلغ"], ["28/09/2026", "دعاسة", "722.9"]]]),
        "tulkarem.docx",
    )
    for table in (csv_table, xlsx_table, word_table):
        assert isinstance(table, RawTable)
        assert table.rows
        for row in table.rows:
            assert all(cell is None or isinstance(cell, str) for cell in row.cells)


def test_dataframe_is_text_only_and_carries_lines(hebron_like_xlsx: bytes) -> None:
    frame = read_bytes(hebron_like_xlsx, "hebron.xlsx").to_dataframe()
    assert list(frame.columns) == ["_line", *AR_HEADER]
    assert frame["المبلغ"].tolist() == ["346.01", "468.24", "958.64"]
    assert frame["_line"].tolist() == [2, 3, 5]


# ── Excel ───────────────────────────────────────────────────────────────────


def test_xlsx_keeps_text_exactly(hebron_like_xlsx: bytes) -> None:
    table = read_bytes(hebron_like_xlsx, "hebron.xlsx")
    first = table.rows[0].cells
    assert first[1] == "٠١/١٠/٢٠٢٦"  # Arabic-Indic digits are not converted here
    assert first[2] == "0023"  # leading zeros survive
    assert first[0] == "40000"
    assert table.rows[1].cells[3] == "غلاية كهربائية ١٫٧"


def test_xlsx_missing_product_is_none_not_dropped(hebron_like_xlsx: bytes) -> None:
    table = read_bytes(hebron_like_xlsx, "hebron.xlsx")
    assert table.rows[2].cells[3] is None
    assert len(table.rows) == 3


def test_xlsx_blank_rows_are_counted_not_returned(hebron_like_xlsx: bytes) -> None:
    table = read_bytes(hebron_like_xlsx, "hebron.xlsx")
    assert table.blank_lines == (4,)  # the trailing blank row is just the end of the sheet


def test_xlsx_real_date_cell_is_iso_and_recorded(excel_date_xlsx: bytes) -> None:
    table = read_bytes(excel_date_xlsx, "x.xlsx")
    assert table.rows[0].cells[1] == "2026-10-03"
    assert table.excel_date_cells == ((2, 1),)


def test_xlsx_numbers_are_written_as_the_sheet_shows_them() -> None:
    data = make_xlsx({"Sales": [["A", "B", "C"], [1004.2, 52.5, 400.0]]})
    assert read_bytes(data, "f.xlsx").rows[0].cells == ("1004.2", "52.5", "400")


def test_xlsx_two_sheets_with_data_is_held() -> None:
    data = make_xlsx({"Sales": [["A"], ["1"]], "Copy": [["A"], ["2"]]})
    with pytest.raises(MirsadError) as excinfo:
        read_bytes(data, "two.xlsx")
    assert code_of(excinfo) is ErrorCode.FILE_TABLE_AMBIGUOUS
    assert excinfo.value.severity is Severity.HELD
    assert excinfo.value.context["tables"] == ["Sales", "Copy"]


def test_xlsx_empty_sheet_alongside_data_is_ignored() -> None:
    data = make_xlsx({"Sales": [["A"], ["1"]], "Sheet2": []})
    assert read_bytes(data, "one.xlsx").source.container == "Sales"


def test_xlsx_header_only_is_empty() -> None:
    with pytest.raises(MirsadError) as excinfo:
        read_bytes(make_xlsx({"Sales": [AR_HEADER]}), "h.xlsx")
    assert code_of(excinfo) is ErrorCode.FILE_EMPTY


# ── Delimited text ──────────────────────────────────────────────────────────


def test_utf8_bom_is_noted_and_stripped() -> None:
    data = b"\xef\xbb\xbf" + "txn_id,date,amount\n40000,2026-09-28,457.93\n".encode()
    table = read_bytes(data, "albireh.csv")
    assert table.source.had_bom is True
    assert table.source.encoding == "utf-8"
    assert table.header[0] == "txn_id"  # no BOM glued to the first header


def test_windows_1256_arabic_is_accepted() -> None:
    table = read_bytes(AR_CSV.encode("cp1256"), "jenin.csv")
    assert table.source.encoding == "cp1256"
    assert table.header == AR_HEADER
    assert table.rows[0].cells[3] == "مقلاة 28 سم"


def test_lost_characters_are_kept_as_received() -> None:
    """Jenin's till cannot write Arabic-Indic digits in cp1256; they arrive as '?' (D-011)."""
    text = ",".join(AR_HEADER) + "\n40000,29-09-2026,0009,مقلاه ?? سم,2,302.38,\n"
    table = read_bytes(text.encode("cp1256"), "jenin.csv")
    assert table.rows[0].cells[3] == "مقلاه ?? سم"


def test_non_arabic_legacy_encoding_is_refused_not_guessed() -> None:
    data = "id;name;amount\n1;Crème brûlée;12.5\n2;Café;3.0\n".encode("latin-1")
    with pytest.raises(MirsadError) as excinfo:
        read_bytes(data, "latin.csv")
    assert code_of(excinfo) is ErrorCode.FILE_ENCODING_UNDETECTED


def test_semicolon_csv_named_xls_is_read_as_csv() -> None:
    data = "Txn;Date;Code;Product;Qty;Amount;Notes\n40000;27/09/2026;0004;بساط حمام;4;103.34;\n".encode()
    table = read_bytes(data, "bethlehem.xls")
    assert table.source.detected_format == "csv"
    assert table.source.delimiter == ";"
    assert table.source.extension_mismatch is True
    assert table.rows[0].cells[3] == "بساط حمام"


def test_ragged_row_is_kept_and_reported() -> None:
    good = [f"{i},ترمس,10" for i in range(3, 13)]
    data = "\n".join(["id,name,amount", "1,دعاسة,5", "2,طقم صحون, 12 قطعة,20", *good]).encode()
    table = read_bytes(data, "r.csv")
    assert table.rows[1].cells == ("2", "طقم صحون", " 12 قطعة", "20")
    assert table.width_mismatch_lines == (3,)


def test_delimiter_is_refused_when_too_many_rows_disagree() -> None:
    """One odd row in twelve is a ragged row; one in four means we do not know the shape."""
    data = "id,name,amount\n1,ترمس,10\n2,طقم صحون, 12 قطعة,20\n3,دعاسة,5\n".encode()
    with pytest.raises(MirsadError) as excinfo:
        read_bytes(data, "r.csv")
    assert code_of(excinfo) is ErrorCode.FILE_DELIMITER_UNDETECTED


def test_quoted_multiline_field_reports_its_starting_line() -> None:
    data = 'id,name,amount\n1,"ترمس\n1 لتر",10\n2,دعاسة,5\n'.encode()
    table = read_bytes(data, "m.csv")
    assert [row.line for row in table.rows] == [2, 4]
    assert table.rows[0].cells[1] == "ترمس\n1 لتر"


def test_blank_csv_lines_are_counted() -> None:
    data = "id,amount\n1,10\n\n,\n2,5\n".encode()
    table = read_bytes(data, "b.csv")
    assert table.blank_lines == (3, 4)
    assert len(table.rows) == 2


def test_undecidable_delimiter_is_refused() -> None:
    data = "a;b,c\n1;2,3\n4;5,6\n".encode()
    with pytest.raises(MirsadError) as excinfo:
        read_bytes(data, "both.csv")
    assert code_of(excinfo) is ErrorCode.FILE_DELIMITER_UNDETECTED
    assert set(excinfo.value.context["candidates"]) == {",", ";"}


@pytest.mark.parametrize("data", [b"", b"\n\n  \n", "id,amount\n".encode()])
def test_nothing_to_read_is_empty(data: bytes) -> None:
    with pytest.raises(MirsadError) as excinfo:
        read_bytes(data, "e.csv")
    assert code_of(excinfo) is ErrorCode.FILE_EMPTY


# ── Word ────────────────────────────────────────────────────────────────────


def test_word_table_keeps_preamble_and_cells() -> None:
    data = make_docx(
        ["نخيل للتجزئة - فرع طولكرم", "مبيعات الأسبوع 27/09/2026", "(التسجيل يدوي - الصندوق معطل)"],
        [[["التاريخ", "الصنف", "الكمية", "المبلغ", "ملاحظات"], ["28/09/2026", "إبريق زجاج 1.5", "2", "614.66", ""]]],
    )
    table = read_bytes(data, "tulkarem.docx")
    assert table.source.detected_format == "docx"
    assert table.source.preamble[2] == "(التسجيل يدوي - الصندوق معطل)"
    assert table.rows[0].cells == ("28/09/2026", "إبريق زجاج 1.5", "2", "614.66", None)
    assert table.rows[0].line == 2


def test_word_with_two_tables_is_held() -> None:
    data = make_docx([], [[["a"], ["1"]], [["b"], ["2"]]])
    with pytest.raises(MirsadError) as excinfo:
        read_bytes(data, "t.docx")
    assert code_of(excinfo) is ErrorCode.FILE_TABLE_AMBIGUOUS


# ── Format sniffing ─────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("data", "detected"),
    [
        (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 100, "ole2"),
        (b"%PDF-1.7\x00\x01\x02", "binary"),
        (b"PK\x03\x04not really a zip", "corrupt-zip"),
    ],
)
def test_unreadable_formats_are_rejected_with_what_was_found(data: bytes, detected: str) -> None:
    with pytest.raises(MirsadError) as excinfo:
        read_bytes(data, "x.xls")
    assert code_of(excinfo) is ErrorCode.FILE_FORMAT_UNSUPPORTED
    assert excinfo.value.context["detected"] == detected


def test_identical_bytes_have_identical_hashes() -> None:
    """What FILE_EXACT_DUPLICATE will key on — the Jenin week-03 pair (D-008)."""
    data = AR_CSV.encode("cp1256")
    assert read_bytes(data, "jenin.csv").source.sha256 == read_bytes(data, "jenin-FINAL.csv").source.sha256
