# Mirsad — Decisions

The client thread closed on 9 November 2026. From then on, when a question comes up that the client has not answered, **the developer decides it, writes it here with the reason, and keeps building.** A written assumption that turns out wrong costs an hour to change; a week of waiting costs a week.

Each entry says what was decided, why, and what would make us revisit it. Newest last. An entry is never deleted: if one is reversed, a later entry says so and points back.

| | |
|---|---|
| **Owner** | Amani |
| **Reviewer** | Imam |
| **Source of the rule** | Imam's closing letter, 9 Nov 2026 |

---

## D-001 — The SPEC.md gate is waived

**Decided:** 9 Nov 2026 · **By:** Imam, recorded by Amani

CLAUDE.md said no application code until `docs/SPEC.md` was approved. Imam's closing letter instructs building to start now, from the plan's task IDs, without a specification document. `SPEC.md` was never written.

Scope is now defined by three things together: the task list in `PROJECT-PLAN.md` §7, the client's own words in `discovery/`, and this file. Where they disagree, the newer entry here wins, then the client's words, then the plan.

**Revisit if:** a reviewer finds a task being built against two incompatible readings of the scope. Then write the missing part of the spec, not the whole document.

## D-002 — Delivery dates, final

**Decided:** 9 Nov 2026 · **By:** Imam

| | Date |
|---|---|
| Block one → Rania | **Sat 12 Dec** |
| Block one → Suha | **Tue 22 Dec** |
| Freeze, then review | review **Sun 27 Dec** |
| Block two | from **Mon 4 Jan** |
| Phone view (M-029) | block two, January |

These replace the 5 / 15 / 20 December dates in `PROJECT-PLAN.md` §1.11 and §7. The week lost waiting on the client thread is absorbed here and is not counted against build time.

## D-003 — Tulkarem is read, marked and excluded — not left unread

**Decided:** 9 Nov 2026 · **By:** Imam

**Reverses** `PROJECT-PLAN.md` §1.10 and the client's reply 003 §4, which said not to ingest the hand-typed Word files in block one.

The closing letter says: ingest, mark, exclude from rankings, keep readable. Its first build step includes a `.docx` reader. Tulkarem's rows therefore enter the system as `unverified_source` (M-034): readable in drill-down, counted in the data quality report, and **never** in a ranking or comparison.

**Why this is the safer side of the reversal:** a file that is read and marked can be shown to the owner with its gaps named. A file that is never read is a silent hole in the chain's total.

**New dependency:** `python-docx`, which ADR-0001 did not list. It only reads tables and paragraphs; nothing else in the stack changes.

## D-004 — M-035 (the retrospective) runs after block one

**Decided:** 9 Nov 2026 · **By:** Imam

`PROJECT-PLAN.md` §1.15 scheduled it before Sprint 1. The closing letter moves it to after block one is delivered. The review notes have arrived and are stored with the other client files (D-006).

## D-005 — The client thread is closed; update 004 is superseded

**Decided:** 9 Nov 2026 · **By:** Imam

The closing letter is the last client document. It states there would be no update 004; `discovery/CLIENT-UPDATE-004.md` exists and was recorded as sent on 11 Nov. Both are kept as written. **Where they disagree, the closing letter wins** — in particular on the Tulkarem decision (D-003) and on when M-035 runs (D-004).

No further questions go to Suha or Rania. Open questions are decided here.

## D-006 — Real client files live in `/data/`, never in git

**Decided:** 9 Nov 2026 · **By:** Amani

The six weeks of exports and the review-notes workbook are unpacked into `/data/` at the repository root, which `.gitignore` excludes. `.gitignore` also gained `*.docx`, because the Tulkarem files would otherwise have been committable (non-negotiable 11).

Tests never use these files. Test fixtures are synthetic and generated in the test itself.

## D-007 — The Rania meeting is recorded as requirements, not as a transcript

**Decided:** 9 Nov 2026 · **By:** Amani

The meeting notes describe manual corrections Rania has made for years that her employer does not know about. This repository is public. `discovery/RANIA-MEETING.md` records **what the system must do** because of those facts — and the file-by-file inventory — but not her words about her employer or her own habits.

## D-008 — The two Jenin week-03 files are byte-identical

**Decided:** 9 Nov 2026 · **By:** Amani

`week-03/jenin-2026-10-11.csv` and `jenin-2026-10-11-FINAL.csv` have the same SHA-256. The closing letter describes the second as a fuller re-export of the same day, which would differ.

**Decision:** treat the pair as what it is — an exact duplicate upload (`FILE_EXACT_DUPLICATE`). The restatement path (`FILE_PERIOD_RESTATED`) still gets built and tested, against synthetic fixtures, because it is in M-010's scope regardless.

