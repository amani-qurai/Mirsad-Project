# Mirsad — Project Plan & Management Requirements

| | |
|---|---|
| **Status** | Revised 2026-11-07 after the client's answers — awaiting reviewer approval |
| **Owner / Developer** | Amani |
| **Reviewer / Client proxy** | Imam |
| **Client** | Suha Qasem — Nakheel Retail (UAE, trades in AED) |
| **Repository** | `amani-qurai/Mirsad-Project` (public) |

---

## 1. Schedule — and a correction to my own estimate

### 1.1 What I got wrong

The first version of this plan said four weeks was achievable with discipline. **That figure came from adding up phases in my head, not from summing the tasks.** Having now estimated every task in §6 and added them up, the work is **≈ 31 days after every available cut**, which is about six weeks for one person at five productive days a week.

Four weeks was wrong when I wrote it, and it was wrong before the client's answers added anything. The answers made a bad estimate worse, but they did not cause it.

This is worth stating plainly because the whole project is about not presenting unverified numbers as facts, and an estimate is a number.

### 1.2 Why the work is this size

The dashboard is a two-day job. The client did not ask for a dashboard.

| What looks simple | Why it is not | Days |
|---|---|---|
| "Match the same product written four ways" | Canonical registry, alias table, several scorers for mixed Arabic/English, a published threshold, a never-merge-below rule, a review queue, replay of past decisions — **plus product codes that are only unique within a branch and a numbering era**, because two branches restarted at 1 | **6.5** |
| "Trace any figure back to the original rows" | An architectural constraint on every table and every query — **and now every figure must also declare what is missing from it** | **3.5** |
| "Dates come in different formats" | Per-file inference with confidence, flag-don't-guess, remembered per branch, **and re-checked every upload because the client confirmed formats do change** | **2.0** |
| "One branch writes Arabic, another English" | One normalisation module, keeping originals, the most-tested file in the repo | **1.5** |
| "Switching language redraws the charts" | Complete mirroring including axes, legends, ticks, tooltips. No library does this free | **1.0** |
| Returns | Two branches record a return as a *positive* row with `RTN` in a notes column. Get it wrong and those branches look like they are over-selling | **1.0** |
| "Ship it seeded" | Eleven branches, a year of deliberately broken data exercising every acceptance case. A named deliverable | **2.0** |

### 1.3 The three honest options

| | What the client gets | When |
|---|---|---|
| **A — Four weeks, reduced scope** | The engine and a thin dashboard. Several acceptance criteria not met. **Requires telling her now which ones** | 4 weeks |
| **B — Six weeks, full acceptance list** | Everything on the nine-point list | 6 weeks |
| **C — Four-week core, then two weeks** *(recommended)* | At week 4: upload, clean, data quality report, resolve queue, traceability, a working but minimal dashboard — a real system she can use. Full list two weeks later | 4 + 2 |

**C, for two reasons.** It is the same total as B but puts something working in front of her at week four, which is when feedback is still cheap. And the first four weeks deliver the honesty machinery — the part she actually wrote to us about — rather than a spread of half-finished features.

**A is viable but has a condition:** it means going back to her now and naming what will not be in v1. That conversation is not optional, and doing it late is how projects lose clients.

### 1.4 The decision taken

**Four weeks, cut list activated immediately** (§7). The plan below is built that way. Given §1.1, four weeks delivers the Option C core, not the full acceptance list — §7 names exactly what that leaves out.

---

## 2. Roles

| Role | Who | Responsibility |
|---|---|---|
| Product owner / client | Suha (played by Imam) | Answers discovery questions, accepts delivery |
| Weekly user | Rania | The only person who uses this every week. **Not yet consulted** |
| Developer & architect | Amani | All design decisions, all code, all PRs |
| Reviewer | Imam | Approves ADRs and the SPEC, reviews every PR, tests at delivery |
| Executor | Claude Code | Implements approved tasks only, inside the rules in §9 |

**The executor does not make design decisions.** It receives a task with acceptance criteria and implements it. Any ambiguity comes back as a question, not as an invented assumption.

---

## 3. Lifecycle, and where Agile actually applies

Agile does not mean skipping the specification. It means the *build* is iterative while requirements and architecture are settled once, because they are the expensive things to change.

