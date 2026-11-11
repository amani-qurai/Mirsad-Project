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
