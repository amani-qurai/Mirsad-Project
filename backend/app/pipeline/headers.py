"""Header mapping: each branch's column names → one set of standard fields (M-008).

Eleven tills name the same column eleven ways — ``NET_AMOUNT``, ``Value``,
``AMOUNT_EXVAT``, ``المبلغ``. This module says which column is which, and
nothing else: it does not read a single cell value.

Rules (DECISIONS.md D-012):

- A header is compared after case-folding and collapsing spaces and
  underscores. No Arabic letter normalisation happens here — that is
  ``domain/arabic``'s job (NN-5), and exact header names have not needed it.
- **Every column must be recognised.** A column we have never seen is not
  ignored: a new column can change the meaning of the others (Jenin's
  separate discount is exactly that). The file is *held* until a person says
  what the column is, and the answer is remembered.
- ``DATE`` and ``AMOUNT`` are required. Without them no row can be placed in
  time or counted.
- The header can tell us the amount is pre-VAT (``AMOUNT_EXVAT``). That is
  recorded on the mapping so validation reports it; it is never silently
  multiplied away.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from app.errors import ErrorCode, MirsadError
from app.pipeline.readers import RawTable


class Field(StrEnum):
    TXN_ID = "txn_id"
    DATE = "date"
    PRODUCT_CODE = "product_code"
    PRODUCT_NAME = "product_name"
    QUANTITY = "quantity"
    AMOUNT = "amount"
    DISCOUNT = "discount"
    NOTES = "notes"


class AmountBasis(StrEnum):
    UNSTATED = "unstated"  # the file does not say; most branches
    EX_VAT = "ex_vat"      # the header says so — Qalqilya


REQUIRED: frozenset[Field] = frozenset({Field.DATE, Field.AMOUNT})


@dataclass(frozen=True)
class Alias:
    field: Field
    basis: AmountBasis | None = None


def header_key(header: str) -> str:
    """The comparison form of a header. Case, spacing and underscores only."""
    return re.sub(r"[\s_]+", " ", header).strip().casefold()


def _aliases(field: Field, *names: str, basis: AmountBasis | None = None) -> dict[str, Alias]:
    return {header_key(name): Alias(field, basis) for name in names}


# Every header seen in the six weeks of real exports, and nothing guessed
# beyond them. A new spelling is added here when a person has confirmed it.
KNOWN_HEADERS: dict[str, Alias] = {
    **_aliases(Field.TXN_ID, "TXN_ID", "TXN", "Txn", "Transaction", "Trans No", "رقم العملية"),
    **_aliases(Field.DATE, "TRX_DATE", "DATE", "Trans Date", "التاريخ"),
    **_aliases(Field.PRODUCT_CODE, "ITEM_NO", "CODE", "Item Code", "رمز الصنف"),
    **_aliases(
        Field.PRODUCT_NAME,
        "ITEM_NAME", "ITEM", "PRODUCT", "Description", "Item Description", "اسم الصنف", "الصنف",
    ),
    **_aliases(Field.QUANTITY, "QTY", "Quantity", "الكمية"),
    **_aliases(Field.AMOUNT, "NET_AMOUNT", "AMOUNT", "Value", "المبلغ"),
    **_aliases(Field.AMOUNT, "AMOUNT_EXVAT", basis=AmountBasis.EX_VAT),
    **_aliases(Field.DISCOUNT, "الخصم"),
    **_aliases(Field.NOTES, "NOTES", "NOTE", "Remarks", "ملاحظات"),
}


@dataclass(frozen=True)
class HeaderMapping:
    columns: Mapping[Field, int]  # standard field → column index in the raw table
    amount_basis: AmountBasis

    def has(self, field: Field) -> bool:
        return field in self.columns


def map_headers(table: RawTable, remembered: Mapping[str, Alias] | None = None) -> HeaderMapping:
    """Map a table's headers, or hold the file with everything a person needs to fix it.

    ``remembered`` holds answers a person has already given for this branch
    (header text → field). They take precedence over the built-in table, so a
    correction made once sticks.
    """
    known = {**KNOWN_HEADERS, **{header_key(k): v for k, v in (remembered or {}).items()}}

    columns: dict[Field, int] = {}
    unrecognised: list[str] = []
    duplicated: dict[str, list[str]] = {}
    basis = AmountBasis.UNSTATED

    for index, header in enumerate(table.header):
        alias = known.get(header_key(header))
        if alias is None:
            unrecognised.append(header)
            continue
        if alias.field in columns:
            first = table.header[columns[alias.field]]
            duplicated.setdefault(alias.field.value, [first]).append(header)
            continue
        columns[alias.field] = index
        if alias.basis is not None:
            basis = alias.basis

    missing = sorted(field.value for field in REQUIRED - columns.keys())
    if unrecognised or duplicated or missing:
        raise MirsadError(
            ErrorCode.FILE_HEADERS_UNRECOGNISED,
            {
                "file": table.source.name,
                "unrecognised": unrecognised,
                "duplicated": duplicated,
                "missing": missing,
                "headers": list(table.header),
            },
        )
    return HeaderMapping(columns=columns, amount_basis=basis)
