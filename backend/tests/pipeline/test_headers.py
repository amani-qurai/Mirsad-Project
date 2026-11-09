"""M-008 — header mapping: every known header set maps; anything else is held."""

from __future__ import annotations

import pytest

from app.errors import ErrorCode, MirsadError, Severity
from app.pipeline.headers import Alias, AmountBasis, Field, map_headers
from app.pipeline.readers import RawRow, RawTable, SourceFile

F = Field

# The ten header layouts seen across the eleven branches' real exports.
# Column names are the tills' schema, not client data.
KNOWN_LAYOUTS = {
    "nablus / rafidia": (
        ["TXN_ID", "TRX_DATE", "ITEM_NO", "ITEM_NAME", "QTY", "NET_AMOUNT", "NOTES"],
        [F.TXN_ID, F.DATE, F.PRODUCT_CODE, F.PRODUCT_NAME, F.QUANTITY, F.AMOUNT, F.NOTES],
    ),
    "ramallah": (
        ["Transaction", "Date", "ITEM_NO", "Description", "Qty", "Amount", "Remarks"],
        [F.TXN_ID, F.DATE, F.PRODUCT_CODE, F.PRODUCT_NAME, F.QUANTITY, F.AMOUNT, F.NOTES],
    ),
    "al-bireh": (
        ["txn_id", "date", "item_no", "item_name", "qty", "amount", "notes"],
        [F.TXN_ID, F.DATE, F.PRODUCT_CODE, F.PRODUCT_NAME, F.QUANTITY, F.AMOUNT, F.NOTES],
    ),
    "hebron": (
        ["رقم العملية", "التاريخ", "رمز الصنف", "اسم الصنف", "الكمية", "المبلغ", "ملاحظات"],
        [F.TXN_ID, F.DATE, F.PRODUCT_CODE, F.PRODUCT_NAME, F.QUANTITY, F.AMOUNT, F.NOTES],
    ),
    "jenin": (
        ["رقم العملية", "التاريخ", "رمز الصنف", "اسم الصنف", "الكمية", "المبلغ", "الخصم", "ملاحظات"],
        [F.TXN_ID, F.DATE, F.PRODUCT_CODE, F.PRODUCT_NAME, F.QUANTITY, F.AMOUNT, F.DISCOUNT, F.NOTES],
    ),
    "tulkarem": (
        ["التاريخ", "الصنف", "الكمية", "المبلغ", "ملاحظات"],
        [F.DATE, F.PRODUCT_NAME, F.QUANTITY, F.AMOUNT, F.NOTES],
    ),
    "qalqilya": (
        ["TXN", "DATE", "CODE", "PRODUCT", "QTY", "AMOUNT_EXVAT", "NOTE"],
        [F.TXN_ID, F.DATE, F.PRODUCT_CODE, F.PRODUCT_NAME, F.QUANTITY, F.AMOUNT, F.NOTES],
    ),
    "bethlehem": (
        ["Txn", "Date", "Code", "Product", "Qty", "Amount", "Notes"],
        [F.TXN_ID, F.DATE, F.PRODUCT_CODE, F.PRODUCT_NAME, F.QUANTITY, F.AMOUNT, F.NOTES],
    ),
    "jericho": (
        ["Trans No", "Trans Date", "Item Code", "Item Description", "Quantity", "Value", "Notes"],
        [F.TXN_ID, F.DATE, F.PRODUCT_CODE, F.PRODUCT_NAME, F.QUANTITY, F.AMOUNT, F.NOTES],
    ),
    "salfit": (
        ["TXN_ID", "DATE", "ITEM_NO", "ITEM", "QTY", "AMOUNT", "NOTES"],
        [F.TXN_ID, F.DATE, F.PRODUCT_CODE, F.PRODUCT_NAME, F.QUANTITY, F.AMOUNT, F.NOTES],
    ),
}


def table_with(header: list[str], name: str = "branch.xlsx") -> RawTable:
    source = SourceFile(name=name, size=0, sha256="", declared_extension="xlsx", detected_format="xlsx")
    row = RawRow(line=2, cells=tuple("x" for _ in header))
    return RawTable(source=source, header=tuple(header), header_line=1, rows=(row,))


def held(header: list[str], **kwargs) -> MirsadError:
    with pytest.raises(MirsadError) as excinfo:
        map_headers(table_with(header), **kwargs)
    assert excinfo.value.code is ErrorCode.FILE_HEADERS_UNRECOGNISED
    assert excinfo.value.severity is Severity.HELD
    return excinfo.value


@pytest.mark.parametrize("branch", KNOWN_LAYOUTS)
def test_every_known_layout_maps_every_column(branch: str) -> None:
    header, fields = KNOWN_LAYOUTS[branch]
    mapping = map_headers(table_with(header))
    assert {field: index for index, field in enumerate(fields)} == dict(mapping.columns)


def test_only_qalqilya_declares_ex_vat_amounts() -> None:
    for branch, (header, _) in KNOWN_LAYOUTS.items():
        expected = AmountBasis.EX_VAT if branch == "qalqilya" else AmountBasis.UNSTATED
        assert map_headers(table_with(header)).amount_basis is expected, branch


def test_spacing_case_and_underscores_do_not_matter() -> None:
    mapping = map_headers(table_with([" trans  date ", "net amount"]))
    assert mapping.has(F.DATE) and mapping.has(F.AMOUNT)
    assert map_headers(table_with(["التاريخ ", " المبلغ"])).has(F.AMOUNT)


def test_an_unknown_column_holds_the_file_instead_of_being_ignored() -> None:
    error = held(["DATE", "AMOUNT", "Cashier"])
    assert error.context["unrecognised"] == ["Cashier"]
    assert error.context["headers"] == ["DATE", "AMOUNT", "Cashier"]


def test_a_missing_amount_column_holds_the_file() -> None:
    error = held(["DATE", "ITEM_NAME"])
    assert error.context["missing"] == ["amount"]


def test_two_columns_for_one_field_hold_the_file() -> None:
    error = held(["DATE", "AMOUNT", "Value"])
    assert error.context["duplicated"] == {"amount": ["AMOUNT", "Value"]}


def test_a_remembered_answer_resolves_the_hold() -> None:
    held(["DATE", "AMOUNT", "Cashier"])
    mapping = map_headers(
        table_with(["DATE", "AMOUNT", "Cashier"]),
        remembered={"Cashier": Alias(F.NOTES)},
    )
    assert mapping.columns[F.NOTES] == 2


def test_the_review_notes_workbook_is_not_mistaken_for_a_branch_export() -> None:
    held(["Quarter", "Review date", "Branch", "Reported total (ILS)", "Rank (of trading branches)"])