```
Phase 0  Discovery        ✅ answers in, impact assessed
Phase 0b Rania interview  ← we are here, and SPEC.md is blocked on it
Phase 1  Spec & Design       gate: reviewer approval
Phase 2  Sprint 1  Foundations & parsing
Phase 3  Sprint 2  Data quality engine        ← the product
Phase 4  Sprint 3  Dashboard, traceability, completeness
Phase 5  Sprint 4  Seed, hardening, delivery
```

| Done once, up front | Done iteratively |
|---|---|
| Requirements (`QUESTIONS.md` → `ANSWERS.md` → `SPEC.md`) | Feature implementation |
| Stack & layering (`ADR-0001`) | UI refinement |
| Data model, lineage and scope design | Threshold tuning |
| Error-code catalogue | Test coverage |

**Gate rule: no application code until `ADR-0001` and `SPEC.md` are both approved.**

---

## 4. Phase 0 — Discovery ✅

| Deliverable | State |
|---|---|
| `docs/decisions/ADR-0001-technology-stack.md` | Written, in PR #1 |
| `docs/discovery/QUESTIONS.md` | Sent |
| `docs/discovery/ANSWERS.md` | **Received** — all thirteen answered |
| `docs/discovery/IMPACT.md` | Written — five defaults changed, three of our assumptions corrected |
| Rania's six weeks of real files | **Sunday** |

---

## 5. Phase 0b — Rania ← blocking

> *"Talk to Rania before you write the specification."* — the client, and she is right.

Rania is the only weekly user. If the resolve queue is tedious she returns to the spreadsheet and everything else stops mattering. Questions in `docs/discovery/RANIA-INTERVIEW.md`.

**Exit criteria:** the conversation has happened; her alias sheet (if one exists) is in hand; her answer to *"what would make you stop using it"* is recorded verbatim in `SPEC.md`.

---

## 6. Phase 1 — Specification (2–3 days)

`docs/SPEC.md` must contain:

1. What gets built — **and what explicitly does not**. The second list matters more, and after §1.3 it is the more important half of this document.
2. The screens — upload, data quality report, resolve queue, dashboard, drill-down, settings.
3. The data model as an ERD, with the lineage chain `raw_rows → transactions → aggregates` visible, plus scope flags, branch lifecycle, return convention and VAT basis.
4. **Every data quality rule with its reason.**
5. What an unusable row looks like, its reason codes, and where it is viewable.
6. The error-code catalogue, AR and EN, including the nine new codes in `IMPACT.md` §6.
7. A time estimate per phase that is **summed**, not eyeballed.
8. The nine acceptance criteria copied verbatim, each mapped to the task that satisfies it — and each one not being met in four weeks marked as such.

---

## 7. Sprint plan — cut list activated

One-week sprints, five productive days each. Day estimates are per task and summed per sprint. **Where a sprint total exceeds five days, that is stated rather than hidden.**

Cuts applied up front are marked ✂.

### Sprint 1 — Foundations & parsing · 9.5 days
*Goal: a file is uploaded, read correctly, stored with full lineage. No matching yet.*

| ID | Task | Days |
|---|---|---|
| M-001 | Repo scaffold, Docker Compose (`db`/`api`/`web`), Makefile, CI | 1.0 |
| M-002 | i18n foundation: next-intl, `ar.json`/`en.json`, **AED / `ar-AE` / `en-AE`**, `Intl` helpers, locale-parity CI gate | 1.0 |
| M-003 | Migration 1 — lineage foreign keys, scope flags, branch `opened_at`/`closed_at`, `return_convention`, `vat_basis` | 1.0 |
| M-004 | `domain/arabic` — single normalisation entry point, originals preserved | 1.5 |
| M-005 | `domain/numbers` — Arabic-Indic digits, separators, trailing currency text | 0.5 |
| M-006 | `domain/dates` — inference, ambiguity, **format-change detection between uploads** | 2.0 |
| M-007 | Auth, three roles, read-only guest | 1.0 |
| M-008 | Upload: **content-based format sniffing** (one branch sends CSV named `.xls`), encoding, header mapping incl. the notes column, background job | 1.5 |

### Sprint 2 — Data quality engine · 10.25 days
*The product. The sprint that must not be compressed.*

