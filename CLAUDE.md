# CLAUDE.md — Mirsad

Rules for anyone, human or model, writing code in this repository.

---

## What this project is

Nakheel Retail has eleven shops. Every Sunday, eleven till exports arrive and disagree with each other: different headers, three date formats, Arabic-Indic digits, the same product written four ways, duplicate transaction ids. The owner nearly closed a branch last quarter because of a broken file.

She asked for one thing above all others:

> *"I would much rather read 'we could not match these fourteen rows' than look at a beautiful chart built on data nobody checked."*

**That is the product.** The dashboard is the easy part. We are building a system that is honest about its own gaps.

Every decision gets measured against one question: **does this make the uncertainty visible, or does it bury it under an average?**

---

## The gate

Every piece of application code belongs to a task ID in `docs/PROJECT-PLAN.md` §7. If you are asked to implement something that has no task ID, stop and say so.

The original gate — no code until `docs/SPEC.md` is approved — **was waived by the reviewer on 9 November 2026** (`docs/DECISIONS.md` D-001). There is no `SPEC.md`. Scope is the task list, the client's words, and the decisions log, read together.

Read before you build:

| Document | What it settles |
|---|---|
| `docs/DECISIONS.md` | Every decision taken since the client thread closed. **Where it disagrees with anything below, it wins** |
| `docs/decisions/ADR-0001-technology-stack.md` | Stack, and the layering in §6 |
| `docs/discovery/ANSWERS.md` | The client's own words. Wins over everything except `DECISIONS.md` |
| `docs/discovery/RANIA-MEETING.md` | What the weekly user needs, and what is wrong with each branch's file |
| `docs/discovery/IMPACT.md` | What those answers changed, including where our earlier defaults were wrong |
| `docs/PROJECT-PLAN.md` | Sprints, task IDs, Definition of Done. Its dates are superseded by `DECISIONS.md` D-002 |

The client is in **Palestine** and trades in **shekels (ILS)**, locales `ar-PS` and `en-PS`, timezone **Asia/Hebron**. The trading week runs **Saturday to Thursday; Friday is closed everywhere**.

We have had this wrong twice: we assumed Saudi riyals, the client corrected us to dirhams, and she later corrected herself to shekels. **The second error was found by asking about branch names, not about currency** — asking the same question again would have produced the same wrong answer. Currency, locale, timezone and week start all live in configuration, never in a literal.

---

## The eleven non-negotiables

These are the client's terms, not house style. A PR that breaks one does not get merged.

**1 — No literal UI strings.** Every user-visible string goes through `t()`, with keys added to `ar.json` **and** `en.json` **in the same commit**. A key in one locale and not the other is a broken build, not a to-do.

**2 — CSS logical properties only.** `margin-inline-start`, never `margin-left`. `padding-inline-end`, never `padding-right`. The layout must mirror completely when direction changes — a single physical property is a bug that only shows up in Arabic.

**3 — `dir` follows the locale**, set on the document root, never per-component.

**4 — Numbers, currency and dates go through `Intl`.** This product is almost entirely numbers; a raw `toFixed()` or `toLocaleString()` without an explicit locale is immediately visible to the client. Never hand-format a number.

**5 — All Arabic matching goes through `domain/arabic`.** One module, one entry point. It normalises alef forms, hamza forms, taa marbuta, alef maksura, tatweel and diacritics — and **keeps the original string**. Never write an ad-hoc Arabic regex anywhere else in the codebase. If the module is missing a rule, add it there with a test and a documented reason.

**6 — The server returns error codes, never prose.** An API error carries a code from the catalogue in `errors/`, and every code has a translation in both locales. No English sentence ever reaches the client from the backend.

**7 — Nothing is thrown away.** A row that cannot be used is recorded with a reason and stays viewable. The original raw row is kept on every transaction, so that when the owner asks why a number looks wrong, we can show her the line it came from. Deleting a bad row is the one thing this system must never do.

**8 — Never merge below the confidence threshold.** When the system is not sure two things are the same, it asks. It does not guess and move on. The threshold lives in configuration and is published in the UI.

**9 — Tests with every task.** No PR without tests.

**10 — Branch `task/<ID>-<slug>`, then a PR.** Never commit to `main`, never force-push, never merge without review.

**11 — The repo is public.** No secrets, no `.env` files, no real client data. Seed data is synthetic and realistic: real-looking Arabic product and branch names, never `test1` or lorem ipsum.

---

## Backend layering

FastAPI imposes no structure, so we impose it. The ingestion pipeline must be testable without HTTP and without a browser.

```
backend/app/
  api/          HTTP only — routing, auth, serialisation. No business logic.
  domain/       pure logic, no I/O:
                  arabic/      the single normalisation entry point (NN-5)
                  numbers/     Arabic-Indic digits, separators, currency text
                  dates/       format inference + ambiguity detection
                  matching/    scorers, thresholds, decisions
  pipeline/     orchestration: read → normalise → validate → match → persist
  repositories/ all SQLAlchemy access
  models/       SQLAlchemy models + Pydantic schemas
  errors/       the error-code enum — the only source of API error strings
```

**`domain/` imports nothing from `api/` or `repositories/`.** It takes values and returns values. This is what makes golden-file testing possible, and golden-file tests are how we know the data quality report has not silently changed.

---

## Three outcomes for a bad row, not two

The difference matters more than it looks, and it is the honesty requirement made concrete:

| Outcome | Meaning | In the dashboard |
|---|---|---|
| **warning** | Usable, but something is off | Included, flagged |
| **held** | Needs a human decision before it can be trusted | **Excluded, and counted out loud** |
| **rejected** | Cannot be used at all | Excluded, listed with its reason |

An ambiguous date is **held**, never guessed. A product match below threshold is **held**, never merged. "Held" rows are visible in the report with what we need from a human in order to proceed.

**And a second axis: scope.** Severity says what happened to a row; scope says which figures may use it. A row with a date, a branch and an amount but no product belongs in that branch's total and not in the product breakdown — so it is a `warning` with scope `{total}`, not a rejection. Rejecting it would under-report branch totals with no visible symptom, which is the original failure this project exists to prevent.

Every figure therefore states its own completeness: *"this branch's total includes 34 rows with no product, worth ILS 2,100."* Traceability says where a number came from; completeness says what is missing from it.

Collapsing `held` into `rejected` would quietly discard recoverable data. Collapsing it into `warning` would put unverified numbers on the dashboard. Keep all three.

---

## Working method

### Tasks
One task, one branch, one PR, one review.

```
task/M-004-arabic-normalisation
feat(M-004): normalise alef and hamza forms
```

Locale keys ship in the same commit as the string that uses them.

### Before opening a PR
Run the Definition of Done checklist in `docs/PROJECT-PLAN.md` §8. Check the screens in **both** `ar` and `en` and confirm the layout mirrors.

### Conventions beyond this file
Load the **`mirsad-conventions`** skill before touching Arabic text handling, error codes, rejection reasons, or any user-facing string. It holds the normalisation rule table, the error-code catalogue and the i18n checklist — the detail that is too long to live here.

### When something is unclear
The client thread is closed, so there is no one to ask. **Decide, write the decision and the reason in `docs/DECISIONS.md`, and keep building.** Do not stop and wait.

What is still forbidden is an assumption nobody can see. This project exists because someone built reports on data nobody checked; a guess buried in a function is the same failure in a different place. A decision in the log can be found, questioned and reversed in an hour. A guess in the code cannot.

The software works the same way at runtime: when *it* cannot decide — an ambiguous date, a weak product match — it holds the row and says so. It does not decide on the user's behalf.
