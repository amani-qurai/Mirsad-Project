// Locale and direction, from configuration rather than literals in components.
//
// M-001 renders an empty shell in the default locale. M-002 (next-intl) chooses
// the locale per request; this module stays the one place that maps a locale
// to its direction, so `dir` is still set once, on <html> (NN-3).

export const LOCALES = ["ar", "en"] as const;
export type Locale = (typeof LOCALES)[number];

// Rania works in Arabic, so the system opens in Arabic.
export const DEFAULT_LOCALE: Locale = "ar";

const RTL: ReadonlySet<Locale> = new Set<Locale>(["ar"]);

export function dirFor(locale: Locale): "rtl" | "ltr" {
  return RTL.has(locale) ? "rtl" : "ltr";
}
