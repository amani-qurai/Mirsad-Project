# Mirsad — Project Plan & Management Requirements

| | |
|---|---|
| **Status** | Proposed — awaiting reviewer approval |
| **Date** | 2026-11-07 |
| **Owner / Developer** | Amani |
| **Reviewer / Client proxy** | Imam |
| **Client** | Suha Qasem — Nakheel Retail |
| **Repository** | `amani-qurai/Mirsad-Project` (public) |

---

## 1. An honest complexity assessment — read this first

The working assumption was *"2–4 weeks, it does not contain complexity things."* **The first half of that is wrong and it is worth saying so now rather than in week three.**

The dashboard is easy. Charts over a clean table are a two-day job. But the client did not ask for a dashboard — she asked for a system that tells her what it could not work out. That is the hard part, and it is most of the project.

| What looks simple | Why it is not | Realistic size |
|---|---|---|
| "Match the same product written four ways" | A canonical product registry, an alias table, several scoring strategies for mixed Arabic/English, a published threshold, a never-merge-below-threshold rule, a human review queue, and replay of past decisions on new uploads. This is a subsystem, not a function. | **4–6 days** |
| "Trace any figure back to the original rows" | An architectural constraint on every table and every aggregate query. Raw rows stored as they arrived, foreign keys all the way up, and a drill-down path on every number the UI renders. Retrofitted, it is a rewrite. | **2–3 days, but only if designed in on day one** |
| "Dates come in different formats" | Per-file format inference with a confidence measure, a flag-don't-guess rule, a resolution that is remembered per branch, and flagged rows excluded from totals rather than estimated. | **2 days** |
| "One branch writes Arabic, another English" | A single normalisation module — alef, hamza, taa marbuta, tatweel, diacritics — that keeps the original string, is the only entry point in the codebase, and is the most heavily tested file in the repo. | **1–2 days** |
| "Switching language redraws the charts" | Complete layout mirroring including axes, legends, tick alignment and tooltips. No charting library does this for free. | **2–3 days** |
| "Ship it seeded" | A generator producing eleven branches and a year of *deliberately and realistically broken* data that exercises every acceptance case. It is named as a deliverable, and an empty dashboard proves nothing. | **2 days** |

**Conclusion.**

- **2 weeks:** not achievable at the stated acceptance bar. It would produce a working uploader and a dashboard with the honesty removed — which is the one thing the client said she does not want.
- **4 weeks:** achievable, with scope discipline, the defaults in `QUESTIONS.md` accepted, and no exploratory detours. **This is the recommended plan.**
- **6 weeks:** comfortable, with a real test suite and polish.

The plan below is built for **four weeks**, with a mid-point checkpoint and a pre-agreed cut list (§7) so that if we fall behind, we drop features we chose in advance rather than quality we did not.

---

## 2. Roles

| Role | Who | Responsibility |
|---|---|---|
| Product owner / client | Suha (played by Imam) | Answers discovery questions, accepts delivery |
| Developer & architect | Amani | All design decisions, all code, all PRs |
| Reviewer | Imam | Approves ADRs and the SPEC, reviews every PR, tests at delivery |
| Executor | Claude Code | Implements approved tasks only, inside the rules in §9 |

**The executor does not make design decisions.** It receives a task with acceptance criteria and implements it. Any ambiguity comes back as a question, not as an invented assumption.

---

## 3. Lifecycle, and where Agile actually applies

Agile does not mean skipping the specification. It means the *build* is iterative while requirements and architecture are settled once, up front, because they are the expensive things to change.

```
Phase 0  Discovery        ← we are here
Phase 1  Spec & Design       gate: reviewer approval
Phase 2  Sprint 1  Foundations & parsing
Phase 3  Sprint 2  Data quality engine        ← the product
Phase 4  Sprint 3  Dashboard & traceability
Phase 5  Sprint 4  Seed, hardening, delivery
```

| Done once, up front | Done iteratively |
|---|---|
| Requirements (`QUESTIONS.md` → `SPEC.md`) | Feature implementation |
| Stack & layering (`ADR-0001`) | UI refinement |
| Data model & lineage design | Threshold tuning |
| Error-code catalogue | Test coverage |

