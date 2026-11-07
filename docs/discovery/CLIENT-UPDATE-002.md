# Client update 002 — the phone view, and a correction to update 001

| | |
|---|---|
| **To** | Suha Qasem — Nakheel Retail |
| **From** | Amani |
| **Date** | 2026-11-08 |
| **Status** | Ready to send |
| **Needs** | A decision on the phone view, and two answers |

---

Suha,

Option 2 noted, and the 20 December date changes how I am reading the whole schedule. Thank you for it — it is more useful than any of the thirteen answers, and I should have asked for it.

Your question first, then something I found while answering it.

## The phone view: a day and a half

Not a week. And not a day either, so here is the exact shape.

**As a ranked list, it is a day and a half.** Eleven branches, each with its total for the date range, the change against the comparison period, and its completeness line underneath. Tap a branch, see its figures. Read-only, as you said.

Two reasons it is cheap. The server work that feeds it is already being built for the main dashboard — the phone screen is presentation only. And a list suits a phone better than a chart does: eleven branch names will not fit on the axis of a 375-pixel-wide chart in either language, let alone in Arabic. **As a mirrored bar chart on a phone it is nearer four days**, almost all of it spent making labels legible. If you want the chart later, say so and I will cost it properly, but I think you would stop using it and use the list.

**Why the original estimate was a week:** I had cut "mobile", not "look at branch totals on a phone". A week was the honest cost of the whole system at phone width — the resolve queue with its per-row buttons, the report tables, upload, settings — in two languages, mirrored. You have just told me you want none of that, and almost the entire estimate goes with it.

That is a useful lesson about my own cut list, and I have written it into the plan: **a cut expressed as a category overstates what it saves.** I will re-read the rest of the list the same way you read this one.

One thing I will not do on the phone screen, and I would rather say it now than be asked later. The completeness note stays in the same block as the number, not behind a tap. A figure that appears on a small screen with its caveat hidden one gesture away is the problem you hired me to prevent, reintroduced by a layout decision. That constraint is part of why it is a day and a half rather than half a day.

---

## Now the part I found while costing it

**The four-week list in my last letter does not fit in four weeks.** I listed what you would have on 5 December without summing the tasks I had already estimated in the same document. When I added them up:

| | Days |
|---|---|
| Foundations and file parsing | 9.5 |
| The data quality engine — report, review queue, returns, duplicates | 10.25 |
| The dashboard pieces I named in that letter | 6.75 |
| **Total** | **26.5** |
| **Four weeks** | **20.0** |

Six and a half days short.

**This is the same mistake as last week, one level down.** Last week I had summed phases instead of tasks. This week I described a delivery instead of summing the tasks inside it. In both cases I wrote a sentence about numbers without re-deriving the numbers, and the sentence was the thing that reached you.

I am telling you three days after the last letter rather than three weeks, and the fix is mechanical rather than a promise to be more careful: **every date I give you from now on arrives with the task list it was summed from.** The dates below are the first ones written that way.

### What this does to your dates

| | Lands | Working days you get before 20 December |
|---|---|---|
| The core system | **Wednesday 9 December** | 7 |
| The core system plus the phone view | **Thursday 10 December** | 6 |

Not the ten working days you were counting on. Seven, or six with the phone view.

**I would still take the phone view.** It costs you one of those days, and under the freeze below the alternative is not mid-December — it is January.

**And a question you will reasonably ask:** why not give you the dashboard on 5 December and finish the rest while you use it? Because the dashboard would then be sitting on an engine that has not finished handling returns and duplicate transaction numbers. Those are the two things that make branch figures wrong in ways that look perfectly reasonable, which is precisely what you must not be holding on 20 December. The numbers go in front of you after the checking works, not before.

I am also not going to close the gap by planning to work six-day weeks. An estimate that only holds if I do not have a bad fortnight is the same kind of number as the ones we are building this system to catch.

---

## Your fortnight is not my build time

This matters more than the five days, and it is the one place I have changed what Option 2 means.

The ten working days between delivery and your review are **yours**. Nothing new gets built in them. Between 10 and 18 December the only changes I make are fixes to problems you or Rania actually hit.

If I spent that fortnight building the remaining features, the system would change under you every few days in exactly the period you are trying to learn whether you can trust it — and your whole reason for choosing Option 2 disappears. You said it yourself: the value is walking into that meeting with numbers you have tested.

