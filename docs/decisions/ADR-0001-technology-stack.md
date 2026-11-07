# ADR-0001 — Technology Stack

| | |
|---|---|
| **Status** | Proposed — awaiting reviewer approval |
| **Date** | 2026-11-07 |
| **Owner** | Amani |
| **Reviewer** | Imam |
| **Supersedes** | — |

---

## 1. Why this document exists

The client sent one email. No specification, no feature list. Before anything is built we have to turn that email into **technical forces** — the properties the system must have regardless of who writes it — and only then pick tools.

This ADR does that in three moves:

1. Extract the forces from the client's own words.
2. For each layer of the system, state the options, the benefits, the costs, and the verdict.
3. Trace every verdict back to a force, so no choice is justified by taste.

If a choice below cannot be traced to a line in the client's email or the project non-negotiables, it is the wrong choice and should be challenged in review.

---

## 2. The forces, extracted from the client's request

Quotations are Suha Qasem's own words. "NN-*n*" refers to the numbered non-negotiables in `mirsad-amani-start.md`. "AC-*n*" refers to the delivery acceptance criteria.

| # | Force | Where it comes from |
|---|---|---|
| **F1** | Read heterogeneous till exports — different headers, encodings, column orders, file formats | *"Every Sunday each branch manager sends me a sales file from the till system"* / *"The files do not agree with each other"* |
| **F2** | Decide that two differently-written product names are the same product, with a published confidence threshold, and **ask instead of guessing** below it | *"The same product appears three or four different ways"* / NN-8 / AC-3 |
| **F3** | Normalise Arabic text centrally — alef, hamza, taa marbuta, tatweel, diacritics — and keep the original string | *"One branch writes the product names in Arabic, another in English, one writes them in both"* / NN-5 |
| **F4** | Parse Arabic-Indic digits, thousands separators, trailing currency text | AC-7 |
| **F5** | Detect ambiguous dates and **flag rather than guess** | *"The dates come in different formats depending on who exported them"* / AC-6 |
| **F6** | Detect duplicate transaction ids that are legitimately repeated across branches | *"Two of the branches have repeated transaction numbers since a till update last year"* |
| **F7** | **Persist every rejected row with a reason, and keep it viewable.** Nothing is thrown away | *"Tell me honestly what it could not work out"* / NN-7 / AC-2 |
| **F8** | **Full lineage: any figure on the dashboard traces back to the raw rows it came from** | *"Last quarter I came close to closing a branch, and then found out the numbers were wrong"* / NN-7 / AC-5 |
| **F9** | A human resolution, made once, is replayed automatically on every later upload | AC-4 |
| **F10** | Aggregate by branch, product, time, and against a comparison period | *"Sales by branch, by product, over time, compared with last month"* |
| **F11** | Bilingual AR/EN UI that **mirrors completely**, including charts, with all numbers/dates/currency through `Intl` | NN-1 … NN-4 / AC-8 |
| **F12** | `docker compose up` on a clean machine | AC-1 |
| **F13** | Seeded demo: 11 branches, ~1 year of deliberately messy transactions, a populated resolve queue and DQ report on first open | AC-9 / "The seed data is a deliverable" |
| **F14** | Public repo, no secrets, no real client data, tests with every task | NN-9 / NN-11 |

**The force that outranks the others is F8.** Traceability is not a feature you add in week three; it is a constraint on every table and every aggregate query in the system. A stack that makes lineage awkward is disqualified no matter how pleasant it is elsewhere.

---

## 3. Decision summary

| Layer | Decision | Primary force served |
|---|---|---|
| Backend language | **Python 3.12** | F1–F6 |
| Backend framework | **FastAPI** + Pydantic v2 | F7, F11 (error codes), F12 |
| ORM / migrations | **SQLAlchemy 2.0** + **Alembic** | F8, F9 |
| Database | **PostgreSQL 16** (JSONB + `pg_trgm`) | F7, F8, F9, F10 |
| Data wrangling | **pandas**, **charset-normalizer**, **openpyxl** | F1, F4 |
| Fuzzy matching | **RapidFuzz** + `pg_trgm` candidate generation | F2 |
| Arabic text | one internal module over **`unicodedata`** — no third-party dependency | F3 |
| Background work | **FastAPI `BackgroundTasks`** + a jobs table (no Celery for v1) | F1, F12 |
| Frontend | **Next.js 15** (App Router) + **TypeScript** | F11 |
| i18n | **next-intl** | F11 |
| Charts | **Apache ECharts** via `echarts-for-react` — with a Sprint-1 spike | F11 (AC-8) |
| Tests | **pytest** (+ golden-file fixtures), **Vitest**, **Playwright** | F14 |
| Orchestration | **Docker Compose** | F12 |

