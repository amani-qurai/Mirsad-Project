"""Product matching, block-one ladder: exact and confirmed spellings only (M-013, D-018).

The full ladder in the conventions adds fuzzy scoring. Block one deliberately
stops short of it (PROJECT-PLAN §7.1): **anything not already known is either
a new product or a question for a person — never a guess.** Rania's answers
become the labelled data the fuzzy thresholds are tuned against in block two.

For each row, in order:

1. **Lost characters** (``?`` where Jenin's till dropped a digit, D-011): only
   a spelling a person has already confirmed matches. Otherwise held, with the
   product its code points to as the suggestion. Never creates a product.
2. **Exact spelling** already in the catalogue → matched.
3. **Same comparison key** (``domain/arabic``) as a known spelling → matched.
   For 2 and 3: if the row's code belongs to a *different* product, the row
   is held as a conflict instead (``PRODUCT_NAME_CONFLICT``).
4. **Unknown spelling, but there is a candidate** — its code belongs to a
   known product, or the same key is already waiting for a person → held
   (``PRODUCT_MATCH_UNCONFIRMED``) with the candidates. One answer resolves
   every row with that spelling.
5. **Unknown spelling, no candidate at all** → a new product
   (``PRODUCT_NEW``). A fake new product is visible and fixable; a wrong
   merge is invisible.

The code is evidence, never identity: it can *suggest* a product, but a name
the catalogue does not know is never filed under a product on the code alone
(product code eras, M-012).

Pure: no I/O. The ``Catalogue`` is state passed in and updated in memory;
storing it is the repositories' job.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.domain.arabic import normalise_for_matching
from app.errors import ErrorCode

LOST_CHARACTER = "?"


class Rung(StrEnum):
    EXACT = "exact"
    NORMALISED = "normalised"
    NEW = "new"


@dataclass
class Product:
    id: int
    name: str  # the first spelling seen — a display default a person can rename
    codes: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class Match:
    product: int | None  # None while a person's answer is needed
    rung: Rung | None
    code: ErrorCode | None = None  # None: matched cleanly
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class Catalogue:
    products: dict[int, Product] = field(default_factory=dict)
    spellings: dict[str, int] = field(default_factory=dict)  # exact spelling → product
    keys: dict[str, int] = field(default_factory=dict)  # comparison key → product
    code_owner: dict[str, int] = field(default_factory=dict)  # product code → product
    pending: dict[str, set[int]] = field(default_factory=dict)  # key → candidate products

    # ── A person's answers ───────────────────────────────────────────────────

    def confirm(self, spelling: str, product: int, code: str | None = None) -> None:
        """A person says this spelling is this product. Every later row with it matches.

        Passing the code the spelling arrived with also accepts that pairing,
        which is how a name/code conflict is resolved.
        """
        self.spellings[spelling] = product
        if code:
            self.products[product].codes.add(code)
        if LOST_CHARACTER not in spelling:
            key = normalise_for_matching(spelling)
            self.keys[key] = product
            self.pending.pop(key, None)

    def confirm_new(self, spelling: str, code: str | None = None) -> int:
        """A person says this spelling is a product the catalogue does not have."""
        product = self._create(spelling, code)
        self.pending.pop(normalise_for_matching(spelling), None)
        return product

    # ── Matching ─────────────────────────────────────────────────────────────

    def match(self, spelling: str, code: str | None = None) -> Match:
        key = normalise_for_matching(spelling)
        code = code.strip() if code and code.strip() else None

        if LOST_CHARACTER in spelling:
            if spelling in self.spellings:
                return self._matched(self.spellings[spelling], Rung.EXACT, spelling, code)
            return self._held(spelling, key, code, lost=True)

        if spelling in self.spellings:
            return self._matched(self.spellings[spelling], Rung.EXACT, spelling, code)
        if key in self.keys:
            return self._matched(self.keys[key], Rung.NORMALISED, spelling, code)

        if (code is not None and code in self.code_owner) or key in self.pending:
            return self._held(spelling, key, code, lost=False)

        product = self._create(spelling, code)
        return Match(product, Rung.NEW, ErrorCode.PRODUCT_NEW, {"name": spelling, "product": product})

    # ── Internals ────────────────────────────────────────────────────────────

    def _matched(self, product: int, rung: Rung, spelling: str, code: str | None) -> Match:
        owner = self.code_owner.get(code) if code else None
        if owner is not None and owner != product and code not in self.products[product].codes:
            return Match(
                None,
                None,
                ErrorCode.PRODUCT_NAME_CONFLICT,
                {
                    "name": spelling,
                    "product_code": code,
                    "candidates": self._describe({product, owner}),
                    "by_name": product,
                    "by_code": owner,
                },
            )
        if code is not None and owner is None:
            self.code_owner[code] = product
            self.products[product].codes.add(code)
        return Match(product, rung)

    def _held(self, spelling: str, key: str, code: str | None, *, lost: bool) -> Match:
        candidates: set[int] = set()
        if code is not None and code in self.code_owner:
            candidates.add(self.code_owner[code])
        if not lost:
            candidates |= self.pending.get(key, set())
            self.pending[key] = set(candidates)
        context: dict[str, Any] = {"name": spelling, "candidates": self._describe(candidates)}
        if code is not None:
            context["product_code"] = code
        if lost:
            context["lost_characters"] = True
        return Match(None, None, ErrorCode.PRODUCT_MATCH_UNCONFIRMED, context)

    def _create(self, spelling: str, code: str | None) -> int:
        product = len(self.products) + 1
        self.products[product] = Product(product, spelling, {code} if code else set())
        self.spellings[spelling] = product
        self.keys[normalise_for_matching(spelling)] = product
        if code is not None and code not in self.code_owner:
            self.code_owner[code] = product
        return product

    def _describe(self, products: set[int]) -> list[dict[str, Any]]:
        return [{"product": p, "name": self.products[p].name} for p in sorted(products)]
