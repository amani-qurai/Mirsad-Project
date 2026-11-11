import { describe, expect, it } from "vitest";
import { DEFAULT_LOCALE, LOCALES, dirFor } from "./locale";

describe("dirFor", () => {
  it("is rtl for Arabic and ltr for English", () => {
    expect(dirFor("ar")).toBe("rtl");
    expect(dirFor("en")).toBe("ltr");
  });

  it("covers every configured locale", () => {
    for (const locale of LOCALES) {
      expect(["rtl", "ltr"]).toContain(dirFor(locale));
    }
  });

  it("opens in a configured locale", () => {
    expect(LOCALES).toContain(DEFAULT_LOCALE);
  });
});
