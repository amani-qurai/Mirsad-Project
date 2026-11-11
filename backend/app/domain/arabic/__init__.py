"""The single entry point for Arabic (and mixed-script) name matching — NN-5 (M-004).

    key = normalise_for_matching(raw_name)   # for comparison only
    # raw_name is stored and shown unchanged, always

The rules, their order and the reason for each are specified in
``.claude/skills/mirsad-conventions/references/arabic-normalisation.md``.
Three rules were added after the real files arrived (DECISIONS.md D-017);
they are marked below.

The output is a comparison key. It is never stored *instead of* the original,
never shown, and never translated: ``Bathmat`` and ``بساط حمام`` stay
different here, and only a person can say they are the same product.
"""

from __future__ import annotations

import re
import unicodedata

from app.domain.numbers import to_ascii_digits

# 2. Invisible characters that make identical-looking strings differ.
_INVISIBLE = dict.fromkeys(
    [0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0x061C, 0xFEFF, 0x2066, 0x2067, 0x2068, 0x2069]
)

# 3. Diacritics (harakat), superscript alef, Quranic marks.
_DIACRITICS = re.compile("[ؐ-ًؚ-ٰٟۖ-ۭ]")

# 4. Tatweel.
_TATWEEL = "ـ"

# 5. Letter forms.
_LETTERS = str.maketrans(
    {
        "أ": "ا",  # أ → ا
        "إ": "ا",  # إ → ا
        "آ": "ا",  # آ → ا
        "ٱ": "ا",  # ٱ → ا
        "ؤ": "و",  # ؤ → و
        "ئ": "ي",  # ئ → ي
        "ء": None,      # ء removed
        "ة": "ه",  # ة → ه
        "ى": "ي",  # ى → ي
    }
)

# Added (D-017a): a decimal mark between digits is part of the number.
# Without this, 1.5 and 15 become the same key — a 1.5 L jug and a 15 L box.
# "." "," and the Arabic decimal separator ٫ all appear in the real names.
_DECIMAL = re.compile(r"(?<=\d)[.,٫](?=\d)")
_DECIMAL_MARK = ""  # private-use placeholder, survives the punctuation pass

# Added (D-017b): a multiplication sign between digits is a dimension, as in
# 120×170. It becomes the letter x, which is how the other branches write it.
_TIMES = re.compile(r"(?<=\d)\s*[×✕✖]\s*(?=\d)")

# Added (D-017c): a space wherever digits meet letters, so 6pc = 6 pc,
# 1.7L = 1.7 L and 120x170 = 120 x 170. Spacing around a unit is typed
# inconsistently and carries no meaning.
_DIGIT_LETTER = re.compile(r"(?<=\d)(?=[^\W\d_])|(?<=[^\W\d_])(?=\d)")

_SPACE = re.compile(r"\s+")


def _strip_punctuation(text: str) -> str:
    return "".join(
        " " if unicodedata.category(ch)[0] in "PS" else ch
        for ch in text
    )


def normalise_for_matching(value: str) -> str:
    """Return a comparison key. The caller keeps the original.

    Idempotent: ``normalise_for_matching(k) == k`` for any key ``k`` it returns.
    Takes no locale or option: one behaviour everywhere, so a stored key stays valid.
    """
    s = unicodedata.normalize("NFKC", value)            # 1
    s = s.translate(_INVISIBLE)                          # 2
    s = _DIACRITICS.sub("", s)                           # 3
    s = s.replace(_TATWEEL, "")                          # 4
    s = s.translate(_LETTERS)                            # 5
    s = to_ascii_digits(s)                               # 6
    s = s.casefold()                                     # 7
    s = _TIMES.sub("x", s)                               # added b
    s = _DECIMAL.sub(_DECIMAL_MARK, s)                   # added a
    s = _strip_punctuation(s)                            # 8
    s = s.replace(_DECIMAL_MARK, ".")
    s = _DIGIT_LETTER.sub(" ", s)                        # added c
    return _SPACE.sub(" ", s).strip()                    # 9
