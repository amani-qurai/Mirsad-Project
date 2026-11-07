# Bilingual AR/EN and RTL mirroring

Non-negotiables 1–4. The client's acceptance test is *"switching language redraws the charts correctly in both directions"* — so this is checked at delivery, not assumed.

**Contents**
- [Strings](#strings)
- [Numbers, currency, dates](#numbers-currency-dates)
- [Layout](#layout)
- [Direction](#direction)
- [Charts](#charts)
- [Arabic text in the UI](#arabic-text-in-the-ui)
- [Review checklist](#review-checklist)

---

## Strings

Every user-visible string goes through `t()`, with the key in **both** `ar.json` and `en.json` **in the same commit**.

```tsx
// no
<button>Resolve</button>
<span>{count} rows could not be matched</span>

// yes
<button>{t('resolve.action')}</button>
<span>{t('report.unmatched', { count })}</span>
```

**Why the same commit:** a key added to `en.json` alone does not fail visibly in English, so it ships. It fails in Arabic — the locale the client's accountant uses. `scripts/check_locale_parity.py` runs in CI to make this structural rather than a habit.

Rules:

- Keys are namespaced by feature: `report.unmatched`, `resolve.action`, `errors.ROW_DATE_AMBIGUOUS`.
- Never build a sentence by concatenation. Arabic word order differs, so the pieces cannot be reassembled. Use interpolation and let the translation own the whole sentence.
- Pluralisation goes through the i18n library's plural support. Arabic has six plural categories against English's two — `count === 1 ? 'row' : 'rows'` cannot be translated.
- Error messages are keyed by code (see `error-codes.md`), never passed as text from the backend.

---

## Numbers, currency, dates

Everything through `Intl`, with an explicit locale.

```ts
// no
`${value.toFixed(2)} ILS`
value.toLocaleString()
`${d.getDate()}/${d.getMonth() + 1}/${d.getFullYear()}`

// yes
new Intl.NumberFormat(locale, { style: 'currency', currency: 'ILS' }).format(value)
new Intl.NumberFormat(locale).format(value)
new Intl.DateTimeFormat(locale, { dateStyle: 'medium' }).format(d)
```

**Why:** this product is almost entirely numbers, so a formatting error is the first thing the client sees. A bare `toLocaleString()` picks up the *browser's* locale, not the app's — so the UI can be in Arabic while the numbers are formatted for whatever machine happens to be open. That is a bug that passes every test run on a developer laptop.

- Use shared helpers (`formatCurrency`, `formatNumber`, `formatDate`) rather than constructing `Intl` objects at call sites — construction is expensive and the options must stay consistent.
- Currency and decimal places come from configuration, not literals.
- Dates are stored as UTC and formatted at the edge.
- Percentages go through `style: 'percent'`.

**The client is in Palestine and trades in shekels (ILS).** Locales are `ar-PS` and `en-PS`; timezone **Asia/Hebron**; the trading week runs **Saturday to Thursday, Friday closed**.

This line has been wrong twice. It said Saudi riyals (our own unflagged assumption), was corrected to dirhams by the client, and was corrected again to shekels by the client when a question about *branch names* exposed it. **Currency, locale, timezone and week start belong in configuration, never in a literal** — the number of times this value has moved is the argument.

`en-PS` may not exist in a given ICU build and will fall back to `en`. That is fine: currency and digits are set explicitly through the options, not inferred from the region.

**Arabic numerals:** `Intl` may render Arabic-Indic digits for `ar-PS`, which is **not** what the client's accounting uses — her files and reports are in Western digits. Set `numberingSystem: 'latn'` explicitly in the shared helpers rather than relying on the locale default, and never leave it to chance: the digits in a financial figure are the first thing she will notice.

Note the asymmetry with `domain/numbers`, which must *read* Arabic-Indic digits out of the incoming files. We parse both and display one.

---

## Layout

**Logical properties only.** A physical property is a bug that only appears in Arabic, which means it reaches the client before it reaches you.

| Never | Always |
|---|---|
| `margin-left` / `margin-right` | `margin-inline-start` / `margin-inline-end` |
| `padding-left` / `padding-right` | `padding-inline-start` / `padding-inline-end` |
| `left` / `right` | `inset-inline-start` / `inset-inline-end` |
| `text-align: left` | `text-align: start` |
| `border-left` | `border-inline-start` |
| `float: left` | `float: inline-start` |

Also:

- Flex and grid already follow direction — prefer `gap` over directional margins.
- Icons that encode direction (chevrons, back arrows, progress) must flip. Icons that do not (a search glass, a calendar) must not. Flipping everything looks as wrong as flipping nothing.
- Tailwind: use `ms-*`/`me-*`/`ps-*`/`pe-*`, never `ml-*`/`mr-*`/`pl-*`/`pr-*`.
- Shadows and transforms with an x-offset need a direction-aware sign — logical properties do not cover them.

---

## Direction

`dir` and `lang` are set on the document root, from the locale, once.

```tsx
<html lang={locale} dir={locale === 'ar' ? 'rtl' : 'ltr'}>
```

Never set `dir` per component, and never read it from the DOM to branch layout logic. One source of truth; everything else follows from CSS.

---

## Charts

**No charting library mirrors itself.** This is the most underestimated line in the acceptance criteria.

All charts go through the shared `<Chart>` wrapper. Direction-dependent configuration lives there, not in each chart:

- Category axis orientation and inversion
- Value axis side
- Tick and data-label alignment
- Legend placement
- Tooltip side and internal alignment
- Grid padding (room for Arabic labels, which are often longer)

**Why one wrapper:** it is the difference between mirroring being solved once and being re-solved per chart, forgotten on the fourth one, and found by the client. It is also what makes the ADR's fallback from ECharts to Recharts a one-file change.

Every chart task includes screenshots in both directions as its evidence.

---

## Arabic text in the UI

- Arabic needs more line height than Latin; set it per locale rather than globally.
- Font stack must cover both scripts. Arabic glyphs that fall back render visibly badly and look like a bug to the client.
- Arabic strings run 20–30% longer than English. Fixed-width buttons and table columns truncate in Arabic and pass review in English.
- Mixed Arabic/English product names — which this dataset is full of — can render with their parts in a confusing order. Wrap bidirectional content with `dir="auto"` or isolate it with `<bdi>`, or product names such as `طقم أكواب 4pc` will display with the pieces out of order.
- Never use CSS `text-transform` on Arabic. It does nothing, and it signals the code assumed Latin.

---

## Review checklist

Before any PR touching the UI:

- [ ] Every new string goes through `t()`, with keys in **both** `ar.json` and `en.json`
- [ ] `scripts/check_locale_parity.py` passes
- [ ] No sentence built by concatenation
- [ ] Plurals go through the i18n library, not a ternary
- [ ] Every number, currency value and date goes through a shared `Intl` helper
- [ ] No physical CSS properties — grep the diff for `margin-left`, `padding-right`, `text-align: left`, `ml-`, `pr-`
- [ ] Directional icons flip; non-directional ones do not
- [ ] Charts go through `<Chart>`; no direction logic in the chart itself
- [ ] Screens checked in `ar` **and** `en`, with the layout fully mirrored
- [ ] Nothing truncates in Arabic — it is the longer language
