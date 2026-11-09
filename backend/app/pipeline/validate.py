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

import datetime as dt
from collections import defaultdict
from decimal import Decimal
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.domain.dates import FileDates, Period, infer_dates
from app.domain.matching import Catalogue
from app.domain.numbers import parse_amount
from app.domain.returns import convention, signed_amount
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
    date: dt.date | None = None  # set only when the date is certain or inferred, never guessed
    product: int | None = None  # set only when matched or newly created, never guessed
    amount: Decimal | None = None  # signed: a refund is negative, however the till wrote it
    is_return: bool = False
    quantity: Decimal | None = None

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


@dataclass(frozen=True)
class TableCheck:
    rows: tuple[RowResult, ...]
    dates: FileDates
    return_convention: str | None = None  # "negative", "rtn_note", "both", or None: no returns at all


def check_rows(
    table: RawTable,
    mapping: HeaderMapping,
    period: Period | None = None,
    catalogue: Catalogue | None = None,
) -> TableCheck:
    """Check every row.

    ``period`` is the week the file covers, if known (D-015). ``catalogue``
    is the product catalogue to match against; it is updated as new products
    are found, so files must be checked in the order they arrived.
    """
    findings: dict[int, list[Finding]] = {row.line: [] for row in table.rows}
    amounts: dict[int, Decimal] = {}
    quantities: dict[int, Decimal] = {}
    returns: dict[int, str] = {}

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

        raw_amount = _value(row, mapping, Field.AMOUNT)
        if raw_amount is not None:
            parsed = parse_amount(raw_amount)
            if parsed.ambiguous:
                found.append(Finding(ErrorCode.ROW_AMOUNT_AMBIGUOUS, {
                    "value": raw_amount, "candidates": [str(c) for c in parsed.candidates],
                }))
            elif parsed.value is None:
                found.append(Finding(ErrorCode.ROW_AMOUNT_UNPARSEABLE, {"value": raw_amount}))
            else:
                signed = signed_amount(parsed.value, _value(row, mapping, Field.NOTES))
                amounts[row.line] = signed.amount
                if signed.is_return:
                    returns[row.line] = "rtn_note" if signed.flipped or parsed.value >= 0 else "negative"
                if signed.flipped:
                    found.append(Finding(ErrorCode.ROW_RETURN_SIGN_FLIPPED, {
                        "value": raw_amount, "note": _value(row, mapping, Field.NOTES),
                    }))
        raw_quantity = _value(row, mapping, Field.QUANTITY)
        if raw_quantity is not None:
            quantity = parse_amount(raw_quantity).value
            if quantity is None:
                found.append(Finding(ErrorCode.ROW_QUANTITY_UNPARSEABLE, {"value": raw_quantity}))
            else:
                quantities[row.line] = quantity
        if mapping.has(Field.TXN_ID) and _value(row, mapping, Field.TXN_ID) is None:
            found.append(Finding(ErrorCode.TXN_ID_MISSING))

    if mapping.has(Field.TXN_ID):
        _check_repeated_ids(table, mapping, findings)

    # Dates are decided once for the whole file (M-006). An empty date is
    # already ROW_MISSING_DATE above, so infer_dates returns None for it.
    dates = infer_dates([_value(row, mapping, Field.DATE) for row in table.rows], period)
    for row, result in zip(table.rows, dates.results):
        if result is not None and result.code is not None:
            findings[row.line].append(Finding(result.code, result.context))

    products: dict[int, int | None] = {}
    if catalogue is not None:
        for row in table.rows:
            name = _value(row, mapping, Field.PRODUCT_NAME)
            if name is None:
                continue  # already ROW_MISSING_PRODUCT
            match = catalogue.match(name, _value(row, mapping, Field.PRODUCT_CODE))
            products[row.line] = match.product
            if match.code is not None:
                findings[row.line].append(Finding(match.code, match.context))

    results = []
    for row, result in zip(table.rows, dates.results):
        # Every finding carries its line, so a message can name it without a lookup.
        found = tuple(Finding(f.code, {**f.context, "line": row.line}) for f in findings[row.line])
        when = result.value if result is not None else None
        results.append(RowResult(
            row.line, found, _scope(row, mapping, found), when, products.get(row.line),
            amounts.get(row.line), row.line in returns, quantities.get(row.line),
        ))
    by_kind = list(returns.values())
    return TableCheck(
        tuple(results), dates, convention(by_kind.count("negative"), by_kind.count("rtn_note")),
    )


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


# What a held finding withholds the row from (D-018). A question about the
# date withholds it from everything; a question about the product only from
# product figures — the sale still happened at that branch on that day.
WITHHOLDS: dict[ErrorCode, Scope] = {
    ErrorCode.DATE_FORMAT_AMBIGUOUS: Scope.TOTAL,
    ErrorCode.ROW_DATE_OUT_OF_RANGE: Scope.TOTAL,
    ErrorCode.ROW_AMOUNT_AMBIGUOUS: Scope.TOTAL,
    ErrorCode.ROW_QUANTITY_UNPARSEABLE: Scope.QUANTITY,
    ErrorCode.PRODUCT_MATCH_UNCONFIRMED: Scope.PRODUCT,
    ErrorCode.PRODUCT_NAME_CONFLICT: Scope.PRODUCT,
}


def _scope(row: RawRow, mapping: HeaderMapping, found: tuple[Finding, ...]) -> frozenset[Scope]:
    """Which figures this row may count towards. Each scope needs the one before it."""
    withheld = {WITHHOLDS[f.code] for f in found if f.code in WITHHOLDS}
    if worst(f.severity for f in found) is Severity.REJECTED or Scope.TOTAL in withheld:
        return frozenset()
    scope = {Scope.TOTAL}
    if _value(row, mapping, Field.PRODUCT_NAME) is not None and Scope.PRODUCT not in withheld:
        scope.add(Scope.PRODUCT)
        if _value(row, mapping, Field.QUANTITY) is not None and Scope.QUANTITY not in withheld:
            scope.add(Scope.QUANTITY)
    return frozenset(scope)