**Gate rule: no application code is written until `ADR-0001` and `SPEC.md` are both approved.** The brief states it plainly — *"A project that starts with code ends in a rewrite."*

---

## 4. Phase 0 — Discovery (now)

| Deliverable | State |
|---|---|
| `docs/decisions/ADR-0001-technology-stack.md` | Written, awaiting approval |
| `docs/discovery/QUESTIONS.md` — 13 questions, three-part format | Written, ready to send |
| Rania's real sample files | **Requested — blocking** |
| `docs/discovery/ANSWERS.md` | Pending client reply |

**Exit criteria:** answers (or *"defaults are fine"*) received, sample files in hand, ADR approved.

**Blocking risk:** the sample files matter more than the answers. Match thresholds tuned on synthetic data and then met with real files is the most likely cause of rework in this project. Chase the files.

---

## 5. Phase 1 — Specification & design (2–3 days)

`docs/SPEC.md` must contain, per the brief:

1. **What gets built — and what explicitly does not.** The second list matters more.
2. The screens — upload, data quality report, resolve queue, dashboard, drill-down, settings.
3. The data model, as an ERD, with the lineage chain `raw_rows → transactions → aggregates` visible.
4. **Every data quality rule with its reason.** A rule without a reason cannot be defended to the client or changed safely later.
5. What an unusable row looks like, the reason codes it can carry, and where it is viewable.
6. The error-code catalogue, with AR and EN translations for every code (NN-6).
7. A time estimate per phase.
8. **The nine acceptance criteria copied in verbatim**, each mapped to the task that satisfies it.

Supporting design documents: `docs/design/DATA-MODEL.md`, `docs/design/API.md`, `docs/design/DQ-RULES.md`, `docs/design/SCREENS.md`.

**Exit criteria:** reviewer approval, recorded in the PR.

---

## 6. Sprint plan

One-week sprints. Each task is one branch, one PR, one review. Task IDs are stable and referenced by every commit, branch and PR.

### Sprint 1 — Foundations & parsing
*Goal: a file can be uploaded, read correctly, and stored with full lineage. No matching yet.*

| ID | Task | Serves |
|---|---|---|
| M-001 | Repo scaffold, Docker Compose (`db`/`api`/`web`), Makefile, CI pipeline | AC-1 |
| M-002 | i18n foundation: next-intl, `ar.json`/`en.json`, `dir`/`lang` on root, `Intl` helpers, **CI check that locale key sets are identical** | NN-1–4 |
| M-003 | Migration 1 — `branches`, `raw_rows` (JSONB), `transactions`, `rejected_rows`, `ingestion_jobs`, **with the lineage foreign keys** | AC-5, NN-7 |
| M-004 | `domain/arabic` — the single normalisation entry point, original string preserved | NN-5 |
| M-005 | `domain/numbers` — Arabic-Indic digits, thousands separators, trailing currency text | AC-7 |
| M-006 | `domain/dates` — per-file format inference, ambiguity detection, flag-never-guess | AC-6 |
| M-007 | Auth and three roles, including the read-only guest account | AC-9 |
| M-008 | Upload endpoint, encoding detection, header mapping, background job with status | — |

**Sprint 1 demo:** upload a broken file, see raw rows stored, flagged dates listed, nothing silently corrected.

### Sprint 2 — The data quality engine
*Goal: the actual product. This is the sprint that must not be compressed.*

| ID | Task | Serves |
|---|---|---|
| M-009 | Validation and rejection rules with reason codes; nothing discarded | AC-2, NN-7 |
| M-010 | Duplicate transaction id detection, scoped per branch | — |
| M-011 | `canonical_products` + `product_aliases`; exact → normalised → fuzzy matching ladder | AC-3 |
| M-012 | Confidence thresholds in configuration, published in the UI; **never merge below threshold** | NN-8 |
| M-013 | Resolve queue API — pending decisions, resolve, reverse, audit trail | AC-3 |
| M-014 | Resolve queue UI, fully bilingual and mirrored | AC-3, AC-8 |
| M-015 | `resolutions` replay — a decision made once is applied on the next upload | AC-4 |
| M-016 | Data quality report API and UI — every problem found, named | AC-2 |

