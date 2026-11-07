# Impact of the client's answers

| | |
|---|---|
| **Status** | Proposed — awaiting reviewer approval |
| **Date** | 2026-11-07 |
| **Source** | [`ANSWERS.md`](ANSWERS.md) — Suha Qasem, 7 November 2026 |
| **Blocks** | `docs/SPEC.md` |

---

## 1. Headline

Eight of thirteen defaults were confirmed. The other five, plus one correction the client volunteered, change the design — and one of them changes it in a way that matters more than the rest.

Three things she told us were not answers to our questions at all. They were corrections:

1. **The currency is wrong in our committed documents.** We assumed Saudi riyals. Nakheel Retail is in the UAE and trades in dirhams.
2. **Our rule for an unusable row was too strict**, and would have silently produced the exact failure this project exists to prevent.
3. **We asked thirteen questions about her data and none about her decisions.** She is right, and she answered the question we should have asked.

---

## 2. Where we were wrong

Recorded plainly, because a correction that is not written down gets made twice.

### 2.1 Currency — a factual error, already committed

The `mirsad-conventions` skill stated Saudi riyals and the `ar-SA` locale in its formatting examples, and `QUESTIONS.md` offered "Saudi riyals" as our default. It is **AED**, and the locale is `ar-AE` / `en-AE`. This was a default we invented and never flagged as a guess — unlike the other twelve, where the question itself admitted we were assuming.

(`ADR-0001` happens not to name a currency, so it needs no correction. Worth stating precisely: a document about our own mistakes is worth less if it is imprecise about them.)

The skill file is what the executor reads before writing any formatting code, so this would have reached the client's screen. Corrected in this change; the question document keeps the original wording, because it is a record of what was sent.

### 2.2 The minimum row — too strict, and wrong in the dangerous direction

We said a row needs date, branch, product and amount, and rejected it otherwise. She said:

> *"A row with a date, a branch and an amount but no product name is still useful to me. It belongs in that branch's total. Most of my decisions are at the branch level, and losing those rows would make branch totals quietly wrong, which is the failure you are trying to prevent."*

She is right, and the mistake is worse than it looks. Our rule would have **under-reported branch totals with no visible symptom**. A branch would appear to be selling less than it was — which is precisely the thing that nearly made her close a branch. We built a rule that reproduced the original failure.

The fix is not a looser threshold. It is a change to the model, in §3.1.

### 2.3 Returns — our rule would have inverted two branches

We assumed negative amounts. Two branches record a return as a **positive row with `RTN` in the notes column**. Under our rule those two branches would have counted returns as sales and looked healthier than they are — the mirror image of §2.2, and equally invisible.

### 2.4 The discovery gap

> *"You asked thirteen careful questions about my data and not one about what I do with it."*

Correct. The questions were about correctness and said nothing about purpose. She filled the gap herself — see §5 — but this is the kind of omission that produces a technically flawless dashboard nobody opens.

---

## 3. New design concepts

Four ideas the answers force into the design that were not in `ADR-0001`.

### 3.1 Row scope — every figure declares its own completeness

**The change.** A row is no longer valid or invalid. It is valid *for some analyses and not others*. Each row carries the set of dimensions it may legitimately contribute to:

| Scope | Requires |
|---|---|
| `total` | date, branch, amount |
| `product` | the above, plus a resolved product |
| `quantity` | the above, plus a parseable quantity |

A row with no product is in scope for `total`, out of scope for `product`. It is counted in the branch total and excluded from the product breakdown.

**The consequence, which is the important part.** Every aggregate the API returns carries a *completeness statement* alongside the number:

> This branch's total includes 34 rows with no product, worth AED 2,100.

Rendered next to the figure, not in a footnote. The client wrote the sentence herself; we are implementing her wording.

**Why this is the most significant change in the document.** Acceptance criterion 5 says any figure must be traceable to its rows. This extends it: a figure must also state **what it is missing**. Traceability answers *where did this number come from*; completeness answers *what is not in it* — and the second question is the one that nearly cost her a branch.

This does not replace the `warning` / `held` / `rejected` model. It is a second axis alongside it: severity says what happened to the row, scope says which figures may use it.

### 3.2 Product codes have eras

`ITEM_NO` exists but is not an identifier. After the till update, two branches **restarted numbering from 1**, so code `0412` is a bath mat in one branch, a kettle in another, and something else again in that same branch's older files.

