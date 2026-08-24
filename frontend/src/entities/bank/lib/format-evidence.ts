import i18n from "@/shared/lib/i18n"
import { fmtMoney } from "@/shared/lib/format"

import type { EvidenceBlock } from "../model/types"

// Keys match the evidence-block fields served by /api/banks/{bank}/evidence.
const MONEY_KEYS = new Set([
  "value",
  "total_assets",
  "total_liabilities",
  "sum_of_parts",
  "gap",
  "before",
  "after",
])

const PERCENT_KEYS = new Set([
  "growth",
  "deviation",
  "observed",
  "expected",
  "share",
  "gap_share",
])

export function evidenceColumnHead(key: string): string {
  const head = i18n.t(`common:evidence.cols.${key}`)
  return head === `common:evidence.cols.${key}`
    ? key.replace(/_/g, " ")
    : head
}

export function fmtEvidenceCell(
  key: string,
  value: string | number | boolean
): string {
  if (typeof value === "boolean") return value ? i18n.t("common:evidence.yes") : "—"
  if (typeof value === "string") return value
  if (PERCENT_KEYS.has(key)) return `${(value * 100).toFixed(1)}%`
  if (MONEY_KEYS.has(key)) return fmtMoney(value)
  if (Math.abs(value) < 100) return String(value)
  return value.toLocaleString(i18n.language === "ru" ? "ru-RU" : "en-US")
}

/** Localized block title; the backend's English text is the fallback. */
export function evidenceTitle(block: EvidenceBlock): string {
  return block.title_key
    ? i18n.t(`common:${block.title_key}`, { defaultValue: block.title })
    : block.title
}

/** Localized block summary with the backend's figures interpolated in. */
export function evidenceSummary(block: EvidenceBlock): string {
  return block.summary_key
    ? i18n.t(`common:${block.summary_key}`, {
        ...(block.summary_args ?? {}),
        defaultValue: block.summary,
      })
    : block.summary
}
