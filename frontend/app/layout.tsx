import type { ReactNode } from "react";
import { DEFAULT_LOCALE, dirFor } from "../src/locale";

// lang and dir are set here, on the document root, and nowhere else (NN-3).
export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang={DEFAULT_LOCALE} dir={dirFor(DEFAULT_LOCALE)}>
      <body>{children}</body>
    </html>
  );
}
