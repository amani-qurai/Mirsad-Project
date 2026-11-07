# Mirsad — Discovery Questions

| | |
|---|---|
| **To** | Suha Qasem — Nakheel Retail |
| **From** | Amani |
| **Date** | 2026-11-07 |
| **Status** | Awaiting answers |
| **Blocks** | `docs/SPEC.md`, and therefore all development |

---

Hello Suha,

Thank you for being direct about the real problem. The sentence that matters most in your email is this one:

> *"I would much rather read 'we could not match these fourteen rows' than look at a beautiful chart built on data nobody checked."*

We have treated that as the core requirement, not a preference. The dashboard is the straightforward part. What we are building is a system that is honest about its own gaps.

Below are thirteen questions. **You do not have to answer all of them.** For each one we have written down what we will assume if we do not hear back, so you can simply say *"defaults are fine"* and we will proceed. Where a default is wrong, tell us only about that one.

Each question says *why it matters* — what actually changes in the system depending on your answer. We are not asking to be thorough; we are asking because these answers change the design, and changing them later is expensive.

A few of these will not have clean answers. *"I don't know, you're the expert"* is a perfectly useful reply — it tells us to go with our default and own the consequence.

---

## 1. Is there a product code in the till export?

**Q:** Do the files contain a SKU, item code or barcode column — even an inconsistent one — or is the product name the only identifier we have?

**Why it matters:** This is the single biggest question on the list. If a reliable code exists, matching products is largely solved and name-matching becomes a cross-check. If names are all we have, matching becomes the central engineering problem of the project and the review queue becomes a permanent part of your Sunday. The answer changes the time estimate substantially.

**Our default if we don't hear back:** We assume no dependable code and build name-based matching as the primary path. If a code column turns out to exist, we prefer it and use names only to detect disagreements — so the work is not wasted either way.

---

## 2. How confident should we be before merging two product names automatically?

**Q:** When a product name is similar but not identical to one we already know, how sure should the system be before deciding they are the same product without asking you?

**Why it matters:** Matching too eagerly merges two genuinely different products and corrupts your numbers silently — which is the exact failure you described last quarter. Matching too cautiously fills the review queue with obvious pairs until nobody uses it.

**Our default if we don't hear back:** Exact match first, then matched after normalisation (ignoring spacing, letter forms and diacritics), then fuzzy match above a published confidence threshold. Below that threshold we ask a human. **We never merge silently below the threshold**, and every automatic match remains visible and reversible.

---

## 3. What happens when the same file is uploaded twice?

**Q:** If a branch sends the same week twice, or sends a corrected file after you have already looked at a report, what should happen — reject it, replace the old one, or keep both?

**Why it matters:** This determines whether the system is safe to use at all. Without a rule, a double upload doubles that branch's sales and the dashboard lies. "Replace" means we must version the data and be able to tell you a number changed and why. "Reject" is safer but blocks genuine corrections.

**Our default if we don't hear back:** An identical file is detected and rejected as an exact duplicate, with a clear message. A *different* file covering the same branch and the same week is accepted as a correction: it supersedes the earlier version, the earlier version stays viewable, and the dashboard shows that the period was restated.

---

## 4. Returns, refunds and cancelled transactions

**Q:** How do returns and voided sales appear in the files — as negative amounts, as a separate transaction type, or not at all? And when you say "sales", do you mean before or after returns?

**Why it matters:** This goes straight to your core worry. If returns are mixed into the files and we count them as sales, a branch with heavy returns looks healthy. If we subtract them but you meant gross, every number is off. This is one of the most common ways a branch comparison misleads someone.

**Our default if we don't hear back:** Negative quantities or amounts are treated as returns. The dashboard shows **net sales** as the headline figure, with gross sales and returns available alongside it, so a branch cannot look better than it is.

---

## 5. What is the minimum a row needs before we can use it?

**Q:** If a row has a date, a branch and an amount but no product name — is that row still useful to you, or should it be set aside?

**Why it matters:** This defines the rejection rules, which are the substance of the data quality report you asked for. Too strict and we discard rows that would have been fine for branch totals. Too loose and incomplete rows quietly pollute the product analysis.

**Our default if we don't hear back:** A row needs **date, branch, product and amount** to enter the dataset. Missing quantity is kept with a warning. Missing any of those four is rejected with a stated reason and remains viewable in the report. Nothing is deleted.

---

## 6. Ambiguous dates — resolve once per file, or per row?

**Q:** A date written `03/04/2025` could be 3 April or 4 March. When a whole file is ambiguous, is it acceptable for us to ask you once *"this branch's file appears to use day/month — is that right?"* and then remember that answer for that branch?

**Why it matters:** Asking per row is unusable — one file could produce hundreds of questions. Asking once per file is practical, but it means we apply one human answer to many rows, so if the answer is wrong it is wrong at scale. Remembering it per branch removes the question permanently but assumes the branch's export settings never change.

**Our default if we don't hear back:** We infer the format from the unambiguous dates inside each file. If a file contains no disambiguating date, we flag the file, ask once, remember the answer for that branch, and re-check it on every later upload. **We never guess a date format silently**, and flagged rows are excluded from the dashboard until resolved rather than estimated.

---

## 7. "Compared with last month" — compared how?

