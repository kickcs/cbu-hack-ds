import { fmt } from "@/shared/lib/format"

import { MAD_LABELS, testLabel } from "../model/labels"
import type { BenfordDetail } from "../model/types"
import type { TestCell } from "./test-columns"

/** Level the χ² fit is judged at, matching the backend's reporting. */
const SIGNIFICANCE = 0.05

/** What the matrix squares say, spelled out for someone reading one bank. */
export function verdictLine(cells: TestCell[]): string {
  const fired = cells.filter((cell) => cell.flagged)
  if (fired.length === 0) {
    return `Nothing in this bank's filings tripped a test. All ${cells.length} ran and returned no finding.`
  }

  const names = fired.map((cell) => testLabel(cell.test).name).join(", ")
  return `${fired.length} of ${cells.length} tests returned a finding: ${names}.`
}

export function madReading(detail: BenfordDetail): string {
  const label = (MAD_LABELS[detail.mad_label] ?? detail.mad_label).toLowerCase()
  const limit = fmt(detail.threshold, 3)

  if (detail.flagged) {
    return `A mean absolute deviation of ${fmt(detail.mad)} sits above Nigrini's ${limit} limit, so the first digits read as ${label} — the spread is unlikely to have come from ordinary lending.`
  }

  return `A mean absolute deviation of ${fmt(detail.mad)} stays under Nigrini's ${limit} limit, so the first digits track the law at ${label}.`
}

export function chiReading(detail: BenfordDetail): string | null {
  if (detail.chi2_p === null) return null

  return detail.chi2_p < SIGNIFICANCE
    ? `χ² rejects the fit at the ${SIGNIFICANCE * 100}% level (p = ${fmt(detail.chi2_p, 4)}).`
    : `χ² does not reject the fit (p = ${fmt(detail.chi2_p, 4)}).`
}
