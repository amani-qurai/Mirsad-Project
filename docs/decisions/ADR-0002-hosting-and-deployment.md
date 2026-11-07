# ADR-0002 — Hosting and deployment

| | |
|---|---|
| **Status** | **Accepted** 9 November 2026 — hosting approved by the client |
| **Date** | 2026-11-08 |
| **Supersedes** | Nothing. `ADR-0001` §"Deferred" left hosting open deliberately |
| **Task** | M-028 — *"confirm hosting pricing against live figures before anything is quoted"* |
| **Client question** | *"What would putting it online cost per month?"* (answer 12) |

---

## 1. Why this document exists

In `CLIENT-UPDATE-001.md` we told the client we would not quote a figure we had not checked, and that it was *"tens of dirhams a month rather than hundreds."*

**The second half of that sentence was itself an unchecked number.** It is right for the configurations that are too small and wrong for the one we would actually stand behind. The corrected answer is below, with every figure's source.

This is the third estimate in this project to need correcting, and the pattern is identical each time: a plausible order of magnitude, stated confidently, never re-derived. The point of writing the arithmetic down is that it stops being possible to do that.

## 2. What is being priced

The baseline matters, because it is not zero-versus-something — **it is zero.**

`docker compose up` on a machine in the office costs nothing, and that is a real option. Hosting buys three things:

1. **Access from anywhere.** This is the one that matters now: she has just asked for a read-only branch-totals screen on her phone (`PROJECT-PLAN.md` §7.2), and *a phone screen served from a PC in the office is not reachable from a hotel.* **Her phone request and her hosting question are the same question**, and she may not have noticed. If she wants the phone view, hosting stops being optional.
2. **Independence from one machine being switched on.** The weekly cycle is Rania's, and it should not depend on whose PC is running.
3. **Backups held somewhere other than the office.**

## 3. Sizing, from the client's own numbers

She told us: *"a few thousand rows per branch per week"* (answer 10), eleven branches.

| | |
|---|---|
| Transactions per year | 3,000 × 11 × 52 ≈ **1.7 M** |
| Rows stored per year | ≈ **3.4 M** — NN-7 keeps the raw row alongside the transaction |
| Database growth | **≈ 3.4 GB/year** at ~1 KB/row with JSONB and trigram indexes |
| Original files retained | 11 × ~2 MB × 52 ≈ **1.1 GB/year** |
| Concurrent users | **3** — Suha, Rania, one guest. Not a load problem |
| Peak | Sunday: eleven files parsed, matched and persisted in one job |

**This is a small-data problem with a bursty weekly job.** It is not CPU-bound or traffic-bound, which is why the cheapest tiers are even candidates. The binding constraint is memory during ingestion, plus enough disk for several years of retained raw rows.

**2 GB is not enough** for Postgres, the API and the web server together while an ingestion job is parsing Excel. **4 GB / 2 vCPU** is the honest size. The Next.js build runs in CI, not on the server.

## 4. Figures

All prices read from the vendors' own pricing pages on **2026-11-08**.

> **Currency corrected 9 November.** This document was written in **AED**. The client is in **Palestine** and trades in **shekels (ILS)** — she corrected herself after our question about branch names. Figures below are now ILS, converted at **1 USD = 3.17** (early November 2026).
>
> **Unlike the dirham, the shekel floats.** The dirham was pegged, so a converted figure stayed true. This one will not. **The dollar figures are the contract; the shekel figures are a snapshot.** At rates between 3.00 and 3.40 the monthly cost runs **ILS 86–98** and the annual **ILS 1,037–1,175**. The client should budget the top of that band.

### DigitalOcean — the priced option

Chosen as the basis because its own pricing page gave complete, unambiguous figures. Not because it is cheapest.

| | Monthly | ILS/mo | ILS/yr |
|---|---|---|---|
| A — 2 GB / 1 vCPU, Postgres on the box, weekly backups | $14.40 | **46** | 548 |
| B — 2 GB / 2 vCPU, Postgres on the box, weekly backups | $21.60 | **68** | 822 |
| **C — 4 GB / 2 vCPU, Postgres on the box, weekly backups** | **$28.80** | **91** | **1,096** |
| D — 2 GB droplet + managed Postgres (1 GB) | $29.55 | 94 | 1,124 |
| E — 4 GB droplet + managed Postgres (1 GB) | $43.95 | 139 | 1,672 |

Components: Basic Droplet 4 GiB / 2 vCPU / 80 GiB / 4 TB transfer = **$24.00**; backups at **20 % weekly** or 30 % daily; cheapest managed PostgreSQL (1 GiB RAM, 1 vCPU, 10–30 GiB) = **$15.15**.