**Q:** Does this mean the same calendar month, or the same number of days? And if a branch was closed for part of either period, should the comparison still be shown?

**Why it matters:** A 31-day month against a 28-day month shows a fake 10% rise. A branch closed for three days shows a fake decline — and that is precisely the kind of number that nearly cost you a branch. Handling it properly means the system needs to know when a branch had no trading data and say so.

**Our default if we don't hear back:** Same calendar month by default, with a per-day average shown beside it. When either period contains days with no data for that branch, the comparison is marked as **not like-for-like** on the chart itself, not in a footnote.

---

## 8. Who resolves the uncertain cases, and can a decision be undone?

**Q:** Will Rania be the one answering the system's questions, or should branch managers resolve their own? And if she matches two products by mistake, should she be able to reverse it?

**Why it matters:** This decides the accounts and permissions, and whether every decision needs an audit trail showing who made it and when. Letting eleven branch managers resolve matches is faster but means eleven people shaping your product list. It also decides what you see: whether you can review Rania's decisions or only their results.

**Our default if we don't hear back:** Three roles — **you** with read access to everything plus a log of every decision made; **Rania** as the one person who resolves uncertain cases; and a **read-only guest** account for demonstrations. Every resolution is reversible, and every resolution records who made it and when.

---

## 9. Are the eleven branches fixed, and are their names consistent?

**Q:** Will branches open or close during the year? And does each branch write its own name the same way every week, or does that vary too?

**Why it matters:** If branch names vary the same way product names do, we need the same matching and review machinery for branches. More importantly, if a file arrives from an unrecognised branch name, the dangerous outcome is the system quietly inventing a twelfth branch — which would split one branch's sales across two and look exactly like a sales drop.

**Our default if we don't hear back:** Branches are set up once as known records, each able to carry several spellings. A file from an unrecognised branch name is **held for a human to map** and never auto-created. Opening or closing a branch is supported and recorded, so comparisons can account for it.

---

## 10. File formats, encodings and size

**Q:** Are the exports CSV, Excel, or a mix? Roughly how many rows does one branch send in a week — hundreds, or tens of thousands?

**Why it matters:** This decides how files are read and whether uploads need to be processed in chunks with a progress indicator. It also affects Arabic text: Excel exports and CSV exports mishandle Arabic in different ways, and the fix for each is different.

**Our default if we don't hear back:** We support CSV and Excel, detect the text encoding automatically (including the older Windows Arabic encoding that till systems often produce), and size the system for up to roughly 50,000 rows per file.

---

## 11. Currency, tax and discounts

**Q:** Are all amounts in one currency? Are they before or after VAT? And do the files show line discounts separately?

**Why it matters:** Your report is almost entirely numbers, so this must be right from the first version — if the amounts mean something different from what the dashboard claims, nothing above it can be trusted. If VAT is inconsistent between branches, two branches with identical sales will not agree.

**Our default if we don't hear back:** One currency, Saudi riyals, formatted for the viewer's language. Amounts are treated as the final amount paid, VAT included. If we find branches that disagree about VAT, we raise it as a data quality finding rather than silently adjusting.

---

## 12. How do you want to receive the data quality report?

**Q:** Is it enough to read the report inside the system, or should it also be downloadable — or emailed to you and Rania on Sunday?

**Why it matters:** Reading it in the system is included. A download is a small addition. Email is a genuinely separate piece of work — a scheduler, a mail service, and a decision about sending your business data through a third party — and it would come out of the same budget as dashboard work.

**Our default if we don't hear back:** The report is read inside the system and downloadable as Excel or CSV, including the full list of rejected rows with reasons. **No email in the first version**, kept as an obvious later addition.

---

## 13. Where will this run, and who logs in?

**Q:** Should this live on a machine in your office, or be hosted online so branch managers can reach it? And roughly how many people will have accounts?

**Why it matters:** Hosting it online brings in domains, certificates, backups and ongoing cost — real work and a monthly bill. Running it in your office is simpler and keeps your sales data on your own premises, but then only people on that network can use it.

**Our default if we don't hear back:** Delivered as a self-contained package that starts with a single command on one machine, with accounts for you, Rania and a read-only guest. Hosting it online is a later step that does not require rebuilding anything.

---

## What we are assuming without asking

So that the list stays short, we have decided these ourselves. Correct any that are wrong:

- The interface is **Arabic and English**, fully mirrored, with every number, date and currency formatted for the chosen language.
- Original files are **kept permanently**. Every figure on the dashboard can be traced back to the exact rows it came from.
- Uploads are **manual** — no direct connection to the till system in this version.
- **One business.** No support for a second company sharing the system.
- Reporting is **weekly**, matching your Sunday cycle. No live updating.
- No forecasting, no budgets, no stock levels, no staff or payroll data.

---

## What we need in order to start

Two things, in this order:

1. **The real files.** Rania's few weeks of actual exports matter more than the answers above. We would rather see the mess than have it described — and as you asked, we will not be polite about it.
2. **Your answers**, or simply *"the defaults are fine."*

Answers to **1, 3, 4, 5 and 6** change the structure of the system and are the ones that would be expensive to revisit later. The rest can be decided while we build.

Thank you,

**Amani**