| Rule | |
|---|---|
| A code never identifies a product on its own | It is scoped to `(branch, valid_from, valid_to)` |
| Code agrees with name | Use the code, record that both agreed |
| Code and name disagree | **`held`** — the client asked for this explicitly |
| Code falls near a branch's renumbering boundary | **`held`** — we cannot know which era it belongs to |

Detecting the boundary matters: the same code attached to two unrelated names across a date gap is the signal. We find it or we ask — we never pick one.

> *"A code and a name pointing at different products is exactly the kind of thing I would want to see rather than have resolved quietly."*

### 3.3 Return conventions are per branch, and silence is suspicious

Each branch gets a `return_convention`: `negative_amount`, `note_flag`, or `unknown`. Inferred from the data, confirmed by a human once, stored, and **re-checked on every upload** — the same treatment as date formats, for the same reason.

While a branch's convention is `unknown`, its net sales figure is marked incomplete rather than presented as fact.

One addition of our own: **a branch reporting zero returns across a whole period is itself a finding.** Every retail branch takes returns. Silence means we are failing to recognise its convention, and that failure makes the branch look better than it is. Absence of evidence is the symptom we should be watching for.

### 3.4 Branches have lifecycles

A branch opened eight months ago, and one may close next year.

- `opened_at` and `closed_at` on every branch
- A comparison period is intersected with the branch's open window
- If the comparison period predates `opened_at`, **there is no comparison** — the chart says so instead of showing −100%

> *"If the dashboard shows it as a catastrophic decline against a period when it did not exist, that is precisely the broken comparison I am trying to escape."*

---

## 4. Answer-by-answer impact

| # | Answer | Impact | Cost |
|---|---|---|---|
| 1 | `ITEM_NO` exists, untrustworthy, two branches renumbered | §3.2 code eras; new `held` codes | **+1.0 d** |
| 2 | No threshold number; wants weekly auto-vs-asked counts | New metric on the dashboard; queue depth tracked over time | **+0.5 d** |
| 3 | Confirmed; corrections ~monthly | None — default already covered it | — |
| 4 | Two branches use `RTN` note, not negatives; net sales | §3.3 return conventions; notes column mapped | **+1.0 d** |
| 5 | Missing product should still count in branch total | §3.1 scope + completeness | **+1.5 d** |
| 6 | Confirmed; **formats do change** — re-ask, never assume | Default held; add `DATE_FORMAT_CHANGED` | — |
| 7 | Doesn't think in calendar-vs-equal-days; wants fairness shown on the chart | Default held | — |
| 8 | Rania only; reversible; audited | Default held | — |
| 9 | New branch 8 months old; one may close | §3.4 lifecycle | **+0.5 d** |
| 10 | Mixed Excel/CSV; one CSV named `.xls`; few thousand rows | Sniff content, never trust the extension | **+0.25 d** |
| 11 | **AED not SAR**; one branch pre-VAT; discounts inconsistent | Correct the currency; VAT and discount basis per branch, reported never adjusted | **+0.5 d** |
| 12 | Confirmed | — | — |
| 13 | Office first, **but she checks from her phone**; must be hostable later without rebuild; wants a cost | Mobile is now a requirement, not a nicety; deployment portability stated; produce a cost estimate | **+1.25 d** |
| — | Any date range, not weeks | Aggregations take arbitrary `(from, to)` — free now, two days if retrofitted | — |

**Gross: ≈ 6.5 days. Net: ≈ 5 days**, since scope eligibility replaces simpler validation work already planned.

---

## 5. What she actually uses it for

The answer to the question we failed to ask:

> *"I decide what to stock more of, which branch needs attention, when to run a promotion, and occasionally whether a branch is worth keeping. Those decisions are monthly and quarterly, not weekly."*

Four consequences for the dashboard:

1. **The default view answers "which branch needs attention"** — not "here is a chart of everything".
2. **Monthly and quarterly are the natural ranges**, with weekly available. Weekly is how the *files arrive*, not how she *looks*.
3. **"What to stock more of" is a product-level question**, which makes the product breakdown's completeness statement (§3.1) load-bearing rather than decorative.
4. **"Whether a branch is worth keeping" is the decision that nearly went wrong.** Every figure feeding it carries a fairness marker and a completeness statement, or it is not fit for that decision.

---

## 6. New and changed reason codes

Changed:

| Code | Was | Now |
|---|---|---|
| `ROW_MISSING_PRODUCT` | `rejected` | **`warning`**, scope `{total}` — counted in branch totals, excluded from product views |
| `BRANCH_CLOSED_IN_PERIOD` | — | renamed `BRANCH_NOT_OPEN_IN_PERIOD`, covering before opening and after closing |
| `PRODUCT_NAME_CONFLICT` | — | renamed `PRODUCT_CODE_NAME_CONFLICT`, now explicitly `held` |

