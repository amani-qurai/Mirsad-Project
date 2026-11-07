---
name: mirsad-conventions
description: The Mirsad repository's binding conventions for Arabic text normalisation and matching, bilingual AR/EN interface work with full RTL mirroring, API error codes, and the rejection/held/warning reason codes behind the data quality report. Load this before writing or reviewing any code that touches Arabic strings, product or branch name matching, a user-visible string, an `Intl` format call, a CSS spacing or alignment property, an API error response, or a row that is being rejected or flagged during ingestion — and also when adding a new reason code, a new error code, or a new locale key. Use it even when the task looks like a small fix, because these are the eleven client non-negotiables made concrete, and the usual way they break is one physical CSS property or one untranslated string slipping into an otherwise fine change.
---

# Mirsad conventions

Nakheel Retail's owner nearly closed a profitable branch because a broken file made its sales look like they had collapsed. The conventions here exist so that the system never again presents an unverified number as a fact.

Two ideas govern everything below:

1. **Normalise for comparison, never for storage.** Every transformation exists so two strings can be compared. The original is what a human will read when they ask "why does this number look wrong" — so it is always kept.
2. **Uncertainty is output, not an edge case.** When the system cannot resolve something, saying so clearly *is* the deliverable. Burying it in an average is the failure mode we were hired to fix.

## Reference files

| Read this | When |
|---|---|
| `references/arabic-normalisation.md` | Any Arabic text handling, matching, or a change to `domain/arabic` |
| `references/error-codes.md` | Any API error, or a new rejection / held / warning reason code |
| `references/i18n-rtl.md` | Any user-visible string, `Intl` call, CSS spacing or alignment, or chart work |

---

## Arabic text: one module, originals kept

All Arabic normalisation goes through `domain/arabic`. One module, one entry point.

```python
from app.domain.arabic import normalise_for_matching

key = normalise_for_matching(raw_name)   # for comparison only
# raw_name is persisted unchanged, always
```

**Why one module:** these rules are lossy on purpose. `ة → ه` merges "مكتبة" (library) and "مكتبه" (his desk); `ى → ي` merges "على" (on) and "علي" (Ali). Those trade-offs are acceptable for retail product names and unacceptable elsewhere, which is only safe if every call site uses the same reviewed rule set. An ad-hoc regex somewhere else in the codebase is how two genuinely different products quietly become one.

**Why the original is kept:** the owner's trust depends on being able to see the line a number came from. A normalised string is not that line.

If a rule is missing, add it to `domain/arabic` with a test and a one-line reason. Never patch around it at the call site.

The full rule table, with codepoints, ordering and the reason for each rule, is in `references/arabic-normalisation.md`.

---

## Matching: explain, then decide

The matching ladder, in order. Stop at the first rung that resolves.

| Rung | Rule | Outcome |
|---|---|---|
| 1 | Exact string match | matched |
| 2 | Match after normalisation | matched |
| 3 | Fuzzy score **≥ auto threshold** | matched, with the score recorded |
| 4 | Fuzzy score **≥ review floor** | **held** — a human is asked |
| 5 | Below review floor | treated as a new canonical product |

Thresholds live in configuration, never as literals in code, because they will be re-tuned once the client's real files arrive — and because the UI has to display the threshold it is actually using.

Three properties every match must have:

- **A recorded score.** "The system decided" is not an answer we can give the client. The number that drove the decision is stored on the match.
- **Reversibility.** Any match, automatic or human, can be undone, and the reversal is logged with who and when.
- **No silent merging below threshold** (non-negotiable 8). Rung 4 produces a question, never a quiet decision.

Rung 5 is deliberate: an unmatched product becomes a *new* product rather than being forced into the nearest existing one. A fake new product is visible and fixable; a wrong merge is invisible and corrupts a branch's history.

---

## Rejection, held, warning

Three outcomes, and the middle one is the point of the project.

| Outcome | Meaning | Dashboard | Example |
|---|---|---|---|
| **warning** | Usable, something is off | Included, flagged | Quantity missing but amount present |
| **held** | Needs a human decision first | **Excluded and counted out loud** | Ambiguous date; match below threshold; unknown branch name |
| **rejected** | Cannot be used at all | Excluded, listed with reason | No amount; unparseable date; exact duplicate file |

Every one of the three carries a code from `references/error-codes.md`, and **every code appears in the data quality report with a count and the affected rows**. A code that cannot be traced back to rows is not finished.

**Never collapse `held` into the others.** Into `rejected`, and we discard recoverable data the client could have fixed in ten seconds. Into `warning`, and unverified numbers reach the dashboard — the exact failure that cost her a quarter.

Nothing is ever deleted (non-negotiable 7). A rejected row keeps its raw form and stays viewable.

---

## User-facing text and layout

The short version; the full checklist is in `references/i18n-rtl.md`.

- Every string goes through `t()`, with the key in **both** `ar.json` and `en.json` **in the same commit**. Not the next commit.
- Numbers, currency and dates go through `Intl` with an explicit locale. Never `toFixed()`, never a bare `toLocaleString()`, never hand-built thousands separators.
- CSS logical properties only: `margin-inline-start`, `padding-inline-end`, `inset-inline-start`, `text-align: start`. A single `margin-left` is a bug that only appears in Arabic, which means it reaches the client before it reaches you.
- `dir` and `lang` are set on the document root from the locale, never per component.
- Charts go through the shared `<Chart>` wrapper. Direction-dependent options — axis inversion, label alignment, legend placement, tooltip side — belong in that wrapper, not in each chart. The client tests language switching, and no charting library mirrors itself.

**Why this is strict:** the product is almost entirely numbers in two directions. A missing translation or an unmirrored margin is not cosmetic here — it is the first thing visible on the screen the client opens.

---

## API errors

The server returns codes, never prose (non-negotiable 6).

```python
raise MirsadError(ErrorCode.ROW_DATE_AMBIGUOUS, context={"row": 412, "value": "03/04/2025"})
```

- The code comes from the enum in `errors/` — the single source of truth.
- Both `ar.json` and `en.json` carry a message for it, added in the same commit as the code.
- `context` holds structured values for the message to interpolate. It never holds a pre-built sentence.
- A new code without both translations fails CI, by design.

**Why:** an English sentence from the backend cannot be shown to an Arabic-speaking accountant, and a sentence assembled in the API cannot be corrected by a translator. Codes also make the data quality report groupable and countable, which is what makes "we could not match these fourteen rows" possible to write at all.

---

## Writing tests here

Golden-file tests on the messy fixtures are the real safety net: feed the deliberately broken files in, assert the exact data quality report that comes out — row counts, reason codes, flagged dates, duplicate ids, match scores.

This matters more than unit-test coverage, because the failure we are guarding against is not a crash. It is the report quietly changing shape — a reason code disappearing, a held row becoming a warning, fourteen unmatched rows becoming thirteen with no one noticing. A golden file turns that into a failing build.

`domain/` is pure, so its tests need no database and no HTTP. Keep it that way; it is what makes these tests fast enough to run on every commit.
