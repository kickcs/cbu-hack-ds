import i18n from "i18next"
import { initReactI18next } from "react-i18next"

import { resources } from "./resources"

export const SUPPORTED_LANGUAGES = ["en", "ru", "uz"] as const
export type Language = (typeof SUPPORTED_LANGUAGES)[number]

const STORAGE_KEY = "regtech-language"

function isLanguage(value: string | null): value is Language {
  return value === "en" || value === "ru" || value === "uz"
}

function initialLanguage(): Language {
  const stored = localStorage.getItem(STORAGE_KEY)
  return isLanguage(stored) ? stored : "en"
}

/** The language that carries the report strings when the rest is localized. */
export const APP_LANGUAGE: Language = "en"

i18n.use(initReactI18next).init({
  resources,
  lng: initialLanguage(),
  fallbackLng: APP_LANGUAGE,
  ns: ["app", "common", "ui"],
  defaultNS: "app",
  interpolation: { escapeValue: false },
})

i18n.on("languageChanged", (language) => {
  document.documentElement.lang = language
})

export function setLanguage(language: Language) {
  localStorage.setItem(STORAGE_KEY, language)
  void i18n.changeLanguage(language)
}

export default i18n
