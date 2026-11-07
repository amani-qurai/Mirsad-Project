# Client update 003 — the calendar, Tulkarem, and a finding about Ramallah

| | |
|---|---|
| **To** | Suha Qasem — Nakheel Retail |
| **From** | Amani |
| **Date** | 2026-11-09 |
| **Status** | Ready to send |
| **Needs** | One decision, and two things I am missing |

---

Suha,

The currency is corrected everywhere — shekels, Palestine, `Asia/Hebron`, week starting Saturday. Everything below is in shekels.

Before the rest: your trading calendar produced something about **Ramallah** that I think matters more than anything else in this letter, and I have put it at the end so it is the last thing you read rather than the first thing you skim.

## What I take from the currency

You said *"ask me twice about anything I answered quickly."* I am going to do something slightly different, because I think asking twice would have failed.

If I had asked you about the currency again, you would have confirmed dirhams. You were not uncertain — you were confidently wrong, which is a different thing and much harder to catch. What caught it was a question about **branch names**, from a completely different direction.

So the rule I am adopting is not *ask twice*. It is **cross-check from an unrelated angle**: for anything you answer quickly, find a second question that would give an inconsistent answer if the first were wrong.

It is also, I notice, exactly what the software does. It never asks the same scorer twice about a product; it checks the product *code* against the product *name* and raises a conflict when they disagree. Your branch names were the code. "We are in the UAE" was the name. They disagreed, and that is the only reason we are having this conversation in November rather than in February.

**You did not make a careless mistake. My questions were not triangulated.** That is a method problem, and it is fixed.

## Hosting, in shekels

**ILS 91 a month. ILS 1,096 a year.**

| | ILS/month |
|---|---|
| The server — 4 GB memory, 2 processors, 80 GB disk | 76 |
| Weekly server backups | 15 |
| Nightly copy of the database to a machine in your office | 0 |
| **Total** | **91** |

**One caveat you should budget for.** The dirham was pegged to the dollar, so a converted figure stayed true. **The shekel floats.** The provider bills in dollars — $28.80 a month — and the shekel figure moves with the rate, which was about 3.17 when I checked this week.

At rates between 3.00 and 3.40 you are looking at **ILS 86–98 a month, ILS 1,037–1,175 a year.** Budget the top of that and you will not be surprised.

I would rather show you the band than give you one number that quietly stops being true in March.

## The trading calendar — and the thing I now have to build

Your answer was more complete than I expected, and it added real work. Honestly:

| | Days |
|---|---|
| Branch trading schedules — Friday closed everywhere, Ramallah's Sunday morning, Hebron's early Thursday | 0.75 |
| **Closure periods you can add afterwards, with every comparison recalculating** | 1.25 |
| Holiday calendar | 0.25 |
| Timezone and branch-local day boundaries | 0.25 |
| Extending the fairness markers to cover part-days and closures | 0.5 |
| Shekels, Palestinian locale, digits | 0.25 |
| Tulkarem handling (below) | 0.5 |
| **Total** | **3.75** |

**The Jenin requirement is not negotiable and I am not treating it as an extra.** You said an unflagged eleven-day closure *"looks like a collapse in any monthly comparison, and it is precisely the shape of mistake that nearly cost me a branch."* That is the sentence the whole project is built around, so it goes in the first block, and you will be able to add a closure in February and have October's comparisons redraw themselves.

## Tulkarem — I am not going to try to read that file

Rania's *"not really a file"* turned out to mean a dead till and three months of a manager typing into Word.

**My recommendation: we do not ingest it before your review.** Three reasons, and the first is yours:

1. You said it: *"I would rather its numbers were missing and labelled than present and wrong, especially for a branch at a review where branches are judged."*
2. **The format is dying anyway.** The till is replaced in January — February, as you read it. Building a reader for three months of one manager's typing, during the tightest four weeks of the project, is work we throw away.
3. Ingesting it produces exactly the dangerous kind of number: plausible, unverifiable, and sitting in a ranking on the day you decide branch futures.

**What you will see instead.** Tulkarem appears, clearly marked *"hand-recorded, not verified, excluded from comparison."* Its months are out of every ranking and every comparison. The files are kept and you can read them. The indicative total is on that branch's own page and nowhere else — so it cannot quietly end up in a figure you act on.

You will know Tulkarem is a gap. You will not be shown a number pretending it is not.

In January, once the new till is in, we decide properly. My guess is the answer is Rania entering the gap through the review queue rather than any file reader at all.

## The schedule — and a change to how it is delivered

The calendar work pushes the first block from 10 to **15 December**. With Friday closed, that leaves you **three working days** before the review, not seven.

Three is too few, so I want to split the delivery rather than shrink it:

| | When | For | What |
|---|---|---|---|
| **First** | **Saturday 5 December** | **Rania** | Upload, cleaning, the data quality report, the review queue |
| **Second** | **Tuesday 15 December** | **You** | The dashboard, comparisons, completeness, traceability |
| Freeze | 15–18 Dec | — | Defects only, nothing new |
| **Review** | **Sunday 20 December** | You | — |

**Why this is better than one delivery on the 15th.** You still get three days on the dashboard — but the numbers underneath it will have had ten days of Rania working through the queue. You would not be looking at raw output; you would be looking at figures someone has already been through. And her real decisions become the data I tune the matching against in January, which is worth more than anything I could invent.

Block two from 4 January, as you said.

## The one decision I need

**Does the phone view stay in the first block, or move to January?**

You approved it when it cost one of seven testing days. The calendar work changed that trade: **it now costs two of your three.**

I am not going to treat your earlier yes as covering a different arithmetic. **My recommendation is to move it to January** — you will be at your desk for the review, not in a hotel, so its value is after the 20th rather than before it. Three testing days instead of one is worth more to you that week.

Tell me which, and I will build to it.

## And the finding — Ramallah

This is the part I would not have reached without your calendar.

**Ramallah closes Sunday mornings. Every week. For years.** Which means it trades roughly half a day less than every other branch, every single week — somewhere around 8% less selling time, permanently.

So: **in every quarterly comparison you have ever made, Ramallah has been judged against branches that were open longer than it was.** Not because of a broken file. Because nobody subtracted the hours.

I do not know yet whether that is large enough to have changed a decision. But it is the same class of problem as the branch you nearly closed, except this one has been quietly running for years rather than appearing in one bad week — and it will not show up as an anomaly, because it is perfectly consistent.

The system will mark it from day one: Ramallah's raw total will never be presented as comparable to another branch's without saying so.

**To measure it properly I need normal opening hours per branch** — what time each shop opens and closes on a normal day. You gave me the exceptions, which was the harder half, but I cannot calculate "half a day less" without knowing how long a day is.

## What I need back

1. **The phone view — first block or January?** My recommendation: January.
2. **Normal opening and closing hours per branch**, so Ramallah and Hebron can be measured rather than described.
3. **The Eid and public holiday list**, whenever it suits.

Rania on Thursday and Sunday, noted. Thank you for doing it yourself.

Amani
