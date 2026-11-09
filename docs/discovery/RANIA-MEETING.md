# Rania — meeting record

| | |
|---|---|
| **Who** | Rania Haddad, accountant at Nakheel Retail — the only weekly user |
| **When** | 9 November 2026, 10:00–11:40 |
| **Present** | Rania, Amani. Suha deliberately not in the room |
| **Replaces** | `RANIA-INTERVIEW.md` (the guide; this is the result) |
| **Recorded as** | Requirements, not a transcript — `DECISIONS.md` D-007. The repository is public |

---

## The one sentence

> *"I do not mind the hours. I mind that I cannot prove any of it."*

She can produce last October's number for any branch. She cannot produce **what was done to get it**. Mirsad's job is to make that second thing exist without her having to keep it.

## Her Sunday today

About **six and a half hours**, every week, for four years: download eleven attachments, look at each one before touching it, paste branch by branch into a master workbook converting dates by hand, then reconcile product names — **the longest step, and the one nobody sees** — then type Tulkarem in from Word, then build the report and check it against the previous week.

## Corrections made by hand, today, that the system must make visible instead

Each of these is currently done correctly by a person, outside any system, and recorded nowhere. If she is away, they are not done and nobody would know.

| What happens to the file | What the system must do | Task |
|---|---|---|
| **Qalqilya exports amounts before VAT** (a till configuration, since the update). Corrected by ×1.16 by hand | **Do not silently apply 1.16.** Detect the pre-VAT basis, report it as a data quality finding, and make the correction a visible, recorded decision. Historical figures have looked consistent only because of the manual fix | M-017, `vat_basis` in M-003 |
| **Jericho and Salfit record a return as a positive row with `RTN` in the notes.** Sign flipped by hand | Return convention per branch; `RTN` parsing; a branch with zero returns is itself a finding | M-011 |
| **The same product, written several ways.** Reconciled from memory into the master workbook | **Build the product catalogue from the branch files, not from the master workbook.** Her sheet now contains spellings that appear in no branch file — it is not a source of truth for products | M-013 |
| A correction log was started and abandoned after a month | Every decision — a match, a resolved date, a VAT correction — is recorded automatically, with who and when. She never maintains it | M-014, M-016 |

## What she asked for

1. **"Tell me which file to open first."** Broken files flagged at upload, before an hour goes on the clean ones.
2. **"Let me fix a name once."** A resolution sticks and replays on every later upload (M-016).
3. **"Do not make me a page of settings."** Ask her a question, take the answer, remember it. Configuration happens through the resolve queue, not a settings screen.
4. **"If I am away, somebody else must be able to run it."** **This is the acceptance test for the handover** (M-027): someone who is not Rania runs a Sunday from the delivery guide alone.

## What she is afraid of

> *"That it works for a month and then one Sunday it gives a number that is wrong and looks right."*

The requirement behind every other requirement. Anything the system cannot resolve arrives **on the screen, named and counted** — never only in a log.

---

## File inventory — what is wrong with each branch's export

As known on 9 November. **Assume there is more**; the readers report what they actually find.

| Branch | Format | What is wrong with it |
|---|---|---|
| **Nablus** | `.xlsx` | Closest to clean. English names, `DD/MM/YYYY`. **The control** |
| **Nablus (Rafidia)** | `.xlsx` | Arabic names, same till as Nablus. Same products, different spelling |
| **Ramallah** | `.xlsx` | **`MM/DD/YYYY` for the first three weeks, then `DD/MM/YYYY`** — the till update changed the export mid-history. **Transaction numbers restarted at 1 and repeat.** Arabic and English mixed in one column. Opens 12:00 on Sundays |
| **Al-Bireh** | `.csv` | UTF-8 **with BOM**. `YYYY-MM-DD` |
| **Hebron** | `.xlsx` | **Arabic-Indic digits in about half the dates.** Arabic headers. Closes 15:00 on Thursdays |
| **Jenin** | `.csv` | **Windows-1256**, not UTF-8 — Arabic-Indic digits in names are lost at source as `?` (D-011). Arabic headers. **A separate discount column** no other branch has. Negative amounts present |
| **Tulkarem** | `.docx` | **Hand-typed Word table.** Till dead since August. No transaction numbers, names from memory, sales almost certainly missing. **Read, marked `unverified_source`, excluded from rankings, readable** (D-003) |
| **Qalqilya** | `.xlsx` | **Amounts pre-VAT** (`AMOUNT_EXVAT`). English headers. Closes 19:00 |
| **Bethlehem** | `.xls` | **A CSV with the wrong extension, semicolon-delimited.** Mixed names. Closed 24–26 December |
| **Jericho** | `.xlsx` | **`RTN` returns.** Dates as text: `5 Oct 2026`. Opens 08:00 |
| **Salfit** | `.xlsx` | **Two-digit years** (`05/10/26`). **Transaction numbers restarted at 1.** `RTN` returns. Opened March, trades 10:00–19:00 |

**Across the set:**

- Rows with **no product name** (~3%): keep, count in the branch total, exclude from the product breakdown, say so (`ROW_MISSING_PRODUCT`, scope `{total}`).
- Rows with **no date or no amount** (<1%): rejected with a reason.
- **Line discounts:** a separate column in Jenin; already deducted everywhere else, and never stated.
- **`week-03/jenin-…-FINAL.csv`:** described as a later, fuller re-export of the same day. It is byte-identical to the first file (D-008).
- Every Excel date seen so far is **stored as text**, not as an Excel date — the format question is never answered by the file itself.
