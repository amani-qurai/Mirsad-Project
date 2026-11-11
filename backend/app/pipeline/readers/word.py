"""Word tables — Tulkarem's hand-typed weekly sales (M-008, DECISIONS.md D-003).

These files are read so they can be *shown*, marked ``unverified_source`` and
kept out of every ranking (M-034). Reading them is not trusting them.
"""

from __future__ import annotations

import io

import docx

from app.errors import ErrorCode, MirsadError


def read_word_table(data: bytes, name: str) -> tuple[tuple[str, ...], list[tuple[str, ...]]]:
    """Return ``(preamble paragraphs, table rows as text)`` for the single table holding data."""
    document = docx.Document(io.BytesIO(data))

    tables = [
        [tuple(cell.text for cell in row.cells) for row in table.rows]
        for table in document.tables
    ]
    tables = [t for t in tables if any(text.strip() for row in t for text in row)]

    if not tables:
        raise MirsadError(ErrorCode.FILE_EMPTY, {"file": name})
    if len(tables) > 1:
        raise MirsadError(
            ErrorCode.FILE_TABLE_AMBIGUOUS,
            {"file": name, "count": len(tables), "tables": [f"table {i}" for i in range(1, len(tables) + 1)]},
        )

    # The heading paragraphs say which branch and week the person typed this
    # for, and that the till was down. Kept verbatim for the drill-down view.
    preamble = tuple(p.text for p in document.paragraphs if p.text.strip())
    return preamble, tables[0]
