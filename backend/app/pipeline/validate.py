"""Row checks that need no parsing: is each required value there at all? (M-009)

This runs **before any cleaning**. It answers "what came in, what can be kept,
what cannot, and why" from presence alone. Whether ``10/03/2026`` is March or
October, or whether ``٣٤٦٫٠١`` is a number, is decided later by
``domain/dates`` and ``domain/numbers``, which add their own findings.

Every row gets a result, including clean ones, so the counts always add up:
rows in = kept + rejected. Nothing is dropped (NN-7) — a rejected row keeps its
line number and raw cells and stays viewable.

Two axes per row:

- **severity** — the worst finding: rejected, held, warning, or none.
- **scope** — which figures the row may count towards. A row with a date and
  an amount but no product belongs in its branch's total and not in the
  product breakdown.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.errors import SEVERITY, ErrorCode, Severity, worst
from app.pipeline.headers import Field, HeaderMapping
from app.pipeline.readers import RawRow, RawTable


class Scope(StrEnum):
    TOTAL = "total"        # needs date and amount
    PRODUCT = "product"    # also needs a product
    QUANTITY = "quantity"  # also needs a quantity


@dataclass(frozen=True)
class Finding:
    code: ErrorCode
    context: dict[str, Any] = field(default_factory=dict)

    @property
    def severity(self) -> Severity:
        return SEVERITY[self.code]


@dataclass(frozen=True)
class RowResult:
    line: int
    findings: tuple[Finding, ...]
    scope: frozenset[Scope]

    @property
    def severity(self) -> Severity | None:
        return worst(f.severity for f in self.findings)

    @property
    def kept(self) -> bool:
        return self.severity is not Severity.REJECTED


def _value(row: RawRow, mapping: HeaderMapping, f: Field) -> str | None:
    """The cell for a field, or None if it is empty or whitespace."""
    index = mapping.columns.get(f)
    if index is None or index >= len(row.cells):
        return None
    cell = row.cells[index]
    return cell if cell is not None and cell.strip() else None


def check_rows(table: RawTable, mapping: HeaderMapping) -> tuple[RowResult, ...]:
    findings: dict[int, list[Finding]] = {row.line: [] for row in table.rows}

    for row in table.rows:
        found = findings[row.line]
        if _value(row, mapping, Field.DATE) is None:
            found.append(Finding(ErrorCode.ROW_MISSING_DATE))
        if _value(row, mapping, Field.AMOUNT) is None:
            found.append(Finding(ErrorCode.ROW_MISSING_AMOUNT))
        if _value(row, mapping, Field.PRODUCT_NAME) is None:
            # The code alone never identifies a product (product code eras,
            # M-012), so a code without a name is still a missing product.
            code = _value(row, mapping, Field.PRODUCT_CODE)
            found.append(Finding(ErrorCode.ROW_MISSING_PRODUCT, {"product_code": code}))
        if mapping.has(Field.QUANTITY) and _value(row, mapping, Field.QUANTITY) is None:
            found.append(Finding(ErrorCode.ROW_MISSING_QUANTITY))
        if mapping.has(Field.TXN_ID) and _value(row, mapping, Field.TXN_ID) is None:
            found.append(Finding(ErrorCode.TXN_ID_MISSING))

    if mapping.has(Field.TXN_ID):
        _check_repeated_ids(table, mapping, findings)

    results = []
    for row in table.rows:
        # Every finding carries its line, so a message can name it without a lookup.
        found = tuple(Finding(f.code, {**f.context, "line": row.line}) for f in findings[row.line])
        results.append(RowResult(row.line, found, _scope(row, mapping, found)))
    return tuple(results)


def _check_repeated_ids(table: RawTable, mapping: HeaderMapping, findings: dict[int, list[Finding]]) -> None:
    """Same id twice: a duplicate only if the whole row is identical (D-013).

    Ramallah's till restarted its numbering, so the same id appears on
    different sales in one file. Rejecting those would delete real sales.
    """
    by_id: dict[str, list[RawRow]] = defaultdict(list)
    for row in table.rows:
        txn = _value(row, mapping, Field.TXN_ID)
        if txn is not None:
            by_id[txn].append(row)

    for txn, rows in by_id.items():
        if len(rows) < 2:
            continue
        first_with_cells: dict[tuple[str | None, ...], int] = {}
        distinct_lines: list[int] = []
        for row in rows:
            if row.cells in first_with_cells:
                findings[row.line].append(
                    Finding(ErrorCode.TXN_DUPLICATE_WITHIN_FILE, {"txn_id": txn, "same_as_line": first_with_cells[row.cells]})
                )
            else:
                first_with_cells[row.cells] = row.line
                distinct_lines.append(row.line)
        if len(distinct_lines) > 1:
            for line in distinct_lines:
                findings[line].append(Finding(ErrorCode.TXN_ID_REUSED, {"txn_id": txn, "lines": distinct_lines}))


def _scope(row: RawRow, mapping: HeaderMapping, found: tuple[Finding, ...]) -> frozenset[Scope]:
    if worst(f.severity for f in found) is Severity.REJECTED:
        return frozenset()
    scope = {Scope.TOTAL}
    if _value(row, mapping, Field.PRODUCT_NAME) is not None:
        scope.add(Scope.PRODUCT)
    if _value(row, mapping, Field.QUANTITY) is not None:
        scope.add(Scope.QUANTITY)
    return frozenset(scope)
