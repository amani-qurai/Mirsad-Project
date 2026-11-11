"""Delimited text files: encoding, delimiter, then rows (M-008).

Seen so far: UTF-8, UTF-8 with a BOM (Al-Bireh), Windows-1256 (Jenin), and a
semicolon-delimited file named ``.xls`` (Bethlehem).
"""

from __future__ import annotations

import csv
import io

from app.errors import ErrorCode, MirsadError

from .table import Cell, RawRow

_BOMS: tuple[tuple[bytes, str], ...] = (
    (b"\xef\xbb\xbf", "utf-8"),
    (b"\xff\xfe", "utf-16-le"),
    (b"\xfe\xff", "utf-16-be"),
)

# Accepted only if the decoded text is recognisably Arabic (D-010).
_ARABIC_FALLBACK = "cp1256"
_MIN_ARABIC_SHARE = 0.9

DELIMITER_CANDIDATES = (",", ";", "\t", "|")
_SAMPLE_RECORDS = 50
_MIN_CONSISTENCY = 0.9


def decode(data: bytes, name: str) -> tuple[str, str, bool]:
    """Return ``(text, encoding, had_bom)`` or refuse with FILE_ENCODING_UNDETECTED."""
    for bom, encoding in _BOMS:
        if data.startswith(bom):
            try:
                return data[len(bom):].decode(encoding), encoding, True
            except UnicodeDecodeError:
                raise MirsadError(
                    ErrorCode.FILE_ENCODING_UNDETECTED, {"file": name, "bom": encoding}
                ) from None

    try:
        return data.decode("utf-8"), "utf-8", False
    except UnicodeDecodeError:
        pass

    # Windows-1256 decodes almost any byte sequence, so "it decoded" proves
    # nothing. Accept it only when what comes out is Arabic.
    text = data.decode(_ARABIC_FALLBACK, errors="replace")
    if _arabic_share(text) >= _MIN_ARABIC_SHARE:
        return text, _ARABIC_FALLBACK, False

    raise MirsadError(ErrorCode.FILE_ENCODING_UNDETECTED, {"file": name, "tried": ["utf-8", _ARABIC_FALLBACK]})


def _is_arabic(ch: str) -> bool:
    cp = ord(ch)
    return (
        0x0600 <= cp <= 0x06FF
        or 0x0750 <= cp <= 0x077F
        or 0xFB50 <= cp <= 0xFDFF
        or 0xFE70 <= cp <= 0xFEFF
        or ch in "‌‍‎‏"  # joiners and direction marks
    )


def _arabic_share(text: str) -> float:
    non_ascii = [ch for ch in text if ord(ch) > 0x7F]
    if not non_ascii:
        return 0.0
    return sum(_is_arabic(ch) for ch in non_ascii) / len(non_ascii)


def detect_delimiter(text: str, name: str) -> str:
    """Pick the one candidate that splits the file into a consistent shape.

    If none does, or more than one does equally well, refuse rather than guess:
    a wrong delimiter produces a perfectly regular table of wrong columns.
    """
    qualifying: list[str] = []
    for delimiter in DELIMITER_CANDIDATES:
        widths = [
            len(record)
            for record in _records(text, delimiter, limit=_SAMPLE_RECORDS)
        ]
        if not widths or widths[0] < 2:
            continue
        consistency = sum(w == widths[0] for w in widths) / len(widths)
        if consistency >= _MIN_CONSISTENCY:
            qualifying.append(delimiter)

    if len(qualifying) == 1:
        return qualifying[0]
    raise MirsadError(
        ErrorCode.FILE_DELIMITER_UNDETECTED,
        {"file": name, "candidates": qualifying},
    )


def _records(text: str, delimiter: str, limit: int | None = None) -> list[list[str]]:
    out: list[list[str]] = []
    for record in csv.reader(io.StringIO(text, newline=""), delimiter=delimiter):
        if not any(field.strip() for field in record):
            continue
        out.append(record)
        if limit is not None and len(out) >= limit:
            break
    return out


def read_rows(text: str, delimiter: str) -> tuple[tuple[str, ...], int, list[RawRow], list[int]]:
    """Split into header, rows and blank lines, keeping each row's start line."""
    reader = csv.reader(io.StringIO(text, newline=""), delimiter=delimiter)
    header: tuple[str, ...] | None = None
    header_line = 0
    rows: list[RawRow] = []
    blank: list[int] = []
    previous_end = 0

    for record in reader:
        start = previous_end + 1  # a quoted field can span lines; report where the row begins
        previous_end = reader.line_num
        if not any(field.strip() for field in record):
            blank.append(start)
            continue
        if header is None:
            header, header_line = tuple(record), start
            continue
        cells: tuple[Cell, ...] = tuple(field if field != "" else None for field in record)
        rows.append(RawRow(line=start, cells=cells))

    if header is None:
        return (), 0, [], blank
    # Blank lines before the header are not data and are not reported.
    return header, header_line, rows, [line for line in blank if line > header_line]
