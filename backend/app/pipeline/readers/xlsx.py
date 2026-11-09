"""Excel workbooks (M-008).

Every date in the current files is stored as text, and every code like
``0023`` is stored as text too. Both survive untouched because nothing here
converts a string.
"""

from __future__ import annotations

import datetime as dt
import io
from typing import Any

import openpyxl

from app.errors import ErrorCode, MirsadError

from .table import Cell


def cell_text(value: Any) -> tuple[Cell, bool]:
    """Return ``(text, was_excel_date)`` for one cell value."""
    if value is None:
        return None, False
    if isinstance(value, str):
        return (value if value != "" else None), False
    if isinstance(value, bool):  # before int: bool is an int subclass
        return ("TRUE" if value else "FALSE"), False
    if isinstance(value, dt.datetime):
        if value.time() == dt.time(0, 0):
            return value.date().isoformat(), True
        return value.isoformat(), True
    if isinstance(value, (dt.date, dt.time)):
        return value.isoformat(), True
    if isinstance(value, float):
        # repr is the shortest string that round-trips: 346.01, not 346.0100000001
        return (str(int(value)) if value.is_integer() else repr(value)), False
    return str(value), False


def read_sheet(data: bytes, name: str) -> tuple[str, list[tuple[int, tuple[Any, ...]]]]:
    """Return ``(sheet name, [(row number, values)])`` for the single sheet holding data."""
    # data_only: a formula cell gives the value Excel last calculated, which is
    # what the person who exported the file saw.
    workbook = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    try:
        sheets = []
        for sheet in workbook.worksheets:
            rows = [
                (number, tuple(values))
                for number, values in enumerate(sheet.iter_rows(values_only=True), start=1)
            ]
            if any(v is not None and v != "" for _, values in rows for v in values):
                sheets.append((sheet.title, rows))
    finally:
        workbook.close()

    if not sheets:
        raise MirsadError(ErrorCode.FILE_EMPTY, {"file": name})
    if len(sheets) > 1:
        raise MirsadError(
            ErrorCode.FILE_TABLE_AMBIGUOUS,
            {"file": name, "count": len(sheets), "tables": [title for title, _ in sheets]},
        )
    return sheets[0]
