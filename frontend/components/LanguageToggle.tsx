"use client";

import type { Language } from "@/lib/i18n";

export function LanguageToggle({
  language,
  onChange
}: {
  language: Language;
  onChange: (language: Language) => void;
}) {
  return (
    <div className="language-toggle" aria-label="Language">
      <button
        className={language === "tr" ? "active" : ""}
        type="button"
        onClick={() => onChange("tr")}
      >
        TR
      </button>
      <button
        className={language === "en" ? "active" : ""}
        type="button"
        onClick={() => onChange("en")}
      >
        EN
      </button>
    </div>
  );
}
