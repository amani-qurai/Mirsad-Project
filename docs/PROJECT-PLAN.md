# Mirsad — Project Plan & Management Requirements

| | |
|---|---|
| **Status** | Revised 2026-11-08 after the client chose Option 2 — awaiting reviewer approval |
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
| **C — Four-week core, then two weeks** ✅ **chosen** | At week 4: upload, clean, data quality report, resolve queue, traceability, a working but minimal dashboard — a real system she can use. Full list two weeks later | 4 + 2 |

> **The description of C in that table is the sentence §1.5 found wrong.** It is left as written, because it is what the client was shown. The contents and dates that replace it are §1.7 and §7.1 — and unlike this row, they show the task sum they came from.

**C, for two reasons.** It is the same total as B but puts something working in front of her at week four, which is when feedback is still cheap. And the first four weeks deliver the honesty machinery — the part she actually wrote to us about — rather than a spread of half-finished features.

**A is viable but has a condition:** it means going back to her now and naming what will not be in v1. That conversation is not optional, and doing it late is how projects lose clients.

### 1.4 The decision taken — and the date we did not have

**The client chose Option C** (her "Option 2"): four weeks, then two. Reply recorded verbatim in `docs/discovery/CLIENT-REPLY-001.md`.

She also gave us the constraint that should have shaped the schedule from the start:

> **Her quarterly branch review is on 20 December** — the meeting where she decides what happens to each of the eleven branches, *"including the branch I nearly closed last time."*

This is now the project's anchor, and it changes how the schedule is read:

- The deliverable is not "a system by date X". It is **a system she has had time to distrust, test and come to rely on before 20 December.** Software delivered the day before that meeting has negative value: she would walk in with numbers she had no reason to believe and use the spreadsheet instead.
- It tells us **which figures matter first.** The meeting is about *branches*, not products. Branch totals, comparison fairness, completeness and traceability are load-bearing on 20 December. Product-level precision is not.
- It raises the cost of being wrong. She will decide a branch's future using this system. A silently incomplete branch total on that day is the original failure, reproduced by us, on the day it does the most damage.

**She was right that she should have volunteered it, and we should have asked.** Thirteen questions about her data and none about her calendar. The lesson is recorded in §1.6.

### 1.5 A second arithmetic error, found the same way as the first

**`CLIENT-UPDATE-001.md` told her what four weeks delivers. That list does not fit in four weeks, and I had the numbers to check it in the same document.**

| | Days |
|---|---|
| Sprint 1 — foundations & parsing | 9.5 |
| Sprint 2 — data quality engine | 10.25 |
| Sprint 3 items named in the four-week list (M-018, M-019, M-020, M-021, M-022) | 6.75 |
| **Promised at four weeks** | **26.5** |
| **Available in four weeks** | **20.0** |
| **Shortfall** | **6.5** |

The four-week list in update 001 included *"a dashboard: sales by branch, by product, over any date range"* and *"any figure traced back to the original rows"*. Those are Sprint 3 tasks. §7 of this document already said four weeks *"reaches roughly the end of Sprint 2"* — Sprints 1 and 2 sum to 19.75 days, which consumes the whole four weeks on their own.

So two statements in two committed documents contradicted each other, and the prose one went to the client.

**This is the same error as §1.1, one level down.** The first was summing phases instead of tasks. This was describing a delivery instead of summing the tasks inside it. Both come from writing a sentence about numbers without re-deriving the numbers. The habit that fixes it is mechanical, not attitudinal: **any statement of the form "at date X you will have Y" is written by summing task IDs, and the sum is shown.** Every such statement in this plan now shows its arithmetic.

### 1.6 What the two estimation errors have in common

Worth stating once, because it is the project's own subject matter applied to its management:

| | The data | The estimate |
|---|---|---|
| The failure | A figure presented without what is missing from it | A date presented without the tasks summed into it |
| Why it survives review | The number looks plausible | The date looks plausible |
| The fix | Every aggregate carries a completeness statement | Every date carries its summed task list |