---

## 4. Layer-by-layer analysis

### 4.1 Backend language — Python

**Options considered:** Python · Node/TypeScript · Go

| | Benefits | Costs / risks |
|---|---|---|
| **Python** ✅ | The entire problem — CSV dialect sniffing, encoding detection, fuzzy matching, date-format inference, Unicode normalisation — is solved ground with mature libraries (`pandas`, `charset-normalizer`, `python-dateutil`, `RapidFuzz`, `unicodedata`). This is the code that must be *correct*, not the code we want to be inventing. | Two languages in one repo. Slower runtime than Go. Typing is opt-in, so discipline (mypy, Pydantic) has to be enforced rather than assumed. |
| Node / TypeScript | One language front and back; shared types between API and UI; one toolchain. | The ecosystem for *this* problem is thin. Arabic normalisation, confidence-scored fuzzy matching and CSV dialect inference would largely be hand-written — directly against F2, F3, F5, the three things the client will test hardest. Hand-rolling them is where the project fails. |
| Go | Fast, single binary, trivial containers. | Essentially no data-wrangling ecosystem. Every force F1–F6 becomes bespoke code. Wrong tool for a data-quality product. |

**Verdict: Python.** Not a preference — F1 through F6 are all library problems in Python and all greenfield problems elsewhere. The cost we accept is a two-language repo.

---

### 4.2 Backend framework — FastAPI

**Options considered:** FastAPI · Django + DRF · Flask

| | Benefits | Costs / risks |
|---|---|---|
| **FastAPI** ✅ | Pydantic models make **NN-6 ("the server returns error codes, never prose")** structural rather than aspirational: errors are a typed enum, serialised identically everywhere, and the frontend can generate its TypeScript types from the OpenAPI schema — so a missing translation becomes a *compile error*. Native `async` plus `BackgroundTasks` handles multi-file ingestion without adding Celery and Redis containers (F12). `/docs` gives Imam and the client a browsable API at review time. The codebase stays small enough that the design visibly belongs to the author — which matters for a public portfolio repo (F14). | No ORM, no migrations, no auth, no admin out of the box. Assembling SQLAlchemy + Alembic + auth costs roughly 1–2 days of the budget. Little structural guardrail: it is easy to let a FastAPI app sprawl, so the layering has to be imposed deliberately (see §6). |
| Django + DRF | Batteries included: ORM, migrations, management commands (useful for F13 seeding), a permission system that makes the guest read-only account configuration rather than code, and **a free admin UI** that looks at first glance like a ready-made resolve queue. | The admin advantage is an illusion *here*. The resolve queue is not back-office plumbing — it is the product's main surface, and NN-1 … NN-4 require it to be fully bilingual with complete RTL mirroring and `Intl`-formatted numbers. Django admin will not meet that bar, so the queue gets built in the frontend regardless and the headline benefit evaporates. What remains is DRF serializer verbosity, a weaker async story, and Celery for background ingestion. More framework also sits between the author and the ingestion pipeline, which hides the part of the work this project is meant to demonstrate. |
| Flask | Minimal, familiar, unopinionated. | No typing or schema story, so NN-6 becomes manual discipline; no async; everything FastAPI gives free must be hand-built. Strictly worse than FastAPI for the same effort. |

**Verdict: FastAPI.** Django's genuine strengths are cancelled by NN-1 … NN-4, and its costs are not.

---

### 4.3 Database — PostgreSQL 16

**Options considered:** PostgreSQL · SQLite · MongoDB