New:

| Code | Severity | Meaning |
|---|---|---|
| `PRODUCT_CODE_EPOCH_AMBIGUOUS` | `held` | Code falls near a branch's renumbering boundary |
| `ROW_RETURN_BY_NOTE` | `warning` | Return detected via the notes flag, not a negative amount |
| `BRANCH_RETURN_CONVENTION_UNKNOWN` | `held` | How this branch records returns is undetermined |
| `BRANCH_NO_RETURNS_IN_PERIOD` | `warning` | No returns at all — probably an unrecognised convention |
| `BRANCH_VAT_BASIS_EXCLUSIVE` | `warning` | This branch exports pre-VAT; not comparable without adjustment |
| `BRANCH_VAT_BASIS_INCONSISTENT` | `warning` | Branches disagree on VAT basis — a dataset-level finding |
| `ROW_DISCOUNT_BASIS_UNKNOWN` | `warning` | Discount may or may not already be deducted |
| `FILE_EXTENSION_MISMATCH` | `warning` | Content and extension disagree, e.g. CSV named `.xls` |
| `DATE_FORMAT_CHANGED` | `held` | Inferred format differs from this branch's last upload — ask again |

**None of the VAT or discount codes adjust anything.** They report.

> *"Do not adjust it silently — if you corrected it quietly I would never know my own data was inconsistent, and I would want to fix it at the source."*

---

## 7. Hosting

She asked what putting it online would cost per month, and asked us not to build anything that would need rebuilding to get there.

**Portability requirements, from now on:** all configuration through environment variables with no host assumptions; a stateless API; uploads and the database as the only persistent state; no `localhost` baked into anything; HTTPS-ready behind a reverse proxy.

The stack in `ADR-0001` already satisfies this. It is now a stated constraint rather than a happy accident.

**Cost: roughly USD 25–50 per month** for a small virtual server running the existing Compose stack, a domain, and automated backups — with managed Postgres at the upper end. **This is an order-of-magnitude figure and must be confirmed against live pricing before it is quoted to her.** Recorded as an action, not an answer.

---

## 8. Still required before `SPEC.md`

> *"Talk to Rania before you write the specification."*

This is a condition, not a suggestion, and it is correct. Rania is the only person who will use this weekly, and if the resolve queue is tedious she goes back to the spreadsheet and everything else stops mattering.

[`RANIA-INTERVIEW.md`](RANIA-INTERVIEW.md) holds the questions. **`SPEC.md` is not started until that conversation happens.**

Also outstanding: six weeks of real files, arriving Sunday. Thresholds tuned on synthetic data and then met with real exports is still the largest rework risk in the project, and now we know at least two branches will break naive rules.

---

## 9. Schedule

The answers add about **five net days**.

Acting on that prompted a re-estimate of every task rather than of phases, and it found a larger problem that the answers did not cause: **the original four-week figure was never sound.** Summed task by task, the work is ≈ 31 days after every available cut — about six weeks.

The revised numbers, the three options, and the decision taken are in [`PROJECT-PLAN.md`](../PROJECT-PLAN.md) §1.

> **Superseded on 2026-11-08.** This section originally ended: *"four weeks is being held, the cut list is spent immediately, and four weeks therefore delivers the engine and a minimal dashboard rather than the full nine-point acceptance list."*
>
> That sentence was wrong, and the numbers to disprove it were in the same plan. Summed, the four-week list came to 26.5 days against 20 available. The client chose Option C, and the first block now lands **10 December** with its arithmetic shown — [`PROJECT-PLAN.md`](../PROJECT-PLAN.md) §1.5 for the error, §1.7 for the dates, §7.1 for what was reduced.
>
> The original wording is quoted rather than deleted, because a document recording our own mistakes should not quietly acquire a third version of them.

One cut in the original list is no longer available. Comparison-period charts were item 2, and answers 7 and 9 are entirely about comparison fairness — cutting it would remove the thing that nearly cost the client a branch. A cut list written before the client answers is a guess.

---

## 10. Decisions needed

| # | Decision | Needed by |
|---|---|---|
| 1 | Five weeks, or four with the cut list activated now | Before `SPEC.md` |
| 2 | Approve the scope/completeness model in §3.1 — it touches every table and every aggregate | Before `SPEC.md` |
| 3 | Schedule the conversation with Rania | Before `SPEC.md` |
| 4 | Confirm hosting pricing before any figure is given to the client | Before delivery |