We are building a system whose entire premise is that a plausible-looking number is the dangerous kind. Both estimation errors were plausible-looking numbers. **The plan is held to the standard the software is held to**, which is why §1.7 shows its working and why the delivery dates below are ranges attached to task sums rather than round weeks.

### 1.7 Delivery calendar — shown with its arithmetic

Assumes the first working day is **Monday 9 November 2026**, five productive days a week, and the reductions in §7.1.

| | Task days | Lands | Her working days before 20 Dec |
|---|---|---|---|
| Four weeks as originally stated | 20.0 | Fri 4 Dec | — *(does not include a dashboard)* |
| **Block one, reduced** (§7.1) | **22.25** | **Wed 9 Dec** | **7** |
| **Block one + the phone screen** (§7.2) | **23.75** | **Thu 10 Dec** | **6** |
| Block two — the remainder | 9.0 | from Mon 21 Dec → ~Thu 31 Dec, or from Mon 4 Jan → ~Thu 14 Jan | *after the review* |

Three consequences, all of which the client has been told:

1. **Four weeks does not reach a dashboard.** The earliest a system she can look at exists is **Wednesday 9 December**, not 4 December. That still clears 20 December with seven working days of her own use, which is what she chose Option 2 for.
2. **Block two runs after the review, not before it.** The ten working days between delivery and 20 December are *her* fortnight. Shipping new features into them would change the system under her in the fortnight she is learning to trust it — defeating the entire reason she chose this option. Those days are reserved for defects she finds, and nothing else lands.
3. **"Mid-December" is no longer a delivery slot.** Anything not in block one arrives after the review. This is why the phone screen has to be decided now rather than deferred (§7.2).

**The freeze is a commitment, not a gap.** Between 10 and 18 December the only changes are fixes to defects she or Rania report. If that window turns out to be quiet, the time goes to the top of the block-two list — it is not re-spent on new work inside the freeze.

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
Phase 0  Discovery        ✅ answers in, impact assessed, timeline agreed (Option 2)
Phase 0b Rania interview  ← we are here, and SPEC.md is blocked on it
         + the trading calendar, which the thirteen questions missed (§4)
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
| `docs/discovery/CLIENT-UPDATE-001.md` | Sent — timeline correction |
| `docs/discovery/CLIENT-REPLY-001.md` | **Received** — Option 2 chosen, 20 December given |
| `docs/discovery/CLIENT-UPDATE-002.md` | Drafted — phone answer, the §1.5 error, the freeze, two questions back |
| Rania's six weeks of real files | **Sunday** |

### Still open, and blocking `SPEC.md`

| Open item | Why it blocks the spec | Asked in |
|---|---|---|
| **The trading calendar** — which days each branch does not trade, and which day the week starts on | Week boundaries decide every period comparison; non-trading days decide whether an empty day is normal or a missing file; the branch's local timezone decides which date a late-evening sale lands on. All three are invisible when wrong. **Not one of the thirteen questions covered this** | Update 002 |
| The Tulkarem file Rania calls *"not really a file"* | If it is a PDF, a scan or a typed table, format handling is a spec decision rather than a sprint-1 surprise. M-008 sniffs CSV-named-`.xls`, not documents | Update 002 |
| Rania's interview | NN: the client made it a condition. `RANIA-INTERVIEW.md` | §5 |
| Whether block two starts 21 Dec or 4 Jan | Scheduling only — needed by 4 December, not now | Update 002 |

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
8. The nine acceptance criteria copied verbatim, each mapped to the task that satisfies it — and each one **not met in block one** marked as such, with the date it is expected instead.
9. **The trading calendar** (§4), once the client supplies it: week start, non-trading days per branch, timezone. Every period comparison depends on it.

---

## 7. Sprint plan — cut list activated

One-week sprints, five productive days each. Day estimates are per task and summed per sprint. **Where a sprint total exceeds five days, that is stated rather than hidden.**

Cuts applied up front are marked ✂.

### 7.1 Block one — reduced to protect 20 December

§1.5 found block one 6.5 days over. The reductions below were chosen against one test: **does this figure carry weight at the quarterly branch review?** The review is about branches, so branch-level truth is protected and product-level precision is deferred.