| ID | Task | Days |
|---|---|---|
| M-009 | Validation, **scope eligibility**, reason codes; nothing discarded | 2.0 |
| M-010 | Duplicate detection — within file, and within branch | 0.5 |
| M-011 | Return conventions per branch, `RTN` note parsing, **zero-returns-is-a-finding** | 1.0 |
| M-012 | Product code eras, code/name conflict → `held` | 1.0 |
| M-013 | Matching ladder, thresholds in config, never merge below | 2.0 |
| M-014 | Resolve queue API — resolve, reverse, audit trail ✂ *API only, no audit screen* | 0.75 |
| M-015 | Resolve queue UI, bilingual and mirrored | 1.5 |
| M-016 | Resolutions replay on next upload | 0.5 |
| M-017 | DQ report API + UI, incl. VAT and discount findings | 1.0 |

### Sprint 3 — Dashboard, traceability, completeness · 7.0 days

| ID | Task | Days |
|---|---|---|
| M-018 | Aggregates API — **arbitrary date ranges**, comparison, completeness blocks on every figure | 2.0 |
| M-019 | `<Chart>` wrapper + RTL mirroring spike ✂ *bar and line only* | 0.75 |
| M-020 | Dashboard screens — default view answers *"which branch needs attention"* | 2.0 |
| M-021 | Drill-down: every figure traces to its raw rows | 1.5 |
| M-022 | Comparison fairness markers + branch lifecycle ✂ *opening handled; closing is a column, no UI* | 0.5 |
| M-023 | Matching health ✂ *two numbers, not a trend chart* | 0.25 |

### Sprint 4 — Seed, hardening, delivery · 4.5 days

| ID | Task | Days |
|---|---|---|
| M-024 | **Seed generator** — 11 branches, ~1 year, deliberately messy, resolve queue and DQ report populated on first open | 2.0 |
| M-025 | Playwright E2E ✂ *one happy path per locale* | 0.75 |
| M-026 | Security review and public-repo hygiene | 0.5 |
| M-027 | README, delivery guide, acceptance walkthrough on a clean machine | 1.0 |
| M-028 | Confirm hosting pricing against live figures before anything is quoted | 0.25 |

### Deferred by the cut — tell the client

| Cut | Consequence |
|---|---|
| Export DQ report to CSV/XLSX | Readable in-app only |
| Mobile-responsive layout | **She checks numbers from her phone while travelling.** The highest-regret cut on this list |
| Quantity-scope analytics | Value-based views only |
| Audit-trail screen | Reversals are logged and API-readable, not browsable |
| Branch-closing UI | The column exists; closing a branch needs a developer |
| Chart variety beyond bar and line | — |

**Totals: 31.25 days ≈ 6.2 weeks.** Four weeks reaches roughly the end of Sprint 2 plus the start of Sprint 3 — the Option C core.

### Never cut, under any circumstance

- Traceability and completeness (M-018, M-021) — AC-5, and the reason she hired us
- Resolve queue and never-merge-below-threshold (M-013, M-014, M-015)
- The data quality report (M-017)
- Flag-don't-guess on dates (M-006)
- Arabic normalisation through one module (M-004)
- Return convention detection (M-011) — getting it wrong inverts two branches
- The seed data (M-024)
- Tests

Cutting from this list produces a beautiful chart built on data nobody checked.

### A cut that is no longer available

The original cut list offered **comparison-period charts**. The client's answers removed that option: questions 7 and 9 are entirely about comparison fairness, and *"whether a branch is worth keeping"* depends on it. Cutting it would remove the thing that nearly cost her a branch.

**The lesson is general: a cut list written before the client answers is a guess.** This one was revised the day the answers arrived, and should be revised again after Rania.

---

## 8. Definition of Ready / Definition of Done

**A task may start only when it has:** an ID, a one-sentence goal, explicit acceptance criteria, the files it is expected to touch, the acceptance criterion or non-negotiable it serves, and no unresolved design question.

**A task is done only when:**

