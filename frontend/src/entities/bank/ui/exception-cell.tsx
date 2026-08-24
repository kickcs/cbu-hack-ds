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
  const label = testLabel(cell.test)
  const score = cell.score === null ? "no reading" : fmt(cell.score, 3)
  const caption = `${label.name} — ${cell.flagged ? "flagged" : "no finding"}, ${score}`

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