| Task | Full | Block one | Saved | What she has until block two |
|---|---|---|---|---|
| M-007 auth — three roles + read-only guest | 1.0 | 0.5 | 0.5 | Two logins, hers and Rania's. No guest role |
| M-012 product code eras | 1.0 | — | 1.0 | **Product** figures for the two re-numbered branches carry a declared gap. Branch totals unaffected |
| M-013 matching ladder | 2.0 | 0.5 | 1.5 | Exact and alias matching only. Everything else goes to `held` — a large, honest queue rather than a tuned one |
| M-020 dashboard screens | 2.0 | 1.0 | 1.0 | One screen: branch totals over a date range, with fairness and completeness markers |
| M-023 matching health | 0.25 | — | 0.25 | Two numbers deferred |
| | | | **4.25** | |

**Why reducing M-013 is defensible rather than a corner cut.** A crude matcher produces a big `held` pile, and a big `held` pile is the system working as specified — NN-8 is "never merge below the confidence threshold", not "match everything". The alternative is tuning a matching ladder against synthetic data in week three and discovering in December that the thresholds were wrong. Instead, Rania resolves real rows during her fortnight, and those resolutions are **labelled data to tune the ladder against** in block two. The sequence is better engineering than the original order, not a concession.

**Why M-012 can wait and M-011 cannot.** Deferring product code eras makes some *product* rows `held` with a stated reason. Getting the return convention wrong (M-011) silently inverts two branches' sales — exactly the kind of plausible wrong number she would act on at the review. One is visible, the other is not. That is the whole basis for choosing between them.

### Refused reductions

| Candidate | Days | Why not |
|---|---|---|
| M-021 drill-down to raw rows | 1.5 | AC-5, and the reason she hired us. Cutting it is the one thing that makes the four-week system worthless at the review |
| M-018 completeness blocks | 2.0 | Without these the dashboard is the beautiful chart from her brief |
| M-011 return conventions | 1.0 | Two branches would look like they were over-selling, at the meeting where branches are judged |
| M-017 data quality report | 1.0 | The product |
| Keeping 4 December by dropping the dashboard | 6.75 | She would reach the review with nothing to look at, which is the one outcome Option 2 exists to prevent |

### 7.2 The phone screen — the client narrowed it

She narrowed "mobile" to **one screen, read-only: branch totals for a date range, with the fairness and completeness markers. No upload, no resolve queue, no settings.** She asked whether that is a day or a week.

**It is a day and a half, as a ranked list rather than a chart.**

| Shape | Days | Why |
|---|---|---|
| Ranked list — branch, total, change vs comparison period, completeness line under each | **1.5** | Pure presentation over M-018, which already returns every value it needs. The list is also the *better* phone design: eleven labels do not fit on a 375px axis, and a list keeps each completeness statement physically attached to its number |
| The same screen as a mirrored bar chart | ~4.0 | Mobile chart mirroring, Arabic label collision and tick density at phone width — the work the original "mobile-responsive" estimate was mostly made of |

**The original week was never this screen.** "Mobile-responsive layout" meant the whole app at phone width — the resolve queue's dense per-row actions, the grouped report tables, upload, settings, drill-down, in two directions. She does not want any of that on a phone, and removing it removes almost the entire estimate.

**One design constraint the desktop view does not have.** On a phone there is no "beside the number" for a completeness statement to sit in. If it collapses behind a tap, the figure appears without its caveat — NN-7 and the completeness rule defeated by a layout decision. **The caveat shares the block with the number, never a disclosure.** That constraint is why this is a day and a half rather than half a day, and it is not negotiable.

**Cost in her terms:** one of her seven testing days (§1.7). Recommended for block one — under the freeze, the alternative is not "mid-December", it is after the review.

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

### Sprint 3 — Dashboard, traceability, completeness · 8.5 days

