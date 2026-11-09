"""Returns, however a till records them (M-011). Pure.

Two conventions in the real files:

- **Negative amount** — eight branches. ``-570.65`` is a refund.
- **Positive amount, ``RTN`` in the notes** — Jericho and Salfit. ``90`` with
  note ``RTN`` is a refund of 90. Read naively it is a *sale*, and the branch
  looks like it sold twice what it refunded: the error that inverts a branch
  at the review. Rania has been flipping these by hand for four years.

Here the flip is made in code, **and recorded on every row it touches**
(``ROW_RETURN_SIGN_FLIPPED``), so the correction that lived only in one
person's habit is now visible and traceable.

A negative row that also says ``RTN`` is already a refund; it is not flipped
twice.

A file with many sales and **no returns at all** is itself a finding: shops
refund things, so silence usually means returns are recorded somewhere else
or not at all (Tulkarem's hand-typed weeks) — ``FILE_NO_RETURNS``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

# Only the marker the tills actually use. Another word ("refund", "مرتجع")
# is not assumed to mean the same until it is seen and confirmed (D-020).
_RTN = re.compile(r"(?<![A-Za-z])RTN(?![A-Za-z])", re.IGNORECASE)

# Below this many rows, a week without returns is unremarkable.
NO_RETURNS_MIN_ROWS = 50


@dataclass(frozen=True)
class Signed:
    amount: Decimal
    is_return: bool
    flipped: bool  # the sign was changed here, from a positive RTN row


def is_rtn(note: str | None) -> bool:
    return bool(note) and _RTN.search(note) is not None


def signed_amount(amount: Decimal, note: str | None) -> Signed:
    if amount < 0:
        return Signed(amount, True, False)
    if is_rtn(note):
        return Signed(-amount, True, amount != 0)
    return Signed(amount, False, False)


def convention(returns_by_negative: int, returns_by_note: int) -> str | None:
    """How a file records returns, for the report: ``negative``, ``rtn_note``, ``both`` or None."""
    if returns_by_negative and returns_by_note:
        return "both"
    if returns_by_negative:
        return "negative"
    if returns_by_note:
        return "rtn_note"
    return None
