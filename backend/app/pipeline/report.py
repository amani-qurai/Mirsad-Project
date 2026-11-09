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

from app.domain.dates import Order
from app.errors import SEVERITY, ErrorCode, MirsadError, Severity
from app.pipeline.filenames import parse_file_name
from app.pipeline.headers import AmountBasis, Field, map_headers
from app.pipeline.readers import read_bytes
from app.pipeline.validate import Finding, RowResult, Scope, check_rows


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
    branch: str | None = None  # from the file name, when it follows the pattern
    week_start: str | None = None
    date_order: Order | None = None
    date_order_evidence: str | None = None  # "file" or "week"
    # File-level findings that do not stop the rows being read, e.g. a change
    # in date format. A held one holds every kept row in the file.
    file_findings: tuple[Finding, ...] = ()
    rows: tuple[RowResult, ...] = ()

    @property
    def held_file(self) -> bool:
        return any(f.severity is Severity.HELD for f in self.file_findings)

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
        if self.held_file:
            return self.rows_kept  # every usable row waits for the one file-level answer
        return sum(r.severity is Severity.HELD for r in self.rows)

    @property
    def rows_with_warnings(self) -> int:
        if self.held_file:
            return 0
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
            "branch": self.branch,
            "week_start": self.week_start,
            "date_order": self.date_order.value if self.date_order else None,
            "date_order_evidence": self.date_order_evidence,
            "file_findings": [
                {"code": f.code.value, "severity": f.severity.value, "context": f.context} for f in self.file_findings
            ],
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
            "files_held": sum(f.held_file for f in read),
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
            for finding in f.file_findings:
                counts[finding.code] += 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "totals": self.totals(),
            "codes": {code.value: n for code, n in self.code_counts().most_common()},
            "files": [f.to_dict() for f in self.files],
        }


def report_file(
    data: bytes,
    name: str,
    seen: dict[str, str] | None = None,
    date_orders: dict[str, Order] | None = None,
) -> FileReport:
    """Read, map and check one file.

    ``seen`` maps sha256 → name for this batch. ``date_orders`` maps branch →
    the date order of its last file; it is read to detect a change and updated.
    """
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

    parsed = parse_file_name(name)
    check = check_rows(table, mapping, parsed.period if parsed else None)
    order = check.dates.order
    file_findings: list[Finding] = []

    if check.dates.conflicting:
        # Values only readable as day/month and values only readable as
        # month/day in one file: the till changed format mid-file.
        file_findings.append(Finding(ErrorCode.FILE_DATE_FORMAT_CHANGED, {"file": name, "within_file": True}))
    elif parsed is not None and date_orders is not None and order is not None:
        previous = date_orders.get(parsed.branch)
        if previous is not None and previous is not order:
            file_findings.append(
                Finding(
                    ErrorCode.FILE_DATE_FORMAT_CHANGED,
                    {"file": name, "branch": parsed.branch, "previous": previous.value, "current": order.value},
                )
            )
        date_orders[parsed.branch] = order

    return FileReport(
        name=name,
        sha256=digest,
        detected_format=table.source.detected_format,
        extension_mismatch=table.source.extension_mismatch,
        amount_basis=mapping.amount_basis,
        fields_absent=tuple(f for f in Field if not mapping.has(f)),
        branch=parsed.branch if parsed else None,
        week_start=parsed.week_start.isoformat() if parsed else None,
        date_order=order,
        date_order_evidence=check.dates.order_evidence,
        file_findings=tuple(file_findings),
        rows=check.rows,
    )


def report_batch(paths: list[Path]) -> BatchReport:
    """One batch, in the order given — oldest week first, so a change in a
    branch's date format is caught in the file where it happens. The first of
    two identical files is the one kept."""
    seen: dict[str, str] = {}
    orders: dict[str, Order] = {}
    return BatchReport(tuple(report_file(p.read_bytes(), p.name, seen, orders) for p in paths))


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
        if f.date_order is not None:
            flags.append(f"dates {f.date_order.value}" + (" (by week)" if f.date_order_evidence == "week" else ""))
        for finding in f.file_findings:
            flags.append(f"{finding.severity.value.upper()} {finding.code.value} {finding.context.get('previous', '')}→{finding.context.get('current', '')}")
        flag = f" [{', '.join(flags)}]" if flags else ""
        out.append(
            f"{f.name:<38} in {f.rows_in:>4} · kept {f.rows_kept:>4} · rejected {f.rows_rejected:>2}"
            f" · held {f.rows_held:>3} · no product {len(f.lines_outside(Scope.PRODUCT)):>3}{flag}"
        )
        if codes:
            out.append(f"{'':<38} {codes}")
    t = report.totals()
    out.append("")
    out.append(
        f"{t['files']} files ({t['files_refused']} refused, {t['files_held']} held) · {t['rows_in']} rows in · {t['rows_kept']} kept · "
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
