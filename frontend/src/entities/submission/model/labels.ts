import i18n from "@/shared/lib/i18n"

import type { FilingStatus } from "./types"

/** The word stamped on a filing at each stage, in the clerk's own vocabulary. */
export function statusLabel(status: FilingStatus): string {
  return i18n.t(`common:status.${status}`)
}

/** What the auditor should read into that word. */
export function statusNote(status: FilingStatus): string {
  return i18n.t(`common:statusNote.${status}`)
}

/** Docket number: the id, set as a clerk would write it. */
export function docketNo(id: number): string {
  return id.toString().padStart(3, "0")
}

const DATE_LOCALES: Record<string, string> = {
  en: "en-GB",
  ru: "ru-RU",
  uz: "uz-Latn-UZ",
}

/** When the filing came in, in the reader's own zone — the date stamp on it. */
export function filedAt(iso: string): string {
  const at = new Date(iso)
  if (Number.isNaN(at.valueOf())) return "—"

  const locale = DATE_LOCALES[i18n.language] ?? "en-GB"
  const stamp = new Intl.DateTimeFormat(locale, {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  })
  return stamp.format(at)
}

/** How long the examination took, once both ends of it are known. */
export function tookFor(
  started: string | null,
  finished: string | null
): string | null {
  if (!started || !finished) return null
  const ms = new Date(finished).valueOf() - new Date(started).valueOf()
  if (Number.isNaN(ms) || ms < 0) return null
  return ms < 1_000
    ? i18n.t("common:time.underSecond")
    : `${(ms / 1_000).toFixed(1)}s`
}
