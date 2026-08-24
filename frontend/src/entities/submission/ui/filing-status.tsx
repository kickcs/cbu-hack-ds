import { cn } from "@/shared/lib/utils"

import { STATUS_LABELS } from "../model/labels"
import type { FilingStatus } from "../model/types"

/**
 * Where a filing stands, in the rubber type the rest of the report uses.
 * An examined filing says what it found instead of just saying it is done.
 */
export function FilingStatusMark({
  status,
  findings,
  className,
}: {
  status: FilingStatus
  /** Banks flagged, once the examination is over. */
  findings?: number | null
  className?: string
}) {
  if (status === "done") {
    const flagged = findings ?? 0
    return (
      <span
        className={cn(
          "code",
          flagged > 0 ? "text-destructive" : "text-ok",
          className
        )}
      >
        {flagged > 0 ? `${flagged} flagged` : "No findings"}
      </span>
    )
  }

  return (
    <span
      className={cn(
        "code",
        status === "failed" ? "text-destructive" : "text-muted-foreground",
        className
      )}
    >
      {STATUS_LABELS[status]}
      {status === "processing" && <Ellipsis />}
    </span>
  )
}

/** Three dots that fill in one at a time — the only motion in the row's type. */
function Ellipsis() {
  return (
    <span aria-hidden className="ml-0.5 inline-flex">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="animate-pulse"
          style={{ animationDelay: `${i * 200}ms` }}
        >
          .
        </span>
      ))}
    </span>
  )
}