| ID | Task | Days |
|---|---|---|
| M-018 | Aggregates API — **arbitrary date ranges**, comparison, completeness blocks on every figure | 2.0 |
| M-019 | `<Chart>` wrapper + RTL mirroring spike ✂ *bar and line only* | 0.75 |
| M-020 | Dashboard screens — default view answers *"which branch needs attention"* | 2.0 |
| M-021 | Drill-down: every figure traces to its raw rows | 1.5 |
| M-022 | Comparison fairness markers + branch lifecycle ✂ *opening handled; closing is a column, no UI* | 0.5 |
| M-023 | Matching health ✂ *two numbers, not a trend chart* | 0.25 |
| M-029 | **Phone view** — one read-only screen, branch totals as a ranked list, completeness in-block (§7.2) | 1.5 |

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
| ~~Mobile-responsive layout~~ | **Reinstated, narrowed and costed** — the client scoped it to one read-only screen, now M-029 in block one. See §7.2. The rest of the app stays desktop-only |
| Quantity-scope analytics | Value-based views only |
| Audit-trail screen | Reversals are logged and API-readable, not browsable |
| Branch-closing UI | The column exists; closing a branch needs a developer |
| Chart variety beyond bar and line | — |

**The reinstated cut is worth a note.** The highest-regret item on this list turned out to cost a day and a half, because we had cut a category ("mobile") rather than a requirement ("look at branch totals on a phone"). **A cut list written in categories overstates what it saves.** Every remaining row above should be re-read as a requirement before it is defended as a cut — and the client should be the one who narrows it, as she did here.

**Totals: 32.75 days** (31.25 + M-029) ≈ 6.5 weeks.

| Block | Contents | Task days | Lands |
|---|---|---|---|
| **One** | Sprints 1–2 reduced per §7.1, plus M-018 – M-022 and M-029 | 23.75 | Thu 10 Dec |
| **Freeze** | Her fortnight. Defect fixes only; nothing new lands | — | 10–18 Dec |
| **Two** | M-012, M-013 remainder, M-023, M-024 – M-028, the deferred rows above | 9.0 | after 20 Dec |

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
| **Every Friday** | **One line to the client: the date block one is currently landing on, and the number of testing days that leaves her before 20 December.** Nothing else |
| At delivery | Walkthrough of all nine acceptance criteria on a clean machine, with the unmet ones named |

**Why the Friday line exists.** Both estimation errors (§1.5, §1.6) survived because nobody re-derived a date between the moment it was written and the moment it was promised. A single number, recalculated weekly from the remaining task list and sent whether or not it has moved, makes the slip visible while it is still one day rather than six. It is the completeness statement applied to the schedule: **the figure she gets is the date, and what is missing from it.**

---

## 13. Immediate next actions

| # | Action | Owner | Blocks |
|---|---|---|---|
| 1 | ~~Decide between options A, B and C~~ | — | ✅ **Option C chosen** 8 Nov |
| 2 | Send `CLIENT-UPDATE-002.md` | Amani | Items 3–6 |
| 3 | **Confirm the hosting figure** — promised "this week" in update 001, now twice | Amani | A promise already made |
| 4 | Get the **trading calendar** — non-trading days per branch, week start, timezone | Suha | `domain/dates`, every comparison, `SPEC.md` |
| 5 | Get the **Tulkarem file** Rania calls *"not really a file"* | Rania | Whether document parsing is in scope at all |
| 6 | Ask Suha to speak to Rania herself before the interview | Suha | The quality of item 7 |
| 7 | **Interview Rania** — Sunday, live, with the files open | Amani | `SPEC.md` |
| 8 | Collect and examine the six weeks of real files | Amani | Matching thresholds, block two tuning |
| 9 | Write `SPEC.md`, with block one and block two scope separated | Amani | All development |
| 10 | Approve PR #1 | Imam | Sprint 1 |
| 11 | *(By 4 Dec)* confirm block two starts 21 Dec or 4 Jan | Suha | Block two only |

**Not before then: not one line of application code.**

**The schedule in §1.7 assumes work starts Monday 9 November.** Every working day that items 2–6 and 10 take is a day off the front of block one, and block one is already 3.75 days past four weeks. The 20 December date does not move, so this delay is spent out of Suha's seven testing days. **That is the thing to watch this week**, and if it reaches three days she hears about it immediately rather than at delivery.
