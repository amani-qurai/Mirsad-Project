# Arabic normalisation — the rule table

The authoritative specification for `backend/app/domain/arabic`. Every rule here has a reason, because a rule without a reason cannot be defended to the client or changed safely later.

**Contents**
- [The contract](#the-contract)
- [Rule order](#rule-order)
- [The rules](#the-rules)
- [Accepted collisions](#accepted-collisions)
- [What this module must not do](#what-this-module-must-not-do)
- [Test expectations](#test-expectations)

---

## The contract

```python
def normalise_for_matching(value: str) -> str:
    """Return a comparison key. The caller keeps the original."""
```

Two properties this function must have:

- **Idempotent.** `f(f(x)) == f(x)`. Ingestion may normalise a value more than once; the result must not drift.
- **Never persisted as the value.** The output is a comparison key. It may be stored *alongside* the original in a `*_normalised` column for indexing, never *instead of* it.

Non-negotiable 5 makes this the only entry point for Arabic matching anywhere in the codebase.

---

## Rule order

Order is part of the specification, not an implementation detail.

```
1. Unicode NFKC
2. Strip zero-width and bidi control characters
3. Strip diacritics (harakat)
4. Strip tatweel
5. Unify letter forms (alef, hamza-carriers, taa marbuta, alef maksura)
6. Convert Arabic-Indic digits to Western
7. Fold Latin case
   7a. A multiplication sign between digits becomes x          (added, D-017)
   7b. A decimal mark between digits is kept, unified to "."   (added, D-017)
8. Strip punctuation and symbols
   8a. Separate digits from letters with a space               (added, D-017)
9. Collapse and trim whitespace
```

**Why this order:** NFKC must run first because it decomposes presentation forms and ligatures into the base letters that rules 3–5 operate on — reversed, those rules would miss anything a till exported in a presentation form. Diacritic stripping precedes letter unification because some diacritics sit on the very characters being unified. Whitespace collapsing runs last because earlier rules remove characters and can leave double spaces behind.

---

## The rules

### 1. Unicode NFKC normalisation

| Input | Output |
|---|---|
| `ﻻ` (U+FEFB, lam-alef presentation form) | `لا` |
| `ﺍﻟﻤﻜﺘﺒﺔ` (presentation forms) | `المكتبة` |
| `１２３` (full-width) | `123` |

**Reason:** till systems and Excel exports frequently emit Arabic presentation forms (U+FB50–U+FEFF) rather than base letters. Visually identical, different codepoints, and they would never match. NFKC also flattens full-width Latin digits and ligatures in one pass.

### 2. Zero-width and bidi control characters — remove

| Codepoint | Name |
|---|---|
| U+200B | zero-width space |
| U+200C | zero-width non-joiner |
| U+200D | zero-width joiner |
| U+200E | left-to-right mark |
| U+200F | right-to-left mark |
| U+061C | Arabic letter mark |
| U+FEFF | byte-order mark / zero-width no-break space |
| U+2066–U+2069 | directional isolates |

**Reason:** these are invisible. Software inserts them to control display direction, and Excel leaves a BOM at the start of the first cell. They make two strings that look identical compare as different — the single most confusing class of mismatch to debug, because the difference cannot be seen in any report.

### 3. Diacritics (harakat) — remove

| Range | Contents |
|---|---|
| U+064B–U+065F | fathatan, dammatan, kasratan, fatha, damma, kasra, shadda, sukun, and the superscript marks |
| U+0670 | superscript alef |
| U+0610–U+061A | Quranic annotation signs |
| U+06D6–U+06ED | Quranic marks |

**Reason:** diacritics are optional in written Arabic. One branch manager types `مُكَعَّبات` and another types `مكعبات` for the same product. Keeping them guarantees a mismatch on a difference no Arabic reader considers meaningful.

### 4. Tatweel (kashida) U+0640 — remove

| Input | Output |
|---|---|
| `مكـــتبة` | `مكتبة` |

**Reason:** tatweel is a typographic stretch for justification. It carries no meaning and appears unpredictably in exported text.

### 5. Letter form unification

| From | To | Note |
|---|---|---|
| `أ` U+0623, `إ` U+0625, `آ` U+0622, `ٱ` U+0671 | `ا` U+0627 | alef forms |
| `ؤ` U+0624 | `و` U+0648 | waw with hamza |
| `ئ` U+0626 | `ي` U+064A | yeh with hamza |
| `ء` U+0621 | *removed* | standalone hamza |
| `ة` U+0629 | `ه` U+0647 | taa marbuta |
| `ى` U+0649 | `ي` U+064A | alef maksura |

**Reason — alef and hamza forms:** hamza placement is the most common Arabic typing inconsistency. `أكواب` and `اكواب` are the same word to every reader, and the hamza is routinely omitted on informal keyboards and by till software.

**Reason — taa marbuta and alef maksura:** both are word-final letters routinely substituted for their look-alikes (`ة`/`ه`, `ى`/`ي`). This is the second most common inconsistency after hamza, and these two rules are what make `مكتبة` and `مكتبه` match.

**Note on scope:** the project brief names alef forms, hamza forms, taa marbuta, tatweel and diacritics. **Alef maksura is added here deliberately** — it is the same class of problem and omitting it would leave a large category of real mismatches unresolved. It is recorded as an addition so the decision is reviewable rather than assumed.

### 6. Arabic-Indic digits → Western

| From | To |
|---|---|
| `٠١٢٣٤٥٦٧٨٩` U+0660–U+0669 | `0123456789` |
| `۰۱۲۳۴۵۶۷۸۹` U+06F0–U+06F9 | `0123456789` |

**Reason:** product names carry numbers — `طقم أكواب ٤ قطع` and `طقم اكواب 4 قطع` are one product. Note both ranges: U+0660 is Arabic-Indic, U+06F0 is Extended Arabic-Indic (Persian/Urdu), and till systems emit both.

Numeric *amounts* are a different problem and belong to `domain/numbers` — that module handles thousands separators, decimal marks and trailing currency text. This rule is only about digits embedded in names.

### 7. Latin case folding

`Mug Set` → `mug set`

**Reason:** branches write English names with inconsistent capitalisation. Product names here are mixed Arabic and English, so both scripts need their own folding and Arabic has no case.

### 8. Punctuation and symbols — remove

Includes Arabic punctuation (`،` U+060C, `؛` U+061B, `؟` U+061F) and Latin punctuation, hyphens and underscores.

| Input | Output |
|---|---|
| `Mug Set - 4pc` | `mug set 4 pc` |
| `طقم أكواب (٤ قطع)` | `طقم اكواب 4 قطع` |

**Reason:** punctuation in product names is decoration applied inconsistently per branch. `Mug Set - 4pc`, `Mug Set (4pc)` and `Mug Set, 4pc` are one product.

### 7a, 7b, 8a — added after the real files arrived (D-017)

| Rule | Input | Output | Reason |
|---|---|---|---|
| 7a `×` between digits → `x` | `سجاده ارضية ١٢٠×١٧٠` | `سجاده ارضيه 120 x 170` | Rule 8 would delete `×` but keep the letter `x`, so `120×170` and `120x170` — one rug, written both ways in the exports — would never match |
| 7b decimal mark between digits kept as `.` | `Glass Jug 1,5 L` · `غلايه كهربائية ١٫٧` | `glass jug 1.5 l` · `غلايه كهرباييه 1.7` | Rule 8 alone turns `1.5` into `15`: a 1.5 L jug and a 15 L box would share a key. `.`, `,` and `٫` all appear between digits in the real names. A thousands separator inside a product name would also become `.`; none exists in the data |
| 8a space between digits and letters | `Mug Set 6pc` · `FRYING PAN 28CM` | `mug set 6 pc` · `frying pan 28 cm` | Spacing around a unit is typed inconsistently (`6pc` / `6 PC`, `1.7L` / `1.7 L`) and carries no meaning |

The worked example under rule 8 therefore now reads `Mug Set - 4pc` → `mug set 4 pc`.

### 9. Whitespace — collapse and trim

Collapse any run of whitespace to a single space; trim both ends. Includes the non-breaking space U+00A0, which Excel produces often.

**Reason:** earlier rules remove characters and leave gaps behind. Also catches trailing spaces from cell padding, which are invisible and cause mismatches.

---

## Accepted collisions

These rules are lossy on purpose. The collisions are known and accepted **for retail product and branch names**, and must not be assumed safe elsewhere.

| Rule | Collides | Why accepted |
|---|---|---|
| `ة → ه` | `مكتبة` (library) / `مكتبه` (his desk) | Grammatical possessives do not appear in product names, and the inconsistency this fixes is far more common than the collision it creates |
| `ى → ي` | `على` (on) / `علي` (Ali) | Same reasoning; a collision would require two products differing only in a final yeh |
| `ء` removed | distinct words differing only by standalone hamza | Rare in product names; hamza is omitted inconsistently often enough that keeping it causes more misses than drops |
| punctuation removed | `4-pc` / `4 pc` | Intended — these are the same product |

**If a real collision appears in the client's data,** it is a finding to record and raise, not a reason to quietly weaken a rule. The resolve queue exists precisely so a human can separate two things the matcher merged.

---

## What this module must not do

- **Never return a value intended for storage or display.** It returns a comparison key.
- **Never translate or transliterate.** `mug set` and `طقم أكواب` are the same product to a human; this module will not and must not match them. That is a resolve-queue decision made by a person, recorded once, and replayed afterwards — never guessed.
- **Never do stemming or morphology.** Removing `ال` prefixes or pluralisation suffixes merges genuinely different products. Out of scope.
- **Never take a locale or configuration argument.** One behaviour, everywhere, so a stored comparison key stays valid.

---

## Test expectations

This is the most heavily tested file in the repository. Every rule above needs:

1. A case proving the rule applies.
2. A case proving the **original string is unchanged** after the call.
3. An idempotency case: `f(f(x)) == f(x)`.

Plus, across the module:

- A table-driven test with the real-world pairs the rules exist for — `أكواب`/`اكواب`, `مكتبة`/`مكتبه`, `مكـــتبة`/`مكتبة`, `طقم أكواب ٤ قطع`/`طقم اكواب 4 قطع`, a presentation-form string against its base form, and a BOM-prefixed string against its clean form.
- Each accepted collision asserted **explicitly as expected behaviour**, so that a future change which "fixes" one is caught and discussed rather than merged. A test that documents a deliberate trade-off is doing more work than a test that documents a success.
- Empty string, whitespace-only, Latin-only, and digits-only inputs.