- [ ] Acceptance criteria met and demonstrable
- [ ] Tests written and passing — **no PR without tests** (NN-9)
- [ ] Every user-visible string through `t()`, keys in **both** `ar.json` and `en.json` **in the same commit** (NN-1)
- [ ] CSS logical properties only (NN-2)
- [ ] Numbers, currency and dates through `Intl`, **AED**, `ar-AE` / `en-AE` (NN-4)
- [ ] Arabic matching only via `domain/arabic` (NN-5)
- [ ] Server errors are codes, translated in both locales (NN-6)
- [ ] Unusable rows carry a reason, stay viewable, raw row retained (NN-7)
- [ ] **Every aggregate carries its completeness statement**
- [ ] Nothing merged below the confidence threshold (NN-8)
- [ ] No secrets, no `.env`, no real client data (NN-11)
- [ ] Checked in both `ar` and `en`, layout mirrors
- [ ] PR reviewed and approved by Imam — **never self-merged** (NN-10)
- [ ] `docs/` updated if the design changed

---

## 9. Workflow and executor governance

### Branching
```
main                    protected — never committed to directly, never force-pushed
task/<ID>-<slug>        e.g. task/M-004-arabic-normalisation
```

### Commits
```
<type>(<ID>): <summary>        e.g. feat(M-004): normalise alef and hamza forms
```
Locale keys ship in the same commit as the string that uses them.

### Governing the executor

1. **`CLAUDE.md`** — the eleven non-negotiables, the layering, the severity-and-scope model.
2. **The `mirsad-conventions` skill** — normalisation rule table, error-code catalogue, i18n checklist.
3. **A task brief per task** — goal, acceptance criteria, files, non-negotiables in play, out of scope.

### Skills

| Skill | Used for | When |
|---|---|---|
| `dataviz` | Charts, stat tiles, dashboard layout, palette | Sprint 3, before the first chart |
| `code-review` | Every PR before Imam sees it | Every sprint |
| `security-review` | Upload hardening, public-repo hygiene | M-026 |
| `anthropic-skills:xlsx` | Rania's real Excel exports | Sunday onward |
| `skill-creator` | Revising `mirsad-conventions` | As conventions change |

---

## 10. Change control

After `SPEC.md` is approved, a new client request is:

1. Written into `docs/CHANGE-LOG.md` with its date and origin
2. Sized, with its effect on the sprint plan stated
3. Either accepted **with something named that it displaces**, or deferred

Nothing is quietly absorbed. The client should always know what her request cost.

---

## 11. Risk register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| **Four weeks does not fit 31 days of work** | **Critical** | **Certain** | §1.3 — the scope delivered at week 4 is the Option C core, and the client is told which acceptance criteria are not met |
| Real files are worse than assumed | High | **High** | Six weeks of real files arrive Sunday; thresholds live in config, not code |
| Return convention misread → a branch looks like it is over-selling | High | Medium | M-011, plus zero-returns treated as a finding |
| Product code eras misread → two products merged across the renumbering | High | Medium | Code never identifies alone; conflicts are `held` |
| Chart RTL mirroring harder than estimated | High | Medium | Sprint-3 spike; all charts behind one wrapper |
| Lineage or completeness retrofitted | **Critical** | Low | Both land in M-003, before any dashboard work |
| Rania disengages and returns to the spreadsheet | **Critical** | Medium | Phase 0b; her answer to *"what would make you stop"* goes in `SPEC.md` |
| Mobile cut, but she checks from her phone | Medium | **High** | Flagged as the highest-regret cut; first thing restored if time appears |
| Estimates eyeballed rather than summed | High | — | §1.1. Every future estimate is per task and summed |

---

## 12. Reporting

| Cadence | Artefact |
|---|---|
| Per task | PR with the §8 checklist completed |
| Per sprint | A demo against the sprint goal, and what moved, slipped or was cut |
| Week 2 | **Checkpoint.** The cut list is already spent, so if Sprint 2 is not working the *date* moves, not the quality |
| At delivery | Walkthrough of all nine acceptance criteria on a clean machine, with the unmet ones named |

---

## 13. Immediate next actions

| # | Action | Owner | Blocks |
|---|---|---|---|
| 1 | Decide between options A, B and C in §1.3 | Amani + Imam | Everything |
| 2 | **Interview Rania** | Amani | `SPEC.md` |
| 3 | Collect and examine the six weeks of real files | Amani | Sprint 2 thresholds |
| 4 | If option A: tell the client which acceptance criteria v1 will not meet | Amani | Trust |
| 5 | Write `SPEC.md` | Amani | All development |
| 6 | Approve PR #1 | Imam | Sprint 1 |

**Not before then: not one line of application code.**
