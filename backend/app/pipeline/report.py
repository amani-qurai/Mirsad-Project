"""The rejection report: what came in, what was kept, what was not, and why (M-009, M-017).

Built per batch — one Sunday's files — before any cleaning. Every number in it
traces to line numbers, so "we could not use these fourteen rows" can always
be followed by *which* fourteen.

The report is data: codes, counts and lines. It holds no sentences (NN-6); the
interface renders it through ``t()``. The ``render_text`` function below is a
developer's console view and is not shown to users.

    python -m app.pipeline.report ../data/week-01
"""

from __future__ import annotations

import hashlib
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.errors import SEVERITY, ErrorCode, MirsadError, Severity
from app.pipeline.headers import AmountBasis, Field, map_headers
from app.pipeline.readers import read_bytes
from app.pipeline.validate import RowResult, Scope, check_rows


@dataclass(frozen=True)
class FileReport:
    name: str
    sha256: str
    # None when the file was read and checked; otherwise the file-level code
    # that stopped it, and the rows were not examined.
    file_code: ErrorCode | None = None
    file_context: dict[str, Any] = field(default_factory=dict)
    detected_format: str | None = None
    extension_mismatch: bool = False
    amount_basis: AmountBasis | None = None
    fields_absent: tuple[Field, ...] = ()  # columns this file does not have at all
    rows: tuple[RowResult, ...] = ()

    @property
    def rows_in(self) -> int:
        return len(self.rows)

    @property
    def rows_kept(self) -> int:
        return sum(r.kept for r in self.rows)

    @property
    def rows_rejected(self) -> int:
        return self.rows_in - self.rows_kept

    @property
    def rows_held(self) -> int:
        return sum(r.severity is Severity.HELD for r in self.rows)

    @property
    def rows_with_warnings(self) -> int:
        return sum(r.severity is Severity.WARNING for r in self.rows)

    def lines_by_code(self) -> dict[ErrorCode, list[int]]:
        out: dict[ErrorCode, list[int]] = defaultdict(list)
        for row in self.rows:
            for code in dict.fromkeys(f.code for f in row.findings):
                out[code].append(row.line)
        return dict(out)

    def lines_outside(self, scope: Scope) -> list[int]:
        """Kept rows that do not count towards ``scope`` — the completeness gap."""
        return [r.line for r in self.rows if r.kept and scope not in r.scope]

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.name,
            "sha256": self.sha256,
            "file_code": self.file_code.value if self.file_code else None,
            "file_severity": SEVERITY[self.file_code].value if self.file_code else None,
            "file_context": self.file_context,
            "detected_format": self.detected_format,
            "extension_mismatch": self.extension_mismatch,
            "amount_basis": self.amount_basis.value if self.amount_basis else None,
            "fields_absent": [f.value for f in self.fields_absent],
            "rows": {
                "in": self.rows_in,
                "kept": self.rows_kept,
                "rejected": self.rows_rejected,
                "held": self.rows_held,
                "warning": self.rows_with_warnings,
            },
            "codes": {
                code.value: {"severity": SEVERITY[code].value, "count": len(lines), "lines": lines}
                for code, lines in self.lines_by_code().items()
            },
            "outside_scope": {scope.value: self.lines_outside(scope) for scope in (Scope.PRODUCT, Scope.QUANTITY)},
        }


@dataclass(frozen=True)
class BatchReport:
    files: tuple[FileReport, ...]

    @property
    def files_refused(self) -> list[FileReport]:
        return [f for f in self.files if f.file_code is not None]

    def totals(self) -> dict[str, int]:
        read = [f for f in self.files if f.file_code is None]
        return {
            "files": len(self.files),
            "files_read": len(read),
            "files_refused": len(self.files) - len(read),
            "rows_in": sum(f.rows_in for f in read),
            "rows_kept": sum(f.rows_kept for f in read),
            "rows_rejected": sum(f.rows_rejected for f in read),
            "rows_held": sum(f.rows_held for f in read),
            "rows_with_warnings": sum(f.rows_with_warnings for f in read),
        }

    def code_counts(self) -> Counter[ErrorCode]:
        counts: Counter[ErrorCode] = Counter()
        for f in self.files:
            for code, lines in f.lines_by_code().items():
                counts[code] += len(lines)
            if f.file_code is not None:
                counts[f.file_code] += 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "totals": self.totals(),
            "codes": {code.value: n for code, n in self.code_counts().most_common()},
            "files": [f.to_dict() for f in self.files],
        }


def report_file(data: bytes, name: str, seen: dict[str, str] | None = None) -> FileReport:
    """Read, map and check one file. ``seen`` maps sha256 → name for this batch."""
    digest = hashlib.sha256(data).hexdigest()
    if seen is not None:
        if digest in seen:
            return FileReport(name, digest, ErrorCode.FILE_EXACT_DUPLICATE, {"file": name, "same_as": seen[digest]})
        seen[digest] = name

    try:
        table = read_bytes(data, name)
        mapping = map_headers(table)
    except MirsadError as error:
        return FileReport(name, digest, error.code, error.context)

    return FileReport(
        name=name,
        sha256=digest,
        detected_format=table.source.detected_format,
        extension_mismatch=table.source.extension_mismatch,
        amount_basis=mapping.amount_basis,
        fields_absent=tuple(f for f in Field if not mapping.has(f)),
        rows=check_rows(table, mapping),
    )


def report_batch(paths: list[Path]) -> BatchReport:
    """One batch, in the order given. The first of two identical files is the one kept."""
    seen: dict[str, str] = {}
    return BatchReport(tuple(report_file(p.read_bytes(), p.name, seen) for p in paths))


def render_text(report: BatchReport) -> str:
    """Developer console view. Not user-facing: the UI renders the dict through t()."""
    out = []
    for f in report.files:
        if f.file_code is not None:
            out.append(f"{f.name:<38} REFUSED  {f.file_code.value} ({SEVERITY[f.file_code].value})")
            continue
        codes = ", ".join(f"{code.value}×{len(lines)}" for code, lines in sorted(f.lines_by_code().items()))
        flags = []
        if f.extension_mismatch:
            flags.append(f"is {f.detected_format}")
        if f.amount_basis is AmountBasis.EX_VAT:
            flags.append("PRE-VAT")
        flag = f" [{', '.join(flags)}]" if flags else ""
        out.append(
            f"{f.name:<38} in {f.rows_in:>4} · kept {f.rows_kept:>4} · rejected {f.rows_rejected:>2}"
            f" · no product {len(f.lines_outside(Scope.PRODUCT)):>3}{flag}"
        )
        if codes:
            out.append(f"{'':<38} {codes}")
    t = report.totals()
    out.append("")
    out.append(
        f"{t['files']} files ({t['files_refused']} refused) · {t['rows_in']} rows in · {t['rows_kept']} kept · "
        f"{t['rows_rejected']} rejected · {t['rows_held']} held · {t['rows_with_warnings']} with warnings"
    )
    for code, n in report.code_counts().most_common():
        out.append(f"  {code.value:<28} {SEVERITY[code].value:<9} {n}")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    import json

    as_json = "--json" in argv
    folders = [Path(a) for a in argv if not a.startswith("--")] or [Path("../data")]
    paths = sorted(p for folder in folders for p in folder.rglob("*") if p.is_file() and not p.name.startswith("."))
    report = report_batch(paths)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) if as_json else render_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
