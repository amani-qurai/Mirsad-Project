# Rania — interview guide

| | |
|---|---|
| **Who** | Rania, accountant at Nakheel Retail — the only person who will use Mirsad every week |
| **Why now** | The client made this a condition: *"Talk to Rania before you write the specification."* |
| **Blocks** | `docs/SPEC.md` |
| **Length** | 45 minutes, ideally while she has last Sunday's files open |
| **When** | **A Sunday, live, with the files in front of her** — the client has offered this |

---

## What the client told us before this interview

`CLIENT-REPLY-001.md` added three things that change how this conversation is run. They are not notes in the margin; the first one changes what has to happen *before* we meet.

### 1. She is worried about her job — and the reassurance must not come from us

The client's words, which she authorised us to quote:

> *"The point is to stop her spending Sundays fixing exports so that she can do the work I actually need her for, which is the part that requires someone who knows the business."*

**Ask Suha to say that to Rania herself, before the interview.** A contractor relaying "your employer says your job is safe" is third-hand reassurance delivered by the person automating her work — which is approximately what people hear immediately before being made redundant. From Suha it is a commitment. From us it is a rumour.

If it has not happened by the time we meet, quote it as a quote, attribute it clearly, and say we asked her to say it herself. Then move on — dwelling on it makes it louder.

### 2. Her careful answers will be the ones that matter

> *"If you walk in and ask what the worst part of her Sunday is, you may get a careful answer."*

This has a concrete consequence for the running order, not just the tone. **Questions 3 and 5 are the two that invite her to describe her own work as a problem**, and both are now placed *after* the walkthrough rather than inside it. Watching her work is safe — she is demonstrating competence. Being asked what she dreads is not, when she suspects the answer is being collected as justification.

### 3. The silent repairs are the specification

> *"There will be corrections she makes every week that she thinks are too small to be worth describing."*

**Do not rely on question 5 to find these.** It is a yes/no question that offers "no" as an easy, safe answer, and a worried person will take it. They are found by watching: every time her hands move — a retyped cell, a deleted row, a column dragged — stop and ask **"what did you just do there?"** That question is harmless, specific, and nearly impossible to answer vaguely.

Q5 stays as a backstop at the end. The observation is the method.

---

## Why this is not shaped like the client's questions

The thirteen questions sent to Suha came with our defaults attached, because she was approving decisions and a default gives her something to react to.

**Do the opposite here.** Rania is not approving anything — she is the only source of truth about work nobody has ever written down. A default would tell her what we expect and she would agree with it, because that is what people do when a developer describes a plan. These questions are open, and most of the value will come from what she says *after* answering, not from the answer.

Four rules for the conversation:

1. **Do not describe what we are building until the end.** The moment she knows the plan, she starts evaluating it instead of describing her work, and we lose the only chance to hear the problem unprimed.
2. **Ask her to show you, not tell you.** "Can you open last Sunday's files and walk me through it" produces more in ten minutes than an hour of questions. People omit the steps they find obvious, and those are the ones that break. The client put it better than we did: *"What people say they do and what they do are different things, and in her case the difference is the specification."*
3. **Follow the irritation.** Wherever she sighs, laughs, or says "this one is always a problem" — stop and dig. That is the product.
4. **Open with the Tulkarem file.** She has already told Suha one of them is *"not really a file"* — so it is the one thing she has volunteered an opinion about, unprompted. Starting there means starting on ground she chose, where she is the expert and the file is the problem. It is also the known worst case, and we need to see it either way.

---

## Part 1 — The Sunday, as it actually happens (20 min)

Start here and stay longer than feels comfortable.

**1. Walk me through last Sunday from the moment the first file arrives.**
Let her talk. Do not interrupt to clarify; write questions down and come back.

**2. How long does it really take, start to finish?**
Suha said "most of Sunday". Rania's number will differ, and hers is the real one.

**3. Which part do you dread?**
Not "which takes longest" — which one she dislikes. That is the part she will avoid in our tool too, and if the resolve queue lands in that category it will not get used.

> **Not until the walkthrough is finished.** By then she has already shown us the answer, and the question becomes a confirmation rather than an invitation to criticise her own job. If the walkthrough made it obvious, name what we saw and ask if we read it right — easier to agree with than to volunteer.

**4. What do you do when a file is obviously wrong?**
Fix it, send it back, work around it, or ignore it? Does she tell anyone? This reveals a whole loop that is invisible from Suha's side.

**5. Is there anything you fix that nobody ever hears about?**
The most valuable *subject* on this page, and the weakest question for reaching it. Every manual process has silent repairs the owner does not know exist. Each one is either a rule we must implement or a problem we are about to expose for the first time — and exposing it without warning her first would be a bad way for her to meet this system.

> **Demoted to a backstop, asked last.** As written it offers "no" as the safe answer, and the client's warning is that a worried person will take it. The real method is *"what did you just do there?"*, asked during the walkthrough, every time her hands move. Keep this question for the end, to catch what the files did not happen to contain that week.
>
> **And when something turns up here, say what happens next.** If a repair she has been making quietly for three years is about to appear on a report her employer reads, she should hear that from us, in the room, before it appears — along with the fact that the system will show it as *"Rania corrected this"* and not as an error she caused.

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

> The client predicts she also knows *"which manager exports at lunchtime"*. Worth following, because an export taken mid-day is not a full day's trading, and a branch that exports at a different hour from the others is not comparable with them on the same date — a fairness marker we had not thought of. Ask **what time each branch's file usually arrives, and whether anyone ever re-sends a corrected one.** A re-send is `FILE_PERIOD_RESTATED`, and we need to know how often it really happens.

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

## Added after the client's reply

**14. When a branch's file shows nothing for a day, how do you know whether they were shut or the file is short?**

Ask this while the files are open, and ask her to point at an example. The system has to make the same distinction automatically, and it currently cannot: a non-trading day and a truncated export look identical in the data. One is normal and one is a missing figure that must be declared.

Her answer also partly supplies the **trading calendar** we are asking Suha for (`PROJECT-PLAN.md` §4) — but only partly. Rania knows what she observes; Suha knows what is official. Where the two differ, that gap is itself a finding, and the client should hear it.

---

## What to bring back

- The alias sheet or notes from Q8, if they exist
- Her answer to Q12, written in her own words, into `SPEC.md`
- The number from Q13, as the starting review-queue budget
- **Every answer to *"what did you just do there?"*** — the silent-repair list. This is the one the client expects to be most valuable, and it is a list, not an answer
- The Tulkarem file, and what *"not really a file"* turns out to mean
- Her answer to Q14, and where it differs from the official trading calendar
- File arrival times per branch, and how often a corrected file is re-sent

## Three things to watch for

**Her Sunday may not be the one Suha described.** Where their accounts differ, Rania's is what the software has to live with — and the gap itself is worth telling Suha about, carefully.

**She may be wary — and now we know she is.** See the top of this document: the reassurance should come from Suha, before we meet, not from us in the room. What we can do is behave as though her objections matter: say plainly that it is built *for* her to use, that the resolve queue exists because the system is meant to ask her rather than guess, and then **prove it by changing something she objects to and telling her what we changed.** One visible change is worth more than any amount of reassurance.

**Do not promise her the Sundays back.** It is not ours to promise, the client's own framing is about redirecting her work rather than reducing it, and a promise we cannot keep is the fastest way to lose the only weekly user we have. Describe what the system does; let her draw her own conclusion about her Sunday.