**Revisit if:** a corrected Jenin file turns up. Asked of Imam; not blocking.

## D-009 — Readers return text, not typed values

**Decided:** 9 Nov 2026 · **By:** Amani · **Task:** M-008

Every reader returns the same shape: a header, and rows of cells **as the file presented them**, as strings. No date parsing, no number parsing, no encoding repair at this stage.

**Why:** the hard decisions — is `10/03/2026` the 3rd of October or the 10th of March, is `٣٤٦٫٠١` a number — belong to `domain/dates` and `domain/numbers`, where they can be held when ambiguous. A reader that let pandas infer types would make those decisions silently, before anything could flag them. It is also what keeps the raw row intact for drill-down (non-negotiable 7).

Excel cells that are stored as numbers are written out with Python's shortest round-trip form (`346.01`, not `346.0100000001`). Excel cells stored as real dates are written as ISO `YYYY-MM-DD` and the conversion is recorded on the row. None of the 67 current files contain any.

## D-010 — Encodings: UTF-8, then Windows-1256, otherwise refuse

**Decided:** 9 Nov 2026 · **By:** Amani · **Task:** M-008

A text file is decoded as UTF-8 (a BOM is noted and stripped). If that fails, it is decoded as Windows-1256 — but only accepted if its non-ASCII characters are Arabic. Anything else is `FILE_ENCODING_UNDETECTED`, rejected, never guessed.

Windows-1256 decodes almost any byte sequence without error, so "it decoded" is not evidence it decoded correctly. The Arabic check is what stops a Latin-1 file becoming plausible-looking nonsense.

## D-011 — Jenin's till lost characters before the file reached us

**Decided:** 9 Nov 2026 · **By:** Amani

Jenin's export is Windows-1256, which has no Arabic-Indic digits. Product names that contained them arrive with literal `?` in their place (`مقلاه ?? سم`). The information is gone at source; no decoder recovers it.

**Decision:** the reader keeps the `?` exactly as received. Product matching (M-013) must treat `?` as an unknown character, not a literal — so `مقلاه ?? سم` can be *held* against `مقلاة 28 سم`, never auto-merged. Recorded here so it is not "fixed" quietly in the reader.

## D-012 — Header mapping: known names only, every column accounted for

**Decided:** 10 Nov 2026 · **By:** Amani · **Task:** M-008

Each branch's column names map to eight standard fields: transaction id, date, product code, product name, quantity, amount, discount, notes. The table of known names in `backend/app/pipeline/headers.py` holds **exactly the headers seen in the six weeks of real files**, nothing guessed beyond them.

- Headers are compared after case, spacing and underscores are ignored. No Arabic letter normalisation is applied — exact names have been enough, and any Arabic rule belongs in `domain/arabic` (NN-5).
- **A column nobody recognises holds the file** (`FILE_HEADERS_UNRECOGNISED`) rather than being dropped. A new column can change what the others mean — Jenin's separate discount column is exactly that case. A person names the column once and the answer is remembered for that branch.
- **Date and amount are required.** Product, code, quantity and transaction id are not: Tulkarem's Word table has no id and no code, and still has to be read (D-003). What a missing field means for each row is validation's decision (M-009), not the mapper's.
- **`AMOUNT_EXVAT` marks the file's amounts as pre-VAT.** The mapping records it so the data quality report can say so. Nothing multiplies by 1.16 at this stage, or silently at any stage.

**Result on the real files:** all 67 branch files map completely. The six Qalqilya files are marked pre-VAT. The review-notes workbook is held, correctly, because it is not a branch export.

**Revisit if:** a till changes its export headers. That arrives as a held file with the unknown column named, which is the intended behaviour.

## D-013 — A repeated transaction id is a duplicate only when the whole row repeats

**Decided:** 10 Nov 2026 · **By:** Amani · **Task:** M-009

The error catalogue said *same transaction id twice in one file → rejected*. The real files say otherwise: **Ramallah has 102 ids that appear more than once inside the same weekly file, and in every case the rows are different sales** — different product, date and amount. The till restarted its numbering. Applying the catalogue rule would have deleted 110 real Ramallah sales, at the branch whose figures matter most at the review.

- **Same id, every cell identical** → `TXN_DUPLICATE_WITHIN_FILE`, rejected, pointing at the line it copies. None exist in the six weeks; the rule stays because a re-sent line is a real possibility.
- **Same id, different content** → `TXN_ID_REUSED`, a **warning** on every row involved. All are kept and counted. The row is identified by its content, not its id.

This updates the design intent in `.claude/skills/mirsad-conventions/references/error-codes.md`. Repeats *across* weeks for the same branch (Salfit and Ramallah both restarted at 1) are M-010's job.

