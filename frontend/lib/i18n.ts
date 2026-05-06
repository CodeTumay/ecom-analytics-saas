"use client";

import { useEffect, useState } from "react";

export type Language = "tr" | "en";

const LANGUAGE_KEY = "language";

export function useLanguage() {
  const [language, setLanguageState] = useState<Language>("tr");

  useEffect(() => {
    const stored = window.localStorage.getItem(LANGUAGE_KEY);
    if (stored === "tr" || stored === "en") {
      setLanguageState(stored);
    }
  }, []);

  function setLanguage(nextLanguage: Language) {
    setLanguageState(nextLanguage);
    window.localStorage.setItem(LANGUAGE_KEY, nextLanguage);
  }

  return { language, setLanguage };
}

export const commonText = {
  tr: {
    language: "Dil",
    turkish: "TR",
    english: "EN"
  },
  en: {
    language: "Language",
    turkish: "TR",
    english: "EN"
  }
} as const;
