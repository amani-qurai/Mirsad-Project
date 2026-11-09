"""Synthetic fixtures, built in memory (NN-11: no real client data in the repo).

The rows imitate the real exports' quirks — Arabic headers, text dates,
Arabic-Indic digits, codes with leading zeros — with invented values.
"""

from __future__ import annotations

import datetime as dt
import io
from typing import Any, Sequence

import docx
import openpyxl
import pytest

AR_HEADER = ("رقم العملية", "التاريخ", "رمز الصنف", "اسم الصنف", "الكمية", "المبلغ", "ملاحظات")
EN_HEADER = ("TXN_ID", "TRX_DATE", "ITEM_NO", "ITEM_NAME", "QTY", "NET_AMOUNT", "NOTES")


def make_xlsx(sheets: dict[str, Sequence[Sequence[Any]]]) -> bytes:
    workbook = openpyxl.Workbook()
    workbook.remove(workbook.active)
    for title, rows in sheets.items():
        sheet = workbook.create_sheet(title)
        for row in rows:
            sheet.append(list(row))
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def make_docx(preamble: Sequence[str], tables: Sequence[Sequence[Sequence[str]]]) -> bytes:
    document = docx.Document()
    for line in preamble:
        document.add_paragraph(line)
    for rows in tables:
        table = document.add_table(rows=len(rows), cols=len(rows[0]))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                table.cell(r, c).text = value
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


@pytest.fixture
def hebron_like_xlsx() -> bytes:
    return make_xlsx({
        "Sales": [
            AR_HEADER,
            [40000, "٠١/١٠/٢٠٢٦", "0023", "طقم ترمس", 1, 346.01, None],
            [40001, "28/09/2026", "0005", "غلاية كهربائية ١٫٧", 2, 468.24, None],
            [None, None, None, None, None, None, None],
            [40002, "30/09/2026", "0012", None, 3, 958.64, None],
            [None] * 7,
        ]
    })


@pytest.fixture
def excel_date_xlsx() -> bytes:
    return make_xlsx({"Sales": [EN_HEADER, [1, dt.datetime(2026, 10, 3), "0004", "Bathmat", 1, 26.66, None]]})
