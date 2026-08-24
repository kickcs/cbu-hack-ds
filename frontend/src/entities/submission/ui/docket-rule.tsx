import { cn } from "@/shared/lib/utils"

import type { FilingStatus } from "../model/types"

type Props = {
  status: FilingStatus
  /** Whether the finished examination turned up anything. Ignored while it is open. */
  flagged?: boolean
  className?: string
}

/**
 * The mark in the margin of a filing — the one place this view spends any ink.
 *
 * A queued filing is ruled in dots, an open one carries the examiner's pen
 * travelling down it, a settled one is ruled solid in the colour of its verdict,
 * and a returned one is a rule that breaks off.
 */
export function DocketRule({ status, flagged = false, className }: Props) {
  return (
    <span
      aria-hidden
      className={cn(
        "w-0.5 shrink-0 self-stretch rounded-full",
        tone(status, flagged),
        className
      )}
    />
  )
}

function tone(status: FilingStatus, flagged: boolean): string {
  switch (status) {
    case "queued":
      return "bg-[repeating-linear-gradient(to_bottom,var(--muted-foreground)_0_2px,transparent_2px_6px)] opacity-60"
    case "processing":
      return "ink-travel bg-border"
    case "failed":
      return "bg-[repeating-linear-gradient(to_bottom,var(--muted-foreground)_0_7px,transparent_7px_13px)]"
    case "done":
      return flagged ? "bg-destructive" : "bg-ok"
  }
}
