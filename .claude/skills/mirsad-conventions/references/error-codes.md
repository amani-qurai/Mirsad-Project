# Error codes and reason codes

Non-negotiable 6: **the server returns error codes, never prose.** Every code has a translation in `ar.json` and `en.json`, added in the same commit as the code itself.

**Contents**
- [Naming](#naming)
- [Severity: the three outcomes](#severity-the-three-outcomes)
- [The catalogue](#the-catalogue)
- [Adding a code](#adding-a-code)
- [How codes reach the client](#how-codes-reach-the-client)

---

## Naming

```
<SUBJECT>_<PROBLEM>
```

`SUBJECT` is one of `FILE`, `ROW`, `TXN`, `BRANCH`, `PRODUCT`, `DATE`, `AMOUNT`, `AUTH`, `JOB`.

```
FILE_ENCODING_UNDETECTED
ROW_MISSING_AMOUNT
TXN_DUPLICATE_IN_BRANCH
PRODUCT_MATCH_BELOW_THRESHOLD
```

Subject-first because the data quality report groups by subject. The owner reads "11 file problems, 340 row problems, 14 product questions" — a code set that does not group that way makes that sentence impossible to produce.

---

## Severity: the three outcomes

Every code carries exactly one severity. This is the honesty requirement made mechanical.

| Severity | Row is | In the dashboard | Human needed |
|---|---|---|---|
| `warning` | usable | included, flagged | no |
| `held` | not yet trustworthy | **excluded, and counted out loud** | **yes** |
| `rejected` | unusable | excluded, listed with reason | no |

`held` is the severity the project exists for. It is the difference between *"we could not match these fourteen rows"* and a chart that silently averaged them away.

### Severity is one axis. Scope is the other.

Severity says what happened to a row. **Scope says which figures may use it.** A row is not simply valid or invalid — it is valid for some analyses and not others:

| Scope | Requires |
|---|---|
| `total` | date, branch, amount |
| `product` | the above, plus a resolved product |
| `quantity` | the above, plus a parseable quantity |

A row with no product name is `warning` with scope `{total}`: it belongs in its branch's total and not in the product breakdown.

Every aggregate therefore carries a completeness statement beside the number — *"this branch's total includes 34 rows with no product, worth ILS 2,100."* Traceability says where a figure came from; completeness says what is missing from it, and the second is the question that nearly cost the client a branch.

The full model, the new codes below, and the client's own wording are in `docs/discovery/IMPACT.md`.

**Choosing a severity — the test:** can a person resolve this in the UI and make the row usable?

- Yes → `held`
- No, and the row is still meaningful without it → `warning`
- No, and the row means nothing without it → `rejected`

Guessing instead of holding is the one failure this system was commissioned to prevent.

---

## The catalogue

Initial set. The authoritative list is the enum in `backend/app/errors/`; this table is the design intent behind it, and is finalised in `docs/SPEC.md`.

### File level

| Code | Severity | Meaning |
|---|---|---|
| `FILE_EXACT_DUPLICATE` | `rejected` | Byte-identical to a file already ingested |
| `FILE_PERIOD_RESTATED` | `warning` | Same branch and period, different content — supersedes the earlier version, which stays viewable |
| `FILE_ENCODING_UNDETECTED` | `rejected` | Text encoding could not be determined with confidence |
| `FILE_HEADERS_UNRECOGNISED` | `held` | Columns could not be mapped — a human maps them once, and the mapping is remembered for that branch |
| `FILE_EMPTY` | `rejected` | No data rows |
| `FILE_FORMAT_UNSUPPORTED` | `rejected` | Not CSV or Excel |

### Row level

| Code | Severity | Meaning |
|---|---|---|
| `ROW_MISSING_DATE` | `rejected` | No date — cannot be placed in time |
| `ROW_MISSING_BRANCH` | `rejected` | No branch — cannot be attributed |
| `ROW_MISSING_PRODUCT` | `warning`, scope `{total}` | No product. **Counted in the branch total, excluded from the product breakdown**, and declared. Rejecting it would under-report branch totals invisibly — see `docs/discovery/IMPACT.md` §2.2 |
| `ROW_MISSING_AMOUNT` | `rejected` | No amount — nothing to report |
| `ROW_MISSING_QUANTITY` | `warning` | Amount present; quantity null and flagged |
| `ROW_AMOUNT_UNPARSEABLE` | `rejected` | Amount present but not a number after `domain/numbers` |
| `ROW_AMOUNT_NEGATIVE` | `warning` | Treated as a return — see `docs/SPEC.md` |
| `ROW_DATE_UNPARSEABLE` | `rejected` | Not a date in any recognised format |
| `ROW_DATE_OUT_OF_RANGE` | `held` | Parses, but falls outside the plausible trading period |

### Dates

| Code | Severity | Meaning |
|---|---|---|
| `DATE_FORMAT_AMBIGUOUS` | `held` | Day/month order undecidable, e.g. `03/04/2025`. **Never guessed** (AC-6) |
| `DATE_FORMAT_INFERRED` | `warning` | Inferred from unambiguous dates elsewhere in the same file; the inference is recorded |

### Transactions

| Code | Severity | Meaning |
|---|---|---|
| `TXN_DUPLICATE_WITHIN_FILE` | `rejected` | Same transaction id twice in one file |
| `TXN_DUPLICATE_IN_BRANCH` | `held` | Id already seen for this branch — the till update made ids non-unique, so this needs a human |
| `TXN_ID_MISSING` | `warning` | No id; row kept, identified by its content |

### Branches

| Code | Severity | Meaning |
|---|---|---|
| `BRANCH_UNRECOGNISED` | `held` | Name matches no known branch or alias. **Never auto-created** — an invented twelfth branch would split one branch's sales in two and look exactly like a sales collapse |
| `BRANCH_CLOSED_IN_PERIOD` | `warning` | Data for a period the branch was recorded closed |

### Products

| Code | Severity | Meaning |
|---|---|---|
| `PRODUCT_MATCH_BELOW_THRESHOLD` | `held` | Fuzzy score between the review floor and the auto threshold — a human is asked (NN-8) |
| `PRODUCT_MATCH_AUTO` | `warning` | Matched automatically above the threshold; score recorded, reversible |
| `PRODUCT_NEW` | `warning` | Below the review floor — recorded as a new canonical product, not forced into the nearest one |
| `PRODUCT_NAME_CONFLICT` | `held` | Product code and product name disagree with a known pairing |

### Jobs and auth

| Code | Severity | Meaning |
|---|---|---|
| `JOB_FAILED` | `rejected` | Ingestion failed; partial results are discarded, not half-committed |
| `AUTH_INVALID_CREDENTIALS` | — | |
| `AUTH_INSUFFICIENT_ROLE` | — | e.g. a guest attempting to resolve |

---

## Adding a code

1. Add it to the enum in `backend/app/errors/`.
2. Add its message to **both** `ar.json` and `en.json`, in the same commit. CI fails otherwise, by design.
3. Give it a severity, using the test above.
4. Make sure it reaches the data quality report with a count **and** the rows behind it. A code that cannot be traced back to rows breaks non-negotiable 7 and acceptance criterion 5.
5. Write the test for the condition that raises it.

---

## How codes reach the client

```python
raise MirsadError(
    ErrorCode.ROW_DATE_AMBIGUOUS,
    context={"row": 412, "value": "03/04/2025", "candidates": ["2025-04-03", "2025-03-04"]},
)
```

```json
{
  "error": {
    "code": "ROW_DATE_AMBIGUOUS",
    "context": { "row": 412, "value": "03/04/2025", "candidates": ["2025-04-03", "2025-03-04"] }
  }
}
```

- `context` carries structured values only. **Never a pre-built sentence** — a sentence assembled in the API cannot be translated, and prose from the backend cannot be shown to an Arabic-speaking accountant.
- The frontend renders `t('errors.ROW_DATE_AMBIGUOUS', context)`, with numbers and dates formatted through `Intl`.
- `context` must carry enough for a human to act. `ROW_DATE_AMBIGUOUS` without the candidate dates leaves the resolve queue with nothing to offer, which turns a resolvable `held` row into a dead end.