| | Benefits | Costs / risks |
|---|---|---|
| **PostgreSQL 16** ✅ | **JSONB** stores each raw row exactly as it arrived, whatever its shape — which is what NN-7 and F8 demand. Foreign keys make lineage *provable* rather than hopeful: a dashboard figure joins to transactions, which join to raw rows, and the database refuses to let that chain break. **`pg_trgm`** gives indexed trigram similarity, so fuzzy matching can shortlist candidates in SQL and only then score them precisely in Python (F2) — the difference between a matcher that runs in a second and one that compares every string to every other string. Unique constraints make F9 (replayed resolutions) and F6 (duplicate ids scoped per branch) enforceable at the storage layer. Mature `ICU`/collation handling for Arabic. A natural `docker compose` service (F12). | One more container. Requires migration discipline from day one — but Alembic is in the stack anyway. |
| SQLite | Zero setup, a file, instant tests. | No `pg_trgm`, weaker JSON, and real write-concurrency limits during multi-file ingestion. It also quietly makes AC-1 (`docker compose up` on a clean machine) meaningless as a demonstration, and it is not a credible choice to defend in a public repo for a multi-branch analytics product. |
| MongoDB | Schema-free documents suit raw rows of unknown shape. | F8 and F9 are relational problems. Lineage without foreign keys is a convention you have to remember rather than a guarantee the engine enforces — exactly the kind of "trust me" the client told us she no longer accepts. F10's aggregations are clumsier. Wrong shape for the dominant force. |

**Verdict: PostgreSQL 16.** JSONB covers the unstructured half, foreign keys enforce the half the client actually cares about.

---

### 4.4 Fuzzy matching — RapidFuzz, with `pg_trgm` for candidate generation

**Options considered:** RapidFuzz · `thefuzz`/`fuzzywuzzy` · `pg_trgm` alone · embeddings

| | Benefits | Costs / risks |
|---|---|---|
| **RapidFuzz + `pg_trgm`** ✅ | RapidFuzz is a fast C++-backed implementation with several scorers (`ratio`, `token_set_ratio`, `partial_ratio`), which matters because *"mug set"*, *"Mug Set 4pc"* and *"طقم أكواب"* fail under different scorers. `pg_trgm` narrows the candidate set in the database so Python only scores plausible pairs. Scores are **deterministic and explainable** — we can show the client the number that drove a decision, which is what NN-8 and AC-3 require. | Thresholds must be tuned against real data and then **published**, not buried. Two moving parts (SQL shortlist + Python score) instead of one. |
| `thefuzz` / `fuzzywuzzy` | Same API, widely known. | Slower; GPL-adjacent licensing history around `python-Levenshtein`. RapidFuzz is a drop-in improvement with an MIT licence. |
| `pg_trgm` alone | One less dependency; everything in SQL. | Trigram similarity alone is a blunt instrument for mixed Arabic/English and for token-order differences. Not enough for F2 on its own. |
| Embeddings / an LLM matcher | Would catch genuine semantic equivalence such as *"mug set"* ↔ *"طقم أكواب"*. | Non-deterministic, unexplainable to the client, needs an API key in a **public repo** (F14), adds latency and cost, and cannot produce the stable published threshold NN-8 is built on. **Rejected for v1** — recorded in §7 as a possible later addition behind the same human-review gate. |

**Verdict: RapidFuzz + `pg_trgm`.** Explainability is a hard requirement, and that rules out the clever option.

---

### 4.5 Arabic normalisation — one internal module, no dependency

NN-5 requires that *all* Arabic matching go through a single module that normalises alef forms, hamza forms, taa marbuta, tatweel and diacritics while keeping the original string.

| | Benefits | Costs / risks |
|---|---|---|
| **Internal module over `unicodedata`** ✅ | The rules are a few dozen well-understood codepoint mappings. Writing them ourselves means they are **readable, unit-testable, and documented with a reason per rule** — which is what the SPEC has to contain anyway. A third-party normaliser would be a black box sitting on top of the project's most important invariant, and would still need wrapping to satisfy NN-5's single-entry-point rule. No dependency risk on a library that may normalise more aggressively than we want. | We own the correctness. Mitigated by making this the most heavily tested module in the repo, with a golden-file table of input → normalised → original. |
| `camel-tools` / `pyarabic` | Linguistically thorough, handles cases we may not anticipate. | Heavy dependencies (`camel-tools` pulls a large ML stack) for a transformation we need to be exactly and only what we specified. Harder to explain to the client why two strings matched. |

**Verdict: internal module.** This is the one place in the stack where "write it yourself" is the correct answer, because NN-5 is about *control*, not convenience.

---

### 4.6 Frontend — Next.js 15 + next-intl

**Options considered:** Next.js + next-intl · Vite + React + react-i18next

