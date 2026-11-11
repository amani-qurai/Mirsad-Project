"""M-004 — domain/arabic. Every rule: applies, keeps the original, is idempotent."""

from __future__ import annotations

import pytest

from app.domain.arabic import normalise_for_matching as norm

# (rule, input, expected key)
RULES = [
    ("1 NFKC presentation form", "ﻻ", "لا"),
    ("1 NFKC presentation forms", "ﺍﻟﻤﻜﺘﺒﺔ", "المكتبه"),
    ("1 NFKC full-width digits", "１２３", "123"),
    ("2 zero-width space", "ترمس​", "ترمس"),
    ("2 RTL mark", "‏ترمس", "ترمس"),
    ("2 BOM", "﻿طقم ترمس", "طقم ترمس"),
    ("2 Arabic letter mark", "سله؜غسيل", "سلهغسيل"),
    ("3 diacritics", "مُكَعَّبات", "مكعبات"),
    ("3 superscript alef", "هٰذا", "هذا"),
    ("4 tatweel", "مكـــتبة", "مكتبه"),
    ("5 alef hamza above", "أكواب", "اكواب"),
    ("5 alef hamza below", "إبريق", "ابريق"),
    ("5 alef madda", "آلة", "اله"),
    ("5 waw hamza", "مؤقت", "موقت"),
    ("5 yeh hamza", "بئر", "بير"),
    ("5 standalone hamza removed", "ماء", "ما"),
    ("5 taa marbuta", "ساعة", "ساعه"),
    ("5 alef maksura", "مستوى", "مستوي"),
    ("6 Arabic-Indic digits", "ساعه حائط ٣٠", "ساعه حايط 30"),
    ("6 extended digits", "شماعات ۱۰", "شماعات 10"),
    ("7 Latin case", "MUG SET", "mug set"),
    ("8 Latin punctuation", "Cutlery set (24)", "cutlery set 24"),
    ("8 Arabic punctuation", "سلة، غسيل؟", "سله غسيل"),
    ("8 hyphen", "Bedsheet set - double", "bedsheet set double"),
    ("9 whitespace and NBSP", "  Table   Lamp ", "table lamp"),
    ("added a: decimal point kept", "Glass Jug 1.5L", "glass jug 1.5 l"),
    ("added a: decimal comma unified", "Glass Jug 1,5 L", "glass jug 1.5 l"),
    ("added a: Arabic decimal separator", "غلايه كهربائية ١٫٧", "غلايه كهرباييه 1.7"),
    ("added b: multiplication sign", "سجاده ارضية ١٢٠×١٧٠", "سجاده ارضيه 120 x 170"),
    ("added c: digits meet letters", "Mug Set 6pc", "mug set 6 pc"),
]


@pytest.mark.parametrize(("rule", "raw", "expected"), RULES, ids=[r[0] for r in RULES])
def test_rule_applies(rule: str, raw: str, expected: str) -> None:
    assert norm(raw) == expected


@pytest.mark.parametrize(("rule", "raw", "expected"), RULES, ids=[r[0] for r in RULES])
def test_original_is_unchanged(rule: str, raw: str, expected: str) -> None:
    before = str(raw)
    norm(raw)
    assert raw == before


@pytest.mark.parametrize(("rule", "raw", "expected"), RULES, ids=[r[0] for r in RULES])
def test_idempotent(rule: str, raw: str, expected: str) -> None:
    assert norm(norm(raw)) == norm(raw)


# ── The pairs the rules exist for, including the real files' own ─────────────

SAME = [
    ("أكواب", "اكواب"),
    ("مكتبة", "مكتبه"),
    ("مكـــتبة", "مكتبة"),
    ("طقم أكواب ٤ قطع", "طقم اكواب 4 قطع"),
    ("﻿طقم ترمس", "طقم ترمس"),
    ("ﺍﻟﻤﻜﺘﺒﺔ", "المكتبة"),
    # From the six weeks of exports:
    ("إبريق زجاج 1.5", "ابريق زجاج ١.٥"),
    ("غلاية كهربائية 1.7", "غلايه كهربائية ١.٧"),
    ("ساعة حائط 30", "ساعه حائط ٣٠"),
    ("سلة غسيل", "سله غسيل"),
    ("ستاره حمام", "ستارة حمام"),
    ("صينيه تقديم", "صينية تقديم"),
    ("Glass Jug 1.5L", "Glass Jug 1,5 L"),
    ("MUG SET 6 PC", "Mug Set 6pc"),
    ("Floor Rug 120x170", "Floor Rug 120 x 170"),
    ("سجادة 120x170", "سجادة ١٢٠×١٧٠"),
    ("Laundry basket", "Laundry Basket"),
]


@pytest.mark.parametrize(("a", "b"), SAME)
def test_real_world_pairs_match(a: str, b: str) -> None:
    assert norm(a) == norm(b)


DIFFERENT = [
    # Never translated (the rule table: "must not").
    ("Bathmat", "بساط حمام"),
    ("Mug Set 6pc", "طقم مجات 6"),
    # Never stemmed: plural and definite article stay.
    ("Mug Set 6pcs", "Mug Set 6pc"),
    ("كرسي بلاستيك", "كرسي بلاستيكي"),
    # D-017a: the decimal point is part of the number.
    ("Glass Jug 1.5", "Glass Jug 15"),
    # Different words that happen to share letters.
    ("طقم ترمس", "طقم ترامس"),
]


@pytest.mark.parametrize(("a", "b"), DIFFERENT)
def test_these_stay_different(a: str, b: str) -> None:
    assert norm(a) != norm(b)


# ── Accepted collisions: asserted as intended behaviour ─────────────────────


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("مكتبة", "مكتبه"),  # library / his desk — taa marbuta
        ("على", "علي"),      # on / Ali — alef maksura
        ("4-pc", "4 pc"),    # punctuation
    ],
)
def test_accepted_collisions(a: str, b: str) -> None:
    """Deliberate trade-offs. A change that 'fixes' one must be discussed, not merged."""
    assert norm(a) == norm(b)


def test_lost_characters_disappear_from_the_key() -> None:
    """Jenin's '?' placeholders are punctuation here. The matcher, not this
    module, must stop such keys merging with a real name (D-011)."""
    assert norm("ساعه حائط ??") == "ساعه حايط"


@pytest.mark.parametrize("raw", ["", "   ", "​"])
def test_empty_inputs(raw: str) -> None:
    assert norm(raw) == ""


def test_latin_only_and_digits_only() -> None:
    assert norm("Spice Rack") == "spice rack"
    assert norm("٢٠٢٦") == "2026"