So the remaining two weeks run **after** the review. Which means one more decision from you, though not today:

- **Start 21 December**, finishing around the new year, or
- **Start 4 January**, finishing mid-January — and shaped by what the review itself teaches you, not just the fortnight before it.

I lean towards the second. Tell me by 4 December; it does not need an answer now.

The consequence to be clear about: **anything not in the first block arrives after your review, not in mid-December.** When you said you would live without the phone view until mid-December, that option did not actually exist. That is why I am asking you to decide it now.

### What is in the first block, and what moves

I protected branch-level figures and deferred product-level precision, on the grounds that your review is about branches.

**In, for 20 December:** branch totals over any date range · comparison fairness markers · the completeness statement on every figure · any figure traced back to its original rows · the data quality report · the review queue · returns handled per branch · duplicate transaction numbers · your two logins.

**Moved to after the review:**

- **Product codes for the two branches that restarted numbering.** Product figures for those two will carry a stated gap rather than a wrong number. Branch totals are unaffected.
- **The product matching ladder, mostly.** The first block matches exact names and known aliases only. Everything else goes into the review queue rather than being guessed at.

That second one looks like a cut and is closer to the right order. A crude matcher gives you a large review queue, and a large review queue is the system doing what you asked — it never merges what it is unsure about. The alternative is me tuning match thresholds against invented data in November and finding out in December that they were wrong. Instead Rania resolves real rows during your fortnight, and I tune against her actual decisions. **Her fortnight produces the only good test data this project will ever have.**

What I would not move, for completeness: tracing a figure back to its rows, the completeness statements, and the return handling. The first two are why you hired me. The third would make two of your branches look like they were over-selling, at the meeting where branches are judged.

---

## Two things I need

### 1. Your trading calendar

I need to know, per branch, **which days it does not trade, and which day your week starts on.**

What made me ask: your files arrive on Sunday, Rania works on Sunday, your review is on a Sunday — and two of your eleven branches are Ramallah and Tulkarem. I had been about to write a Monday week start and a UAE timezone into the date handling on the strength of "we are in the UAE", and I would rather ask than assume. I have assumed something about this business once already this month and it was the currency.

It matters in three places, all of them invisible when wrong:

- **Every period comparison.** "This week against last week" needs a week boundary. Put it on the wrong day and every weekly comparison is shifted by one day's trading — numbers that look entirely reasonable and are not. This is the figure your review depends on most.
- **Missing files.** A branch with no rows on a day is either closed or has sent a short file. Without the calendar the system cannot tell those apart, and one of them is a gap I should be declaring to you.
- **Late sales.** A sale rung up at 23:30 belongs to the branch's own date. Two hours of timezone error moves it into the next day, and a daily chart shows it in the wrong place.

If different branches keep different days, tell me that too — it is a fairness marker, not a complication.

### 2. The Tulkarem file, now rather than Sunday

Rania's *"not really a file"* is the most informative thing anyone has told me this week. Please have her send me that one file today.

If it is a spreadsheet with a strange shape, it costs me nothing to know early. If it turns out to be a PDF, a scan, or something typed by hand, then reading it is a decision about what we are building rather than a surprise in week two — and I would rather make that decision before I write the specification than after.

---

## On Rania

I would rather you said your own sentence to her yourself, before I meet her.

The words you offered are exactly right, and they land completely differently depending on who says them. From you they are a commitment from her employer. From me, the contractor building the thing that automates her Sunday, "your employer says your job is safe" is approximately what people hear just before being made redundant.

If you tell her first, I get the interview you described. If I have to relay it, I will quote you and say you asked me to.

The rest of your advice I have taken as written, and it changed the interview rather than decorating it. I was going to open by asking what the worst part of her Sunday is. On your warning, that question has moved to the end — and the thing you said matters most, the corrections she makes without mentioning them, is not something I will ask about at all. I will ask "what did you just do there?" every time her hands move while she works through the files. It is a harder question to answer vaguely.

Sunday, live, with the files open: yes, please.

---

## Still owed from me

The hosting figure, this week, as promised — separately from everything above.

---

## What I need back

1. **The phone view in the first block, or after your review?** My recommendation: first block, at the cost of one of your seven days.
2. **The trading calendar.**
3. **The Tulkarem file** — today if Rania can.
4. *(By 4 December, not now)* block two starting 21 December or 4 January.

Amani