| | Benefits | Costs / risks |
|---|---|---|
| **Next.js + next-intl** ✅ | `next-intl`'s message catalogues *are* `ar.json` and `en.json` (NN-1), and its formatters are `Intl` wrappers (NN-4) — so two non-negotiables become the framework's default path rather than a rule we have to keep remembering. Locale-prefixed routing (`/ar`, `/en`) makes setting `dir` and `lang` on `<html>` a documented one-liner (NN-3). Server components let dashboard aggregates render on the server, keeping the client bundle small. Conventional structure that reviewers and future readers recognise. | More concepts to carry: the server/client component split, and auth-cookie handling across that boundary. Heavier container image. Some chart libraries need `"use client"` plus dynamic import to avoid SSR issues. |
| Vite + react-i18next | Simplest possible mental model, fastest HMR, smallest toolchain. SSR is genuinely unnecessary for an internal dashboard. | Locale routing, `dir` switching and the `Intl` helper layer are all hand-wired — more places for NN-1 … NN-4 to be violated quietly, and those are precisely the items on the client's test list (AC-8). |

**Verdict: Next.js + next-intl.** Within a 2–4 week budget, Vite is defensible and would be marginally faster to start. It loses because the non-negotiables that `next-intl` satisfies by default are the same ones that appear on the delivery checklist.

---

### 4.7 Charts — ECharts, with an explicit spike

AC-8: *"Switching language redraws the charts correctly in both directions."* This is the most underestimated line on the acceptance list. **No charting library gives RTL for free.**

| | Benefits | Costs / risks |
|---|---|---|
| **Apache ECharts** (`echarts-for-react`) ✅ | Axis `inverse`, label alignment, legend placement and grid padding are all plain configuration, so a mirrored layout is a config object keyed by direction rather than a second implementation. Handles Arabic label rendering and long-label layout well. Very wide chart range, so F10 is covered without a second library. | Larger bundle; an imperative option-object API that feels unlike React; needs `"use client"` and dynamic import under Next.js. |
| Recharts | Idiomatic React composition, pleasant to write, small. | No RTL concept at all. Axis reversal, tick alignment and tooltip positioning have to be mirrored by hand per chart type — which means AC-8 becomes per-chart manual work and a regression risk on every new chart. |

**Verdict: ECharts** — *provisional.* Sprint 1 carries a half-day spike: one bar chart and one line chart with Arabic category labels, rendered and screenshotted in both directions. If ECharts does not satisfy AC-8 cleanly, we fall back to Recharts behind a thin internal `<Chart>` wrapper. **Every chart goes through that wrapper from the first commit**, so the fallback is a one-file change rather than a rewrite.

---

### 4.8 Background work — `BackgroundTasks`, not Celery

Ingesting eleven files is seconds-to-minutes work, so the upload request cannot block on it.

**Decision:** FastAPI `BackgroundTasks` writing progress to an `ingestion_jobs` table, polled by the UI.

- **Benefit:** no Redis container, no worker container, no separate deploy — AC-1 stays a genuinely clean `docker compose up`, and the budget goes into the matching engine instead of infrastructure.
- **Cost:** work does not survive a process restart, and there is no retry queue or horizontal scaling.
- **Accepted because:** eleven files once a week for one tenant. Celery here would be infrastructure built for a load that does not exist. Recorded in §7 as the first thing to revisit if volume changes.

---

### 4.9 Testing

| Layer | Tool | What it actually proves |
|---|---|---|
| Ingestion & matching | **pytest** with **golden-file fixtures** | The real test strategy: feed the deliberately broken sample files in, assert the exact data-quality report that comes out — row counts, rejection reasons, flagged dates, duplicate ids, match confidences. A change that silently alters the report fails the build. |
| Arabic normalisation | **pytest**, table-driven | Every NN-5 rule has a case, and the original string is asserted preserved. |
| API contract | **pytest** + `httpx` | Every error response is a code with a translation in both locales (NN-6). |
| Frontend units | **Vitest** | Formatting helpers, direction logic, chart option builders. |
| End to end | **Playwright** | Upload → report → resolve → dashboard, run in both locales, with screenshots as the AC-8 evidence. |

A CI check also asserts that `ar.json` and `en.json` have identical key sets — which turns NN-1 from a habit into a gate.

---