### Why not managed Postgres, despite it sounding safer

Because of what is actually irreplaceable here, which is a smaller thing than the database.

| Data | If the server is lost |
|---|---|
| Raw files, transactions, aggregates | **Reproducible.** She has the original files and the pipeline is deterministic — that is what the golden-file tests guarantee |
| **Rania's resolutions and the alias table** | **Gone.** Nobody can re-derive a human decision. It means asking her to redo weeks of work |

The irreplaceable part is *small* — tens of thousands of rows. It does not need a managed database; it needs **a nightly dump taken off the machine**, which is a cron job and a few hundred compressed megabytes. Paying ILS 48/month for managed Postgres to protect data that a nightly `pg_dump` protects for nothing is buying the wrong thing.

What a weekly droplet snapshot alone would cost her: **up to seven days of Rania's decisions.** That is the risk to close, and it is cheap to close.

### Recommendation

**Option C, plus a nightly database dump pulled off the server.**

| | ILS/mo |
|---|---|
| 4 GB / 2 vCPU droplet, Postgres in the same compose stack | 76 |
| Weekly droplet backups (20 %) | 15 |
| Nightly dump → the office machine | 0 |
| **Total** | **≈ 91** · ILS 1,096/yr |
| *If she would rather the dump went to object storage than a PC* | *+16* |

TLS is free (Let's Encrypt). A domain is a separate, small annual cost — **not quoted here, because we have not checked it**, and `.ps` differs from `.com`. It is single-digit shekels a month either way, and it will be confirmed before it is stated.

## 5. Options considered and not recommended

| Option | Why not |
|---|---|
| **Hetzner** | Would roughly halve the bill. Their own page shows shared-vCPU from **€6.49/mo excl. VAT** and currently marks the cheaper line *"Currently not available"*, and third-party reports of 2026 price rises and plan retirements conflict with each other. **We could not confirm a current plan, price and stock from Hetzner's own page, so it is not the basis of the quote.** Worth revisiting at deployment — it is real money |
| **Oracle Cloud Always Free** | Could be free, and has regional datacenters. But the free Arm quota was reportedly halved in June 2026, free capacity is frequently unavailable in a given region, and free instances can be reclaimed. *"Free but may be withdrawn"* is the wrong trade for the system her branch decisions depend on |
| **Fly.io** | Clear official pricing (shared-cpu-2x/2 GB at $13.39/mo, volumes $0.15/GB/mo) but managed Postgres starts at **$38/mo**, and no Middle East region is listed. Worse fit at higher cost |
| **AWS / Azure regionally** | Several times the above for this workload. Residency turned out not to be a requirement (§6), so this is moot |
| **Vercel + a hosted database** | Splits one Docker Compose stack across two platforms and two bills to host a three-user internal tool. Adds operational surface, not value |

## 6. Region, latency and residency

**No provider in the priced list has a Gulf datacenter.** DigitalOcean's nearest is **Bangalore**, then Frankfurt and London.

- **Latency is not a concern.** A weekly-use dashboard with three users does not notice 50 ms or 130 ms. Saying otherwise would be inventing a problem to justify a more expensive region.
- **Residency: asked, and answered.** The client confirmed on 9 November that she knows of no rule — a family business, and the till exports carry no customer personal data. The question was worth asking rather than assuming, and it cost one line. Note that the same letter corrected the country itself, which is why assuming would have been doubly wrong.

## 7. What this figure does not include

The completeness rule, applied to a price. The number above is ILS 91/month **and**:

- **No domain** — small, annual, and not yet checked.
- **Nothing during development.** Hosting starts when we deploy, not now.
- **No email sending.** Emailing the weekly report was never in scope.
- **Not a backup of her own files.** The system keeps what it is given; it is not her archive.
- **Not our time.** Deployment is M-027/M-028 work inside the agreed days; ongoing maintenance after delivery is not priced in this project at all, and she should hear that separately rather than discover it.
- **One moving input:** the **3.17** exchange rate, from several secondary sources agreeing on early November 2026. **The shekel floats**, so this figure drifts in a way the dirham one would not have. **The vendor bills in USD** — the dollar figures are the contract and the shekel figures are derived, which keeps the drift visible rather than hidden inside a number she is asked to approve.

## 8. Decision required

| Who | What |
|---|---|
| ~~Suha~~ | ✅ **Hosted — approved 9 November**, at roughly this figure |
| ~~Suha~~ | ✅ **No residency requirement** |
| **Amani** | Re-check Hetzner at deployment, and the domain price before quoting it |
| **Amani** | Promote this ADR to **Accepted** once she chooses, and record the choice |
