# Rania — interview guide

| | |
|---|---|
| **Who** | Rania, accountant at Nakheel Retail — the only person who will use Mirsad every week |
| **Why now** | The client made this a condition: *"Talk to Rania before you write the specification."* |
| **Blocks** | `docs/SPEC.md` |
| **Length** | 45 minutes, ideally while she has last Sunday's files open |

---

## Why this is not shaped like the client's questions

The thirteen questions sent to Suha came with our defaults attached, because she was approving decisions and a default gives her something to react to.

**Do the opposite here.** Rania is not approving anything — she is the only source of truth about work nobody has ever written down. A default would tell her what we expect and she would agree with it, because that is what people do when a developer describes a plan. These questions are open, and most of the value will come from what she says *after* answering, not from the answer.

Three rules for the conversation:

1. **Do not describe what we are building until the end.** The moment she knows the plan, she starts evaluating it instead of describing her work, and we lose the only chance to hear the problem unprimed.
2. **Ask her to show you, not tell you.** "Can you open last Sunday's files and walk me through it" produces more in ten minutes than an hour of questions. People omit the steps they find obvious, and those are the ones that break.
3. **Follow the irritation.** Wherever she sighs, laughs, or says "this one is always a problem" — stop and dig. That is the product.

---

## Part 1 — The Sunday, as it actually happens (20 min)

Start here and stay longer than feels comfortable.

**1. Walk me through last Sunday from the moment the first file arrives.**
Let her talk. Do not interrupt to clarify; write questions down and come back.

**2. How long does it really take, start to finish?**
Suha said "most of Sunday". Rania's number will differ, and hers is the real one.

**3. Which part do you dread?**
Not "which takes longest" — which one she dislikes. That is the part she will avoid in our tool too, and if the resolve queue lands in that category it will not get used.

**4. What do you do when a file is obviously wrong?**
Fix it, send it back, work around it, or ignore it? Does she tell anyone? This reveals a whole loop that is invisible from Suha's side.

**5. Is there anything you fix that nobody ever hears about?**
The most valuable question on this page. Every manual process has silent repairs the owner does not know exist. Each one is either a rule we must implement or a problem we are about to expose for the first time — and exposing it without warning her first would be a bad way for her to meet this system.

---

## Part 2 — What she knows that we do not (10 min)

She is carrying a mental model built over years. Most of it is not written anywhere.

**6. How do you decide two product names are the same thing?**
Her actual method, not a description of matching. She may use a rule we have not thought of — supplier, price, the branch it came from. If she has one, it belongs in the matching ladder before any fuzzy score.

**7. When you are not sure, what do you do?**
Guess, ask the branch, leave it out, or put it somewhere? This is the resolve queue's real-world predecessor, and its answer tells us what "resolving" should feel like.

**8. Do you keep notes, a mapping sheet, or your own file anywhere?**
Almost certainly yes, and it is gold: a hand-built alias table and a list of known-bad cases. It should seed `product_aliases` on day one rather than being rediscovered by a fuzzy matcher.

**9. Which branches give you the most trouble, and why?**
She will name them instantly. Cross-check against what the files show — where her list and the data disagree, there is something we have misread.

---

## Part 3 — What "done" feels like (10 min)

**10. On a good Sunday, how do you know you have finished?**
There is a moment she considers it done. We need to recreate it, or she will never trust that she is finished and will keep checking in the spreadsheet.

**11. If this took twenty minutes instead of a day, what would you do with the rest of Sunday?**
Lighter in tone, and it surfaces what she actually values about the change — fewer hours, or less anxiety about being blamed for a wrong number. Those lead to different products.

**12. What would make you stop using it and go back to the spreadsheet?**
Ask it directly and let the silence sit. This is the single most useful sentence we can get, because it is the project's real failure condition — and the client named it herself as the thing that would make everything else stop mattering.

---

## Part 4 — Only at the end (5 min)

Now describe what we are building, briefly, and watch her face more than her words.

**13. Here is the part I am least sure about: when the system is not certain two products are the same, it will ask you. How many of those a week would be useful, and how many would be too many?**

Suha asked for the auto-matched-versus-asked count precisely because she fears the queue becomes four hundred items nobody opens. Rania can tell us the number where useful becomes unusable. That number should set the initial confidence threshold — not a value we pick from a paper.

---

## What to bring back

- The alias sheet or notes from Q8, if they exist
- Her answer to Q12, written in her own words, into `SPEC.md`
- The number from Q13, as the starting review-queue budget
- Anything from Q5 that we are about to expose for the first time

## Two things to watch for

**Her Sunday may not be the one Suha described.** Where their accounts differ, Rania's is what the software has to live with — and the gap itself is worth telling Suha about, carefully.

**She may be wary.** Software that automates a task someone has owned for years is not obviously good news, and she has not been asked for her opinion so far. Say plainly at the start that it is being built *for* her to use, that her objections change the design, and that the resolve queue exists because the system is meant to ask her rather than guess. Then prove it by changing something she objects to.
