import i18n from "@/shared/lib/i18n"

/** The Intl locale that matches the active UI language. */
function locale(): string {
  return i18n.language === "ru" ? "ru-RU" : i18n.language === "uz" ? "uz-Latn-UZ" : "en-US"
}

export function fmt(value: number | null | undefined, digits = 4): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—"
  return value.toFixed(digits)
}

export function fmtMoney(value: number): string {
  const abs = Math.abs(value)
  const sign = value < 0 ? "−" : ""
  if (abs >= 1e9) return `${sign}${(abs / 1e9).toFixed(2)}bn`
  if (abs >= 1e6) return `${sign}${(abs / 1e6).toFixed(1)}m`
  return `${sign}${abs.toLocaleString(locale())}`
}

export function fmtCount(value: number): string {
  return value.toLocaleString(locale())
}