## D-014 — The first rejection report checks presence only

**Decided:** 10 Nov 2026 · **By:** Amani · **Task:** M-009

The report runs before any cleaning, so it judges only whether a value is **there**, not whether it is **valid**. Whitespace counts as empty.

| Missing | Outcome | Why |
|---|---|---|
| Date | rejected | Cannot be placed in a week |
| Amount | rejected | Nothing to count |
| Product name | warning, scope `{total}` | Counted in the branch total, left out of product figures. A code without a name is still missing: codes never identify a product alone (M-012) |
| Quantity | warning | Amount still counts; left out of quantity figures |
| Transaction id (column present, cell empty) | warning | Kept, identified by content |

A file with **no** id column at all — Tulkarem — gets one file-level fact (`fields_absent`), not a warning on every row.

Parsing dates and amounts adds its own findings later (M-005, M-006). Amounts are therefore **not totalled** in this report yet: summing text would mean parsing it here, outside `domain/numbers`.

**In a batch, the first of two byte-identical files is kept** and the second is `FILE_EXACT_DUPLICATE`. Files are taken in name order, so of the Jenin week-03 pair, `…-FINAL.csv` is the one kept. The rows are identical, so the totals do not depend on which.

**Result on six weeks:** 23,233 rows in · 23,080 kept · 153 rejected (86 no date, 67 no amount) · 774 outside product figures · 212 Ramallah rows with reused ids, all kept · 0 held (nothing in this stage can be held; dates and matching will add them).

## D-015 — How day/month order is decided, and the file name's part in it

**Decided:** 10 Nov 2026 · **By:** Amani · **Task:** M-006

A value like `10/03/2026` is decided once per file, from evidence, in this order:

