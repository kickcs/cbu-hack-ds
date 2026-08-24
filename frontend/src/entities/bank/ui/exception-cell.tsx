import { useTranslation } from "react-i18next"

import { fmt } from "@/shared/lib/format"
import { cn } from "@/shared/lib/utils"

import type { TestCell } from "../lib/test-columns"
import { testLabel } from "../model/labels"

/**
 * One square of the exception matrix. Outline versus solid carries the verdict,
 * so the matrix still reads without colour; the tint inside an outlined cell is
 * how close that test came to firing.
 */
export function ExceptionCell({
  cell,
  delay = 0,
}: {
  cell: TestCell
  delay?: number
}) {
  const { t } = useTranslation("ui")
  const label = testLabel(cell.test)
  const score =
    cell.score === null ? t("exceptionCell.noReading") : fmt(cell.score, 3)
  const outcome = cell.flagged
    ? t("exceptionCell.flagged")
    : t("exceptionCell.noFinding")
  const caption = t("exceptionCell.caption", { name: label.name, outcome, score })

  return (
    <span
      title={caption}
      aria-label={caption}
      role="img"
      className={cn(
        "block size-3.5 rounded-[2px] border",
        cell.flagged
          ? "stamp-in border-destructive bg-destructive"
          : "border-border/80"
      )}
      style={
        cell.flagged
          ? { animationDelay: `${delay}ms` }
          : {
              backgroundColor: `color-mix(in oklab, var(--foreground) ${Math.round(
                cell.intensity * 20
              )}%, transparent)`,
            }
      }
    />
  )
}
