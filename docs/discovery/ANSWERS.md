# Mirsad — the client's answers

**From:** Suha Qasem — Nakheel Retail
**To:** Amani
**Date:** 7 November 2026
**Re:** Discovery questions

---

Amani,

I have never been sent a document like this by someone I was about to pay. Most people send a price and a promise. You sent me the things that could go wrong.

I have answered all thirteen. Where your default is right I say so plainly. Where it is wrong, or where the real answer is messier than yes or no, I have explained.

Rania is preparing six weeks of real files. They will be with you on Sunday.

---

## 1. Is there a product code

**Yes, there is a code column. No, you cannot trust it.**

This is messier than either of your options, so let me be precise.

Most files have a column the till calls `ITEM_NO`. For eight of the eleven branches it is reliable. But **after the till update last year, two branches restarted their numbering from 1**. So code `0412` means a bath mat in Ramallah and a kettle in Tulkarem, and if you look at older files from those same two branches it means something different again.

So: the code is **a hint, not an authority**. Your plan to build name matching anyway is the right one, and I am glad you did not wait for my answer to start thinking about it.

What I would want: use the code when the branch and the date agree with it, use the name otherwise, and **tell me when the two disagree**. A code and a name pointing at different products is exactly the kind of thing I would want to see rather than have resolved quietly.

---

## 2. The confidence threshold

I do not have a number for you. You are the expert and I would rather you chose it.

Your default is right, including that it stays reversible and visible.

**One thing I want on top:** show me, every week, **how many matches were made automatically and how many were asked.** If the queue has four hundred items nobody will open it, and I would rather find that out in week two than discover six months later that Rania has been clicking through it without reading.

That number is how I will know whether the matching is actually working.

---

## 3. The same file uploaded twice

Your default is right, and corrections are real: it happens **about once a month**, usually because a manager exported at lunchtime and sent the full day's file later.

Keep the earlier version viewable and mark that the period was restated. If a number I looked at last week changes, I want to be able to find out why.

---

## 4. Returns and refunds

Good question, and the answer is the kind of mess you should expect from us.

**Most branches record a return as a negative amount.** But two of them — I think the two oldest tills — record it as **a separate positive row with `RTN` written into the notes column**. Same money, opposite sign, recorded as a sale.

So if you only look for negatives, those two branches will look like they are selling more than they are. Which is the opposite of the problem I described, and just as bad.

**And yes, when I say sales I mean net.** Your default is right. Show gross and returns beside it.

---

## 5. What a row needs

Here I think your default is slightly too strict, and it matters.

**A row with a date, a branch and an amount but no product name is still useful to me.** It belongs in that branch's total. Most of my decisions are at the branch level, and losing those rows would make branch totals quietly wrong, which is the failure you are trying to prevent.

**What I would want:** keep it, count it in the branch total, exclude it from the product breakdown, and **say so** — "this branch's total includes 34 rows with no product, worth 2,100." Then I know the total is right and the product view is incomplete.

Date, branch or amount missing: reject, as you said, with the reason.

---

## 6. Ambiguous dates

Your default is right, and the risk you flagged at the end of it is a real one, not a theoretical one.

**The export settings did change.** That is what the till update last year did to us. So a branch's date format is not permanent, and remembering it forever would be wrong exactly once, silently, in the middle of the history.

Re-checking on every upload, as you wrote, is what I would want. And when a branch's format appears to change, **ask again rather than assume the old answer still holds.**

---

## 7. Compared with last month

You have put your finger on the thing that nearly made me close a branch.

I am not going to tell you whether it is calendar months or equal days, because I do not think in those terms. Here is what I actually need:

**When I look at a branch and see a drop, I need to know whether that branch is doing worse, or whether the comparison is unfair.** A shorter month, three closed days, a holiday — if any of that is behind the number, say so **on the chart**, not underneath it.

Your default does that. Keep it.

---

## 8. Who resolves, and can it be undone

**Rania, and only Rania.** Not the branch managers — eleven people shaping my product list is how we got here.

Yes, reversible, and yes, I want to see who decided what and when. Not because I distrust Rania. Because when a number looks wrong in three months I want to be able to find out what happened without asking anybody to remember.

Your three roles are right.

---

## 9. Are the branches fixed

Mostly, with two things you should build for.

**We opened a branch eight months ago.** It has no comparison for most of last year. If the dashboard shows it as a catastrophic decline against a period when it did not exist, that is precisely the broken comparison I am trying to escape.

**And one branch may close next year.** Not decided, but possible.

Your rule about never auto-creating a twelfth branch is exactly right, and your reasoning for it is the thing I would not have thought of.

---

## 10. File formats and size

**A mix.** Most branches send Excel. Three send CSV. One sends CSV with a `.xls` extension, which I am told is a separate problem.

Size: **a few thousand rows per branch per week.** Comfortably inside your fifty thousand.

---

## 11. Currency, tax and discounts

**Dirhams, not riyals.** We are in the UAE. Worth correcting before any number gets formatted.

Amounts are **after VAT**, with one exception you will find: **one branch exports pre-VAT.** It is the branch that got a different till configuration during the update.

You predicted this one almost exactly: two branches with identical sales that do not agree. Raise it as a data quality finding, as you said. **Do not adjust it silently** — if you corrected it quietly I would never know my own data was inconsistent, and I would want to fix it at the source.

Line discounts: shown separately in some exports, already deducted in others. Treat that as another thing to tell me about rather than solve.

---

## 12. The data quality report

Your default is right. In the system, downloadable, no email.

---

## 13. Where it runs, and who logs in

Office machine is fine to start, but I should tell you something now rather than in week four.

**I travel, and I check numbers from my phone.** If Mirsad only works inside the shop network, I will go back to asking Rania to send me a spreadsheet, and we will be exactly where we started.

I am not asking you to host it in the first version. I am asking you to **make sure that putting it online later does not mean rebuilding it**, and to tell me roughly what hosting it would cost per month so I can decide.

Accounts: me, Rania, and the read-only one for showing people.

---

## Your assumptions

All correct, with one adjustment.

**Weekly reporting is how the files arrive, but it is not how I look at them.** I want to choose any date range — a quarter, a season, since we opened the new branch. Do not build the dashboard so that "a week" is baked into it.

---

## Two things you did not ask, and should have

You asked thirteen careful questions about my data and not one about what I do with it. That is the gap in this document.

**First: what decisions do I actually make?**

Mirsad exists because of a decision — I nearly closed a branch. I decide what to stock more of, which branch needs attention, when to run a promotion, and occasionally whether a branch is worth keeping. Those decisions are monthly and quarterly, not weekly.

That should shape what the dashboard puts in front of me. Right now you know everything about how my data is broken and nothing about what I am trying to see.

**Second: what does a good Sunday look like for Rania?**

She currently loses most of Sunday to this. Nobody has asked her how long it takes, what the worst part is, or what "done" would feel like.

**Talk to Rania before you write the specification.** She is the one who will use this every week, and if she goes back to the spreadsheet because the review queue is tedious, everything else you have planned stops mattering.

---

## What you will have

| | |
|---|---|
| Six weeks of real files, including the bad ones | Sunday |
| Rania's time for a conversation | Whenever you ask |
| These answers | Now |

I am not going to be polite about the files, as you requested. Some of them are genuinely embarrassing.

Suha
