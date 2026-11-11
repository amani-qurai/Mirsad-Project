"""Numbers as the tills write them (M-005). Pure: values in, values out.

This first part handles digits only. Separators (``٫`` decimal, ``٬``
thousands) and trailing currency text come with amount parsing.
"""

from __future__ import annotations

# Arabic-Indic (U+0660–0669) — Hebron writes about half its dates with these.
# Extended Arabic-Indic (U+06F0–06F9) — the Persian/Urdu forms; no till uses
# them today, but a keyboard layout can produce them and they mean the same.
_DIGITS = str.maketrans(
    "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹",
    "01234567890123456789",
)


def to_ascii_digits(text: str) -> str:
    """Replace Arabic-Indic digits with 0–9. Every other character is untouched.

    For comparison and parsing only — the original string is what is stored
    and shown (NN-7).
    """
    return text.translate(_DIGITS)


def has_arabic_indic_digits(text: str) -> bool:
    return text != to_ascii_digits(text)