1. **The value itself.** `30/09/2026` has one valid reading; `10/10/2026` reads the same both ways.
2. **The rest of the file.** If every value that *can* only be read one way agrees, the ambiguous ones follow it. `DATE_FORMAT_INFERRED`, warning, evidence `file`.
3. **The week the file covers**, taken from its name (`<branch>-<YYYY-MM-DD>…`, the date being the week's first day). Only one reading of `10/04/2026` falls in 4–10 October. Evidence `week`.
4. **Otherwise held**: `DATE_FORMAT_AMBIGUOUS`, with both candidate dates.

If the file and the week point different ways for a value, that value is **held**, not chosen.

**Why the week is needed:** 4–10 October has no day above 12, so the week-02 files of every branch carry no evidence of their own. Without step 3, about 2,000 rows a year in weeks like that would sit in the held queue for a decision the week already answers.

**Why the name is acceptable evidence:** it is used *only* to choose between two readings the value already allows. It never moves a date, and a date outside the week is held (`ROW_DATE_OUT_OF_RANGE`), not corrected. A file whose name does not follow the pattern is still read; its ambiguous dates are held.

**Two-digit years** (Salfit, `28/09/26`) are read as 20yy. A year-first reading of a two-digit value is not considered: no till writes one, and the week check would catch it.

**Result on six weeks:** every date in every file falls inside its own week. Nothing unparseable, nothing out of range, nothing ambiguous left over.

## D-016 — A change in a branch's date format holds the file

**Decided:** 10 Nov 2026 · **By:** Amani · **Task:** M-006

Imam's letter asks for *"a loud failure when a branch's format changes."* When a branch's file is read in a different day/month order from its previous file — or a single file contains both orders — the file gets `FILE_DATE_FORMAT_CHANGED`, **held**. Every usable row in it waits for one confirmation; the rows are not rejected and nothing is re-read.

Held rather than a warning because the risk is exactly the one this project exists for: in the week a till switches, an ambiguous date read the old way is a plausible wrong number. One click from Rania is cheap; a silently mis-dated week is not.

**Result on six weeks:** Ramallah reads month-first in weeks 1–3 and day-first from week 4, matching the closing letter. Week 4 (18 Oct, 495 rows) is held. No other branch changes.

**Known noise, kept on purpose:** 8,236 rows carry `DATE_FORMAT_INFERRED`, so "rows with warnings" is dominated by it and the 774 missing-product rows are harder to see. The per-row code stays because drill-down must show how each date was read. **Revisit in M-017**: the data quality screen should state the inference once per file and list the rows behind it, rather than count it beside warnings that need attention.

## D-017 — Three normalisation rules added from the real names

**Decided:** 10 Nov 2026 · **By:** Amani · **Task:** M-004

The rule table in `.claude/skills/mirsad-conventions/references/arabic-normalisation.md` was written before the files arrived. Applied to the 116 real product spellings, it had two defects and one gap:

- **A decimal point was deleted as punctuation**, so `1.5` became `15` — a 1.5 L jug and a 15 L box would share a key. A decimal mark between digits (`.`, `,`, `٫`) is now kept, as `.`.
- **`×` was deleted but `x` kept**, so `120×170` never matched `120x170` — the same rug, written both ways. `×` between digits now becomes `x`.
- **`6pc` vs `6 PC`, `1.7L` vs `1.7 L`**: a space is now inserted wherever digits meet letters.

The rule table is updated with all three and their reasons. No existing rule was weakened.

**Result:** 116 spellings → 96 comparison keys. Of the 20 merges, every one is the same product; **no key appears under two product codes.** The remaining 96 keys cover 25 products, mostly because Arabic and English names are never matched to each other — by design, that is a person's decision, made once.

## D-018 — Block-one matching: known spellings match, everything else is new or a question

**Decided:** 10 Nov 2026 · **By:** Amani · **Task:** M-013 (reduced, per `PROJECT-PLAN.md` §7.1)

No fuzzy scoring in block one. A spelling matches only if it is already known — exactly, or by its `domain/arabic` key. Otherwise:

- **It has a candidate** (its product code belongs to a known product, or the same spelling is already waiting) → **held**, `PRODUCT_MATCH_UNCONFIRMED`, with the candidate as a one-click suggestion.
- **It has no candidate at all** → **a new product**, `PRODUCT_NEW`. Visible and fixable; a wrong merge would not be.
- **Its name and code point at different products** → **held**, `PRODUCT_NAME_CONFLICT`.

**The code suggests; it never decides.** A name the catalogue does not know is never filed under a product because of its code (product code eras, M-012). **Lost characters** (Jenin's `?`, D-011) match only a spelling a person has confirmed, never by key, and never create a product.

**One answer per spelling.** The resolve queue lists spellings, not rows; confirming one resolves every row with it, in every later file. A person's answer about a name/code pairing also accepts that pairing.

**A product question does not remove a sale from its branch's total.** This changes how "held" works, and it is the important part of this entry. CLAUDE.md says held rows are "excluded, and counted out loud." Applied to the whole row, an unconfirmed spelling would remove about two thirds of week one's sales from the branch totals — the plausible wrong number Rania is most afraid of. So each held finding withholds the row only from the figures it affects:

| Held because of | Withheld from |
|---|---|
| The date (ambiguous, out of the week) | everything |
| The product (unconfirmed, conflict) | product and quantity figures; **still in the branch total** |

The row is still counted out loud as held. Its completeness statement reads, for example, *"this branch's total includes 412 rows whose product is not yet confirmed."* The quantity scope now also requires the product scope, as the error-code reference always said.

**Result on six weeks:** 25 products, one per code, none invented. **78 spellings** wait for a person, every one with a single suggestion, and every suggestion is correct on inspection. No conflicts. 22,585 rows count in branch totals; 7,816 in product figures before any answers. **Answering the 78 questions** — simulated by accepting each suggestion — **brings product figures to 21,829 rows and leaves 0 questions**, with still 25 products.

**Revisit in block two:** Rania's 78 answers are the labelled data the fuzzy thresholds will be tuned against.

**Display names** are the first spelling seen (`ELEC KETTLE 1.7L`, `Glass Jug 1,5 L`). They are defaults a person can rename; nothing depends on them.

## D-019 — Amounts: Decimal, read with certainty or held

**Decided:** 10 Nov 2026 · **By:** Amani · **Task:** M-005

Every amount in the six weeks is plain (`457.93`, `-570.65`, `647`). The parser still reads what a till or a typed sheet can produce — Arabic-Indic digits, `٫` and `٬`, `1,234.50` and `1.234,50`, a currency word or `₪` at either end, a minus sign, a trailing minus, accounting brackets — because a format change arrives without notice.

- **A lone comma before exactly three digits (`1,500`) is ambiguous**: one and a half, or fifteen hundred. `ROW_AMOUNT_AMBIGUOUS`, **held** from totals with both candidates. Never guessed.
- **Anything else unreadable** → `ROW_AMOUNT_UNPARSEABLE`, rejected, with the value.
- **An unreadable quantity** is a warning; the amount still counts, the row leaves quantity figures.
- **Money is `Decimal`**, and is written to JSON as text, never as a float.

**Every count in the report now has its worth beside it**: in totals, held from totals, rejected, and in totals but outside product figures. *"This branch's total includes 34 rows with no product, worth ILS 2,100"* can now be written from the report.

**Result on six weeks:** nothing unreadable or ambiguous. ILS 9,663,356.01 in branch totals before returns and VAT are handled; ILS 205,860.42 held from totals (Ramallah week 4); ILS 38,336.11 in rejected rows.
