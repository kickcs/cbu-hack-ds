import i18n from "@/shared/lib/i18n"
import { fmt } from "@/shared/lib/format"

import { madLabel, testLabel } from "../model/labels"
import type { BenfordDetail } from "../model/types"
import type { TestCell } from "./test-columns"

/** Level the χ² fit is judged at, matching the backend's reporting. */
const SIGNIFICANCE = 0.05

/** What the matrix squares say, spelled out for someone reading one bank. */
export function verdictLine(cells: TestCell[]): string {
  const fired = cells.filter((cell) => cell.flagged)
  if (fired.length === 0) {
    return i18n.t("common:verdict.clean", { count: cells.length })
  }

  const names = fired.map((cell) => testLabel(cell.test).name).join(", ")
  return i18n.t("common:verdict.fired", {
    count: cells.length,
    fired: fired.length,
    names,
  })
}

export function madReading(detail: BenfordDetail): string {
  const label = (madLabel(detail.mad_label) ?? detail.mad_label).toLowerCase()
  const limit = fmt(detail.threshold, 3)

  if (detail.flagged) {
    return i18n.t("common:verdict.madFlagged", {
      mad: fmt(detail.mad),
      limit,
      label,
    })
  }

  return i18n.t("common:verdict.madClean", {
    mad: fmt(detail.mad),
    limit,
    label,
  })
}

export function chiReading(detail: BenfordDetail): string | null {
  if (detail.chi2_p === null) return null

  return detail.chi2_p < SIGNIFICANCE
    ? i18n.t("common:verdict.chiReject", {
        level: SIGNIFICANCE * 100,
        p: fmt(detail.chi2_p, 4),
      })
    : i18n.t("common:verdict.chiAccept", { p: fmt(detail.chi2_p, 4) })
}