## 5. Requirement → stack traceability

Read this column-first in review: if a force has no stack element, we have a gap.

| Force | Served by |
|---|---|
| F1 heterogeneous files | pandas · charset-normalizer · openpyxl · header-mapping table in Postgres |
| F2 product matching | RapidFuzz · `pg_trgm` · `canonical_products` + `product_aliases` tables · published threshold |
| F3 Arabic normalisation | internal `arabic` module · original string column on every text field |
| F4 numerals & currency | internal `numbers` parser (Arabic-Indic → Western) · `Intl` on display |
| F5 ambiguous dates | per-file format inference with confidence · `date_flags` table · never auto-resolved |
| F6 duplicate ids | Postgres unique constraint scoped `(branch_id, external_txn_id)` · duplicate rejection reason |
| F7 nothing thrown away | `rejected_rows` table with reason code · DQ report endpoint · UI view |
| F8 traceability | `raw_rows` (JSONB) ← `transactions` ← aggregates, enforced by foreign keys · drill-down API on every figure |
| F9 learned resolutions | `resolutions` table, replayed by the ingestion pipeline before matching runs |
| F10 analytics | SQL aggregates over `transactions` · ECharts |
| F11 bilingual & mirrored | next-intl · CSS logical properties · `dir`/`lang` on `<html>` · `Intl` · `<Chart>` wrapper |
| F12 one-command startup | Docker Compose: `db`, `api`, `web` |
| F13 seed data | Python seed generator producing deliberately messy synthetic data · `make seed` |
| F14 public repo & tests | pytest · Vitest · Playwright · no `.env` committed · synthetic data only · locale-key parity CI check |

---

## 6. Enforced backend layering

FastAPI imposes no structure, so we impose it. The ingestion pipeline must stay testable without HTTP and without a browser.

```
backend/app/
  api/          HTTP only — routing, auth, serialisation. No business logic.
  domain/       pure logic, no I/O:
                  arabic/      NN-5 single entry point
                  numbers/     Arabic-Indic digits, separators, currency text
                  dates/       format inference + ambiguity detection
                  matching/    scorers, thresholds, decisions
  pipeline/     orchestration: read → normalise → validate → match → persist
  repositories/ all SQLAlchemy access
  models/       SQLAlchemy models + Pydantic schemas
  errors/       error code enum — the only source of API error strings
```

Rule for the executor: **`domain/` imports nothing from `api/` or `repositories/`.** It takes values and returns values, which is why the golden-file tests in §4.9 can exist at all.

---

## 7. Deliberately deferred

Recorded so that "we did not think of it" is never the explanation.

| Deferred | Revisit when |
|---|---|
| Celery + Redis | Volume grows beyond weekly uploads, or job durability across restarts is required |
| Embedding / LLM-assisted matching | After thresholds are tuned on real data — and only behind the same human-review gate |
| Multi-tenancy | A second client |
| Real-time dashboard updates | Client asks; weekly cadence does not justify it |
| Kubernetes / cloud deploy | Delivery is `docker compose` per AC-1 |
| Mobile app | Not requested |

---

## 8. Risks this stack carries

| Risk | Severity | Mitigation |
|---|---|---|
| AC-8 chart mirroring harder than expected | **High** | Sprint-1 spike · all charts behind one `<Chart>` wrapper from the first commit |
| Match thresholds tuned on synthetic data, then wrong on real files | **High** | Thresholds live in config, not code · tune against Rania's real files as soon as they arrive · the resolve queue is the safety net by design |
| Lineage retrofitted instead of designed in | **High** | `raw_rows` and foreign keys land in the very first migration, before any dashboard work |
| Two-language repo slows a solo developer | Medium | Shared `make` targets · one compose file · TypeScript types generated from OpenAPI |
| FastAPI sprawl without framework guardrails | Medium | §6 layering, enforced in review and by an import-linter check in CI |
| Seed generator treated as throwaway | Medium | It is a deliverable (F13) with its own task, tests and review |

---

## 9. What approval means

Approving this ADR approves the stack and the layering in §6 — not the feature scope. Scope is decided in `docs/SPEC.md`, which cannot be written until the client answers the questions in `docs/discovery/QUESTIONS.md`.

**No application code is written until both this ADR and `SPEC.md` are approved.**

---

### Reviewer notes

<!-- Imam: comments here. -->
