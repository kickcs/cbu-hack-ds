import type { ReactNode } from "react"

import { cn } from "@/shared/lib/utils"

/** The ruled caption that opens every block of a filed report. */
export function SectionHead({
  children,
  aside,
  className,
}: {
  children: ReactNode
  /** Count, unit or scope — the note a clerk writes at the right of the rule. */
  aside?: ReactNode
  className?: string
}) {
  return (
    <div
      className={cn(
        "flex items-baseline justify-between gap-4 border-b pb-1.5",
        className
      )}
    >
      <h2 className="eyebrow">{children}</h2>
      {aside && (
        <span className="eyebrow shrink-0 normal-case tabular-nums">
          {aside}
        </span>
      )}
    </div>
  )
}
