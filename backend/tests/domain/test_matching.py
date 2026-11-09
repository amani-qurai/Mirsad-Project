"""M-013 (block one) — exact and confirmed spellings only; everything else asks or is new."""

from __future__ import annotations

from app.domain.matching import Catalogue, Rung
from app.errors import ErrorCode

E = ErrorCode


def test_first_sighting_becomes_a_new_product() -> None:
    cat = Catalogue()
    m = cat.match("Bathmat", "0004")
    assert (m.rung, m.code) == (Rung.NEW, E.PRODUCT_NEW)
    assert cat.products[m.product].name == "Bathmat"
    assert cat.code_owner["0004"] == m.product


def test_same_spelling_matches_exactly() -> None:
    cat = Catalogue()
    first = cat.match("Bathmat", "0004")
    again = cat.match("Bathmat", "0004")
    assert (again.product, again.rung, again.code) == (first.product, Rung.EXACT, None)


def test_same_key_matches_after_normalisation() -> None:
    cat = Catalogue()
    first = cat.match("ساعة حائط 30", "0011")
    m = cat.match("ساعه حائط ٣٠", "0011")
    assert (m.product, m.rung, m.code) == (first.product, Rung.NORMALISED, None)


def test_unknown_spelling_with_a_known_code_is_a_question_not_a_merge() -> None:
    """The code suggests; it never decides (product code eras, M-012)."""
    cat = Catalogue()
    bathmat = cat.match("Bathmat", "0004").product
    m = cat.match("بساط حمام", "0004")
    assert m.product is None
    assert m.code is E.PRODUCT_MATCH_UNCONFIRMED
    assert m.context["candidates"] == [{"product": bathmat, "name": "Bathmat"}]
    assert len(cat.products) == 1  # no product invented


def test_one_answer_resolves_every_row_with_that_spelling() -> None:
    cat = Catalogue()
    bathmat = cat.match("Bathmat", "0004").product
    cat.match("بساط حمام", "0004")
    cat.confirm("بساط حمام", bathmat)
    assert cat.match("بساط حمام", "0004").product == bathmat
    assert cat.match("بساط  حمام", "0004").rung is Rung.NORMALISED  # and its key
    assert cat.pending == {}


def test_a_spelling_waiting_for_a_person_holds_rows_without_a_code_too() -> None:
    """Tulkarem has no codes. It must join the same question, not invent a product."""
    cat = Catalogue()
    bathmat = cat.match("Bathmat", "0004").product
    cat.match("سجادة حمام", "0004")
    m = cat.match("سجادة حمام", None)
    assert m.code is E.PRODUCT_MATCH_UNCONFIRMED
    assert m.context["candidates"] == [{"product": bathmat, "name": "Bathmat"}]
    assert len(cat.products) == 1


def test_lost_characters_never_match_by_key_and_never_create() -> None:
    """Jenin: 'ساعه حائط ??' must not become 'ساعه حائط' of any size (D-011)."""
    cat = Catalogue()
    clock = cat.match("ساعة حائط", "0099").product  # a hypothetical size-less clock
    m = cat.match("ساعه حائط ??", "0011")
    assert m.product is None and m.code is E.PRODUCT_MATCH_UNCONFIRMED
    assert m.context["lost_characters"] is True
    assert m.context["candidates"] == []  # 0011 unknown; and the key of a size-less clock is not evidence
    assert clock in cat.products and len(cat.products) == 1


def test_lost_characters_match_once_a_person_confirms_the_exact_spelling() -> None:
    cat = Catalogue()
    clock = cat.match("Wall clock 30", "0011").product
    assert cat.match("ساعه حائط ??", "0011").context["candidates"][0]["product"] == clock
    cat.confirm("ساعه حائط ??", clock)
    assert cat.match("ساعه حائط ??", "0011").product == clock
    # Confirming a damaged spelling does not teach its damaged key.
    assert "ساعه حايط" not in cat.keys


def test_name_and_code_pointing_at_different_products_is_a_conflict() -> None:
    cat = Catalogue()
    mat = cat.match("Bathmat", "0004").product
    lamp = cat.match("Table Lamp", "0012").product
    m = cat.match("Bathmat", "0012")
    assert m.code is E.PRODUCT_NAME_CONFLICT
    assert (m.context["by_name"], m.context["by_code"]) == (mat, lamp)
    assert m.product is None


def test_confirm_new_creates_on_a_persons_word() -> None:
    cat = Catalogue()
    cat.match("Bathmat", "0004")
    cat.match("Bath Towel", "0004")  # held: same code, unknown name
    towel = cat.confirm_new("Bath Towel", "0004")  # the code it arrived with
    assert cat.match("Bath Towel", "0004").product == towel
    assert cat.match("Bathmat", "0004").code is None  # 0004 still means Bathmat too
    assert cat.pending == {}


def test_confirming_a_conflict_accepts_that_pairing() -> None:
    cat = Catalogue()
    mat = cat.match("Bathmat", "0004").product
    cat.match("Table Lamp", "0012")
    assert cat.match("Bathmat", "0012").code is E.PRODUCT_NAME_CONFLICT
    cat.confirm("Bathmat", mat, "0012")
    assert cat.match("Bathmat", "0012").product == mat


def test_arabic_and_english_are_never_matched_by_the_machine() -> None:
    cat = Catalogue()
    cat.match("Spice Rack", "0019")
    assert cat.match("رف بهارات", None).code is E.PRODUCT_NEW  # no code, no candidate: new, visibly