**Sprint 2 demo — the mid-point checkpoint.** Upload eleven messy files, get one clean dataset plus a report naming every problem, with uncertain matches asked rather than assumed. **If this is not working at the end of week 2, the cut list in §7 activates.**

### Sprint 3 — Dashboard & traceability

| ID | Task | Serves |
|---|---|---|
| M-017 | Aggregates API — by branch, product, time, with comparison period | — |
| M-018 | `<Chart>` wrapper + **RTL mirroring spike** (bar and line, Arabic labels, both directions, screenshots) | AC-8 |
| M-019 | Dashboard screens | — |
| M-020 | **Drill-down: every figure on the dashboard traces to the raw rows behind it** | AC-5 |
| M-021 | Not-like-for-like marking when a comparison period has missing days | — |

**Sprint 3 demo:** click any number, reach the original rows. Switch language, everything mirrors.

### Sprint 4 — Seed, hardening, delivery

| ID | Task | Serves |
|---|---|---|
| M-022 | **Seed generator** — 11 branches, ~1 year, deliberately messy; resolve queue and DQ report populated on first open | AC-9 + "seed is a deliverable" |
| M-023 | Export the DQ report and rejected rows as CSV/XLSX | — |
| M-024 | Playwright end-to-end in both locales, screenshots as AC-8 evidence | NN-9 |
| M-025 | Security review and public-repo hygiene — no secrets, no real data, upload hardening | NN-11 |
| M-026 | README, delivery guide, acceptance walkthrough against all nine criteria on a clean machine | AC-1 |

---

## 7. Pre-agreed cut list

Decided now, while nobody is under pressure. If we are behind at the week-2 checkpoint, we cut **in this order**:

1. Export to CSV/XLSX (M-023) — report stays readable in-app
2. Comparison-period charts (M-021) — current-period views remain
3. Playwright coverage reduced to one happy path per locale (M-024)
4. Chart variety reduced to bar and line only

**Never cut, under any circumstance:**

- Traceability (M-020) — it is acceptance criterion 5 and the reason the client hired us
- The resolve queue and the never-merge-below-threshold rule (M-012, M-013)
- The data quality report (M-016)
- Flag-don't-guess on dates (M-006)
- Arabic normalisation through one module (M-004)
- The seed data (M-022)
- Tests

Cutting from this second list produces a beautiful chart built on data nobody checked — the exact thing the client wrote to us to avoid.

---

## 8. Definition of Ready / Definition of Done

**A task may start only when it has:** an ID, a one-sentence goal, explicit acceptance criteria, the files it is expected to touch, the acceptance criterion or non-negotiable it serves, and no unresolved design question.

**A task is done only when:**

- [ ] Acceptance criteria met and demonstrable
- [ ] Tests written and passing — **no PR without tests** (NN-9)
- [ ] Every user-visible string goes through `t()`, with keys in **both** `ar.json` and `en.json` **in the same commit** (NN-1)
- [ ] CSS logical properties only — no `margin-left`, no `padding-right` (NN-2)
- [ ] Numbers, currency and dates formatted through `Intl` (NN-4)
- [ ] Any Arabic matching goes through `domain/arabic` and nowhere else (NN-5)
- [ ] Server errors are codes, translated in both locales — never prose (NN-6)
- [ ] Unusable rows rejected with a reason and still viewable; raw row retained (NN-7)
- [ ] Nothing merged below the confidence threshold (NN-8)
- [ ] No secrets, no `.env`, no real client data; any seed data synthetic and realistic (NN-11)
- [ ] Checked in both `ar` and `en`, and the layout mirrors
- [ ] PR reviewed and approved by Imam — **never self-merged** (NN-10)
- [ ] `docs/` updated if the design changed

---

## 9. Workflow and executor governance

### Branching
```
main                    protected — never committed to directly, never force-pushed
task/<ID>-<slug>        e.g. task/M-004-arabic-normalisation
```
One task, one branch, one PR, one review, then merge. **Never merge something nobody read.**

