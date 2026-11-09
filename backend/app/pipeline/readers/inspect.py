"""Read every file in a folder and print what each one turned out to be.

    python -m app.pipeline.readers.inspect ../data

A first look at a week's files, before any cleaning: format, encoding,
delimiter, header, row count, and anything the reader noticed. Prints headers
and counts only — never row values — so the output is safe to paste anywhere.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

from app.errors import MirsadError

from . import read_file


def main(folder: str) -> int:
    root = Path(folder)
    files = sorted(p for p in root.rglob("*") if p.is_file() and not p.name.startswith("."))
    by_hash: dict[str, list[str]] = defaultdict(list)
    failures = 0

    for path in files:
        label = str(path.relative_to(root))
        try:
            table = read_file(path)
        except MirsadError as error:
            failures += 1
            print(f"{label}\n    REFUSED {error.code.value} ({error.severity.value}) {error.context}")
            continue

        s = table.source
        by_hash[s.sha256].append(label)
        notes = []
        if s.extension_mismatch:
            notes.append(f"named .{s.declared_extension}, is {s.detected_format}")
        if s.had_bom:
            notes.append("BOM")
        if table.blank_lines:
            notes.append(f"{len(table.blank_lines)} blank rows inside the data")
        if table.width_mismatch_lines:
            notes.append(f"{len(table.width_mismatch_lines)} rows not {len(table.header)} cells wide")
        if table.excel_date_cells:
            notes.append(f"{len(table.excel_date_cells)} real Excel date cells")
        detail = " ".join(x for x in (s.detected_format, s.encoding, repr(s.delimiter) if s.delimiter else None) if x)
        print(f"{label}\n    {detail} · {len(table.rows)} rows · header {list(table.header)}")
        for note in notes:
            print(f"    ! {note}")

    duplicates = [names for names in by_hash.values() if len(names) > 1]
    for names in duplicates:
        print(f"IDENTICAL BYTES: {', '.join(names)}")
    print(f"\n{len(files)} files · {len(files) - failures} read · {failures} refused · {len(duplicates)} duplicate sets")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "../data"))
