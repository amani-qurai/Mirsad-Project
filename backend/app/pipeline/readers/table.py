"""The one shape every reader returns.

A reader's only job is to get the cells out of the file **exactly as the file
presented them**. It does not parse dates, numbers or names, does not trim, and
does not repair. Those decisions belong to ``domain/`` where an ambiguous value
can be *held* instead of silently resolved (DECISIONS.md D-009).

Conventions shared by all formats:

- Every cell is a ``str`` or ``None``. ``None`` means the cell was empty.
- ``line`` is 1-based and points at the place in the original file a person
  would look: the text line in a CSV, the row number in a sheet, the row index
  in a Word table. It is what drill-down shows next to the raw row (NN-7).
- Fully blank rows are not returned as rows, but their line numbers are kept
  in ``blank_lines`` so the count is never lost.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import pandas as pd

Format = Literal["xlsx", "csv", "docx"]

Cell = str | None


@dataclass(frozen=True)
class SourceFile:
    """What the file turned out to be — which is not always what it claimed."""

    name: str
    size: int
    sha256: str
    declared_extension: str  # from the file name, lower-case, without the dot
    detected_format: Format  # from the content
    encoding: str | None = None  # text formats only
    had_bom: bool = False
    delimiter: str | None = None  # CSV only
    container: str | None = None  # the sheet name, or "table 1" for Word
    preamble: tuple[str, ...] = ()  # Word: the document's non-empty paragraphs

    @property
    def extension_mismatch(self) -> bool:
        """True when the name says one format and the bytes say another.

        Bethlehem's CSV arrives named ``.xls``. That is worth telling the user
        about at upload — it is one of the "open this file first" signals.
        """
        return self.declared_extension != self.detected_format


@dataclass(frozen=True)
class RawRow:
    line: int
    cells: tuple[Cell, ...]


@dataclass(frozen=True)
class RawTable:
    source: SourceFile
    header: tuple[str, ...]
    header_line: int
    rows: tuple[RawRow, ...]
    blank_lines: tuple[int, ...] = ()
    # (line, column index) of Excel cells that were stored as real dates and
    # written out as ISO text. Kept so the conversion is never invisible.
    excel_date_cells: tuple[tuple[int, int], ...] = field(default=())

    @property
    def width_mismatch_lines(self) -> tuple[int, ...]:
        """Rows with more or fewer cells than the header.

        In a CSV this usually means an unquoted delimiter inside a value. The
        row is kept as it is; deciding what it means is validation's job.
        """
        width = len(self.header)
        return tuple(r.line for r in self.rows if len(r.cells) != width)

    def to_dataframe(self) -> pd.DataFrame:
        """A text-only DataFrame: every column is ``object`` holding ``str`` or ``None``.

        pandas is never allowed to infer types here — that would decide the
        date and number questions before anything could flag them. The
        ``_line`` column carries each row's position in the original file.
        Columns beyond the header (ragged rows) are named ``_extra_<n>``.
        """
        width = max([len(self.header), *(len(r.cells) for r in self.rows)])
        columns = list(self.header) + [f"_extra_{i}" for i in range(len(self.header), width)]
        data = [list(r.cells) + [None] * (width - len(r.cells)) for r in self.rows]
        frame = pd.DataFrame(data, columns=columns, dtype=object)
        frame.insert(0, "_line", [r.line for r in self.rows])
        return frame
