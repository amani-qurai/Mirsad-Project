"""The error-code catalogue — the only source of API error strings (NN-6).

The server never returns prose. It returns a code and structured context; the
frontend renders ``t('errors.<CODE>', context)`` from ``ar.json`` / ``en.json``.

Codes are added here only when something in the code actually raises them, and
each one ships with its message in both locales in the same commit. The design
intent for the full set is in
``.claude/skills/mirsad-conventions/references/error-codes.md``.
"""

from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    WARNING = "warning"    # usable, flagged
    HELD = "held"          # a human must decide before it is trusted
    REJECTED = "rejected"  # unusable; kept and listed with its reason


class ErrorCode(StrEnum):
    # ── File level ──────────────────────────────────────────────────────────
    FILE_FORMAT_UNSUPPORTED = "FILE_FORMAT_UNSUPPORTED"
    FILE_ENCODING_UNDETECTED = "FILE_ENCODING_UNDETECTED"
    FILE_DELIMITER_UNDETECTED = "FILE_DELIMITER_UNDETECTED"
    FILE_TABLE_AMBIGUOUS = "FILE_TABLE_AMBIGUOUS"
    FILE_EMPTY = "FILE_EMPTY"
    FILE_HEADERS_UNRECOGNISED = "FILE_HEADERS_UNRECOGNISED"
    FILE_EXACT_DUPLICATE = "FILE_EXACT_DUPLICATE"
    # ── Row level ───────────────────────────────────────────────────────────
    ROW_MISSING_DATE = "ROW_MISSING_DATE"
    ROW_MISSING_AMOUNT = "ROW_MISSING_AMOUNT"
    ROW_MISSING_PRODUCT = "ROW_MISSING_PRODUCT"
    ROW_MISSING_QUANTITY = "ROW_MISSING_QUANTITY"
    # ── Transactions ────────────────────────────────────────────────────────
    TXN_ID_MISSING = "TXN_ID_MISSING"
    TXN_ID_REUSED = "TXN_ID_REUSED"
    TXN_DUPLICATE_WITHIN_FILE = "TXN_DUPLICATE_WITHIN_FILE"


SEVERITY: dict[ErrorCode, Severity] = {
    ErrorCode.FILE_FORMAT_UNSUPPORTED: Severity.REJECTED,
    ErrorCode.FILE_ENCODING_UNDETECTED: Severity.REJECTED,
    ErrorCode.FILE_DELIMITER_UNDETECTED: Severity.REJECTED,
    # A person can say which sheet or table holds the sales, so it is held.
    ErrorCode.FILE_TABLE_AMBIGUOUS: Severity.HELD,
    ErrorCode.FILE_EMPTY: Severity.REJECTED,
    # A person says once what the column is, and the answer is remembered.
    ErrorCode.FILE_HEADERS_UNRECOGNISED: Severity.HELD,
    ErrorCode.FILE_EXACT_DUPLICATE: Severity.REJECTED,
    ErrorCode.ROW_MISSING_DATE: Severity.REJECTED,
    ErrorCode.ROW_MISSING_AMOUNT: Severity.REJECTED,
    # Counted in the branch total, left out of the product breakdown, and said so.
    ErrorCode.ROW_MISSING_PRODUCT: Severity.WARNING,
    ErrorCode.ROW_MISSING_QUANTITY: Severity.WARNING,
    ErrorCode.TXN_ID_MISSING: Severity.WARNING,
    # Same id, different sale: the till restarted its numbering. Not a duplicate (D-013).
    ErrorCode.TXN_ID_REUSED: Severity.WARNING,
    # Same id and every cell identical: the same line exported twice.
    ErrorCode.TXN_DUPLICATE_WITHIN_FILE: Severity.REJECTED,
}

_RANK = {Severity.WARNING: 1, Severity.HELD: 2, Severity.REJECTED: 3}


def worst(severities: Iterable[Severity]) -> Severity | None:
    """The most serious severity in a set, or None if there is nothing to report."""
    return max(severities, key=_RANK.__getitem__, default=None)


class MirsadError(Exception):
    """An error that reaches the client as a code, never as a sentence."""

    def __init__(self, code: ErrorCode, context: dict[str, Any] | None = None) -> None:
        self.code = code
        self.context = dict(context or {})
        super().__init__(code.value)

    @property
    def severity(self) -> Severity:
        return SEVERITY[self.code]

    def to_dict(self) -> dict[str, Any]:
        return {"error": {"code": self.code.value, "context": self.context}}
