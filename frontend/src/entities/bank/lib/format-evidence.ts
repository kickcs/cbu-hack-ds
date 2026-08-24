import { fmtMoney } from "@/shared/lib/format"

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

const COLUMN_HEADS: Record<string, string> = {
  period: "period",
  indicator: "indicator",
  value: "value",
  trailing_zeros: "zeros",
  transition: "months",
  before: "before",
  after: "after",
  growth: "growth",
  limit: "limit",
  margin: "margin",
  digit: "digit",
  observed: "observed",
  expected: "expected",
  deviation: "deviation",
  share: "share",
  count: "count",
  expected_count: "expected",
  total_assets: "assets",
  total_liabilities: "liabilities",
  sum_of_parts: "sum of parts",
  gap: "gap",
  gap_share: "gap %",
}

export function evidenceColumnHead(key: string): string {
  return COLUMN_HEADS[key] ?? key.replace(/_/g, " ")
}

export function fmtEvidenceCell(
  key: string,
  value: string | number | boolean
): string {
  if (typeof value === "boolean") return value ? "yes" : "—"
  if (typeof value === "string") return value
  if (PERCENT_KEYS.has(key)) return `${(value * 100).toFixed(1)}%`
  if (MONEY_KEYS.has(key)) return fmtMoney(value)
  if (Math.abs(value) < 100) return String(value)
  return value.toLocaleString("en-US")
}
