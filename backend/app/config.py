"""Values that belong in configuration, not in code (CLAUDE.md: never a literal).

Read once here, so a change is one edit, reviewed in one place.
"""

from __future__ import annotations

from decimal import Decimal

# Palestinian VAT. Used only to *suggest* the correction for a branch whose
# amounts are pre-VAT; the correction itself is a person's decision (D-021).
VAT_RATE = Decimal("0.16")

MONEY_PLACES = Decimal("0.01")
