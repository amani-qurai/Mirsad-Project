"""One entry point for every branch file: ``read_file`` / ``read_bytes`` (M-008).

Whatever the format — Excel, CSV in any of three encodings, CSV wearing an
``.xls`` name, a hand-typed Word table — the result is the same ``RawTable``.

    >>> table = read_file("data/week-01/nablus-2026-09-27.xlsx")
    >>> table.to_dataframe().head()

A file that cannot be read safely raises ``MirsadError`` with a file-level code.
It never comes back half-read.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Iterable

from app.errors import ErrorCode, MirsadError

from . import text, word, xlsx
from .sniff import sniff_format
from .table import Cell, RawRow, RawTable, SourceFile

__all__ = ["RawRow", "RawTable", "SourceFile", "read_bytes", "read_file"]


def read_file(path: str | Path) -> RawTable:
    path = Path(path)
    return read_bytes(path.read_bytes(), path.name)


def read_bytes(data: bytes, name: str) -> RawTable:
    detected = sniff_format(data, name)
    base = {
        "name": name,
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "declared_extension": Path(name).suffix.lower().lstrip("."),
        "detected_format": detected,
    }
    if detected == "csv":
        table = _read_text(data, name, base)
    elif detected == "xlsx":
        table = _read_xlsx(data, name, base)
    else:
        table = _read_word(data, name, base)

    if not table.rows:
        raise MirsadError(ErrorCode.FILE_EMPTY, {"file": name})
    return table


def _read_text(data: bytes, name: str, base: dict[str, Any]) -> RawTable:
    decoded, encoding, had_bom = text.decode(data, name)
    if not decoded.strip():
        raise MirsadError(ErrorCode.FILE_EMPTY, {"file": name})
    delimiter = text.detect_delimiter(decoded, name)
    header, header_line, rows, blank = text.read_rows(decoded, delimiter)
    source = SourceFile(**base, encoding=encoding, had_bom=had_bom, delimiter=delimiter)
    return RawTable(source, header, header_line, tuple(rows), tuple(blank))


def _read_xlsx(data: bytes, name: str, base: dict[str, Any]) -> RawTable:
    title, raw_rows = xlsx.read_sheet(data, name)
    dates: list[tuple[int, int]] = []

    def convert(number: int, values: Iterable[Any]) -> tuple[Cell, ...]:
        out: list[Cell] = []
        for column, value in enumerate(values):
            cell, was_date = xlsx.cell_text(value)
            if was_date:
                dates.append((number, column))
            out.append(cell)
        return tuple(out)

    converted = [(number, convert(number, values)) for number, values in raw_rows]
    header, header_line, rows, blank = _split_grid(converted)
    source = SourceFile(**base, container=title)
    return RawTable(source, header, header_line, tuple(rows), tuple(blank), tuple(dates))


def _read_word(data: bytes, name: str, base: dict[str, Any]) -> RawTable:
    preamble, raw_rows = word.read_word_table(data, name)
    converted = [
        (number, tuple(cell if cell != "" else None for cell in values))
        for number, values in enumerate(raw_rows, start=1)
    ]
    header, header_line, rows, blank = _split_grid(converted)
    source = SourceFile(**base, container="table 1", preamble=preamble)
    return RawTable(source, header, header_line, tuple(rows), tuple(blank))


def _split_grid(
    grid: list[tuple[int, tuple[Cell, ...]]],
) -> tuple[tuple[str, ...], int, list[RawRow], list[int]]:
    """Header = first non-blank row. Trailing empty cells are trimmed to the header width.

    A spreadsheet cannot tell "short row" from "row with empty cells at the
    end", so grid rows are padded to the header width and only cells that hold
    something beyond it are kept as extras.
    """
    header: tuple[str, ...] | None = None
    header_line = 0
    rows: list[RawRow] = []
    blank: list[int] = []

    for number, cells in grid:
        if not any(c is not None and c.strip() for c in cells):
            if header is not None:
                blank.append(number)
            continue
        if header is None:
            last = max(i for i, c in enumerate(cells) if c is not None and c.strip())
            header = tuple(c if c is not None else "" for c in cells[: last + 1])
            header_line = number
            continue
        last_filled = max((i for i, c in enumerate(cells) if c is not None), default=-1)
        width = max(len(header), last_filled + 1)
        padded = tuple(cells[:width]) + (None,) * (width - len(cells[:width]))
        rows.append(RawRow(line=number, cells=padded))

    # Blank rows after the last data row are just the end of the sheet.
    last_data = rows[-1].line if rows else 0
    return header or (), header_line, rows, [n for n in blank if n < last_data]