### Commits
```
<type>(<ID>): <summary>        e.g. feat(M-004): normalise alef and hamza forms
```
Locale keys ship in the same commit as the string that uses them.

### Governing the executor
Three mechanisms, in order of authority:

1. **`CLAUDE.md` at the repo root** — the eleven non-negotiables written as rules the executor reads on every session, plus the §6 layering from the ADR. Created as task **M-000**, before any code.
2. **A project skill, `mirsad-conventions`** — the detailed conventions too long for `CLAUDE.md`: the Arabic normalisation rule table, the error-code catalogue, the i18n checklist, the rejection reason codes. Loaded when the executor touches those areas.
3. **A task brief per task** — goal, acceptance criteria, files, non-negotiables in play, and what is explicitly out of scope.

### Skills to use

| Skill | Used for | When |
|---|---|---|
| `dataviz` | Every chart, the stat tiles, the dashboard layout, the palette | Sprint 3, before the first line of chart code |
| `code-review` | Every PR before requesting Imam's review | Every sprint |
| `security-review` | File-upload hardening, public-repo hygiene | Sprint 4 (M-025) |
| `anthropic-skills:xlsx` | Reading Rania's real Excel exports; the XLSX export | Phase 0, Sprint 4 |
| `init` | Generating the first `CLAUDE.md` | M-000 |
| `skill-creator` | Building `mirsad-conventions` | M-000 |
| `update-config` | Hooks that enforce the non-negotiables mechanically | M-000 |

There is no off-the-shelf FastAPI or Next.js skill available, and none is needed — the framework knowledge is not the risk here. **The risk is the eleven non-negotiables being forgotten on task seventeen**, which is what `CLAUDE.md` plus a hook that fails a commit touching `ar.json` without `en.json` actually prevents.

---

## 10. Change control

Discovery questions are answered once. After `SPEC.md` is approved, a new client request is handled as follows:

1. Written into `docs/CHANGE-LOG.md` with its date and origin
2. Sized and assessed for impact on the sprint plan
3. Either accepted with something named that it displaces, or deferred to a "after delivery" list

Nothing is quietly absorbed. The client should always know what her request cost.

---

## 11. Risk register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Real files are worse than the synthetic assumptions | High | **High** | Get Rania's files before Sprint 2; thresholds live in config, not code |
| Chart RTL mirroring harder than estimated | High | Medium | Spike in Sprint 3 behind a `<Chart>` wrapper; Recharts fallback is a one-file change |
| Lineage retrofitted rather than designed in | **Critical** | Low if M-003 lands first | Lineage foreign keys are in the first migration, before any dashboard work |
| Scope creep from "yes, the normal things" in the client email | High | Medium | `SPEC.md` out-of-scope list; §10 change control |
| 2-week expectation held while the plan says 4 | High | — | **This document, §1** |
| Non-negotiables eroding as the task count grows | High | Medium | `CLAUDE.md` + commit hooks + the §8 checklist on every PR |
| Seed data treated as throwaway | Medium | Medium | It is M-022, a reviewed task with tests, not a script written at midnight |
| Solo developer across two languages | Medium | Medium | Shared `make` targets; TypeScript types generated from OpenAPI |

---

## 12. Reporting

| Cadence | Artefact |
|---|---|
| Per task | PR with the §8 checklist completed |
| Per sprint | A demo against the sprint goal, and a short note on what moved, what slipped, and what was cut |
| Week 2 | **Checkpoint** — if the Sprint 2 demo does not work, the §7 cut list activates |
| At delivery | A walkthrough of all nine acceptance criteria on a clean machine |

---

## 13. Immediate next actions

| # | Action | Owner | Blocks |
|---|---|---|---|
| 1 | Approve or comment on `ADR-0001` | Imam | All development |
| 2 | Send `QUESTIONS.md` to the client | Amani | `SPEC.md` |
| 3 | Request Rania's real sample files | Amani | Sprint 2 threshold tuning |
| 4 | Write `SPEC.md` once answers arrive | Amani | All development |
| 5 | M-000 — `CLAUDE.md`, `mirsad-conventions`, enforcement hooks | Amani | Sprint 1 |

**Not before then: not one line of application code.**
